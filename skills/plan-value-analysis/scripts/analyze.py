#!/usr/bin/env python3
"""Deterministic, source-gated subscription plan valuation. No network or prices built in."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_FLOOR, getcontext
from pathlib import Path

getcontext().prec = 40

BUCKETS = ("input", "output", "cache_read", "cache_write")
MODEL_ID = re.compile(r"^[a-z0-9][a-z0-9._-]*/[a-z0-9][a-z0-9._-]*@[a-z0-9][a-z0-9._-]*#[a-z0-9][a-z0-9._-]*$")
EVIDENCE_STATUSES = {"verified", "synthetic", "estimated", "undisclosed", "conflicting", "unavailable"}
ZERO = Decimal(0)
MILLION = Decimal(1_000_000)


class InputError(ValueError):
    pass


def obj(value, where):
    if not isinstance(value, dict):
        raise InputError(f"{where} must be an object")
    return value


def array(value, where):
    if not isinstance(value, list):
        raise InputError(f"{where} must be an array")
    return value


def string(value, where):
    if not isinstance(value, str) or not value.strip():
        raise InputError(f"{where} must be a nonempty string")
    return value


def integer(value, where, minimum=0):
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise InputError(f"{where} must be an integer >= {minimum}")
    return value


def number(value, where, minimum=ZERO, nullable=False):
    if value is None and nullable:
        return None
    if isinstance(value, bool) or not isinstance(value, (str, int, float, Decimal)):
        raise InputError(f"{where} must be a decimal number" + (" or null" if nullable else ""))
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise InputError(f"{where} must be a decimal number") from exc
    if not result.is_finite() or result < minimum:
        raise InputError(f"{where} must be finite and >= {minimum}")
    return result


def model_id(value, where):
    string(value, where)
    if not MODEL_ID.fullmatch(value) or any(x in value for x in ("@latest#", "#auto", "#default")):
        raise InputError(f"{where} needs exact vendor/model@version#mode, not a mutable alias")
    return value


def bucket_numbers(value, where, integer_values=False, nullable=False):
    value = obj(value, where)
    if set(value) != set(BUCKETS):
        raise InputError(f"{where} must have exactly {', '.join(BUCKETS)}; cache tokens are separate from input")
    parse = integer if integer_values else number
    return {key: (parse(value[key], f"{where}.{key}") if not (nullable and value[key] is None)
                  else None) for key in BUCKETS}


def evidence_issue(evidence, data_kind, where):
    if not isinstance(evidence, dict):
        return f"{where}:missing_evidence"
    status = evidence.get("status")
    if status not in EVIDENCE_STATUSES:
        return f"{where}:invalid_evidence_status"
    if data_kind == "synthetic" and status == "synthetic":
        return None
    if status != "verified":
        return f"{where}:evidence_{status}"
    valid_date = False
    try:
        valid_date = date.fromisoformat(evidence.get("fetched_at", "")).isoformat() == evidence.get("fetched_at")
    except (TypeError, ValueError):
        pass
    if not (isinstance(evidence.get("url"), str) and evidence["url"].startswith(("https://", "http://"))
            and valid_date and isinstance(evidence.get("excerpt"), str) and evidence["excerpt"].strip()):
        return f"{where}:incomplete_verified_evidence"
    return None


def add_issue(issues, issue):
    if issue and issue not in issues:
        issues.append(issue)


def fx_convert(amount, currency, rates):
    if amount is None or currency not in rates:
        return None
    return amount / rates[currency]


def api_call_cost(workload, api_price, rates):
    if not api_price or api_price.get("model_id") != workload["model_id"]:
        return None, "api_price_model_mismatch"
    if api_price.get("batch") is not workload["batch"]:
        return None, "api_price_batch_mismatch"
    context = workload["context_tokens"]
    lower = integer(api_price.get("context_min", 0), "api_price.context_min")
    upper = api_price.get("context_max")
    if upper is not None:
        upper = integer(upper, "api_price.context_max", 1)
        if upper <= lower:
            raise InputError("api_price.context_max must exceed context_min")
    if context < lower or (upper is not None and context >= upper):
        return None, "api_price_context_mismatch"
    prices = bucket_numbers(api_price.get("per_million"), "api_price.per_million", nullable=True)
    if any(workload["per_request"][key] and prices[key] is None for key in BUCKETS):
        return None, "api_price_missing_token_rate"
    native = sum((Decimal(workload["per_request"][key]) * (prices[key] or ZERO) / MILLION
                  for key in BUCKETS), ZERO)
    converted = fx_convert(native, api_price["currency"], rates)
    return (converted, None) if converted is not None else (None, "api_price_fx_missing")


def quota_amount(quota, unit):
    if unit == "token_buckets":
        if quota.get("amounts") is None:
            return None
        return bucket_numbers(quota["amounts"], "pool.quota.amounts", integer_values=True)
    return number(quota.get("amount"), "pool.quota.amount", nullable=True)


def windows_for(pool, workload, period_days):
    window = obj(pool.get("window"), "pool.window")
    kind = window.get("kind")
    if kind == "monthly":
        return 1, None
    active = workload.get("active_windows_per_month", {})
    if not isinstance(active, dict) or pool["id"] not in active:
        return None, "active_windows_missing"
    count = integer(active[pool["id"]], f"workload.active_windows_per_month.{pool['id']}")
    if kind == "weekly":
        # Calendar-week resets can touch partial weeks at both ends of the period.
        maximum = (period_days + 12) // 7
    elif kind == "rolling_hours":
        hours = integer(window.get("hours"), "pool.window.hours", 1)
        maximum = (period_days * 24 + hours - 1) // hours + 1
    else:
        raise InputError("pool.window.kind must be monthly, weekly, or rolling_hours")
    if count > maximum:
        raise InputError(f"active windows for {pool['id']} exceed theoretical {period_days}-day maximum")
    return count, None


def debit_per_request(rule, pool, workload, call_usd, rates):
    basis = rule.get("basis")
    allowed = {"requests": {"request"}, "credits": {"request", "weighted_tokens"},
               "weighted_tokens": {"weighted_tokens"}, "currency": {"api_value"},
               "token_buckets": {"token_buckets"}}
    if basis not in allowed[pool["unit"]]:
        raise InputError(f"pool unit {pool['unit']} cannot use debit basis {basis}")
    multiplier = number(rule.get("multiplier", "1"), "rule.multiplier")
    if multiplier == ZERO:
        return None, "zero_debit_unbounded"
    if basis == "token_buckets":
        return None, None
    if basis == "request":
        debit = number(rule.get("units_per_request"), "rule.units_per_request") * multiplier
    elif basis == "weighted_tokens":
        weights = bucket_numbers(rule.get("per_million"), "rule.per_million")
        debit = sum((Decimal(workload["per_request"][key]) * weights[key] / MILLION
                     for key in BUCKETS), ZERO) * multiplier
    elif basis == "api_value":
        currency = string(pool["quota"].get("currency"), "pool.quota.currency")
        if currency not in rates:
            return None, "pool_currency_fx_missing"
        debit = call_usd * rates[currency] * multiplier
    else:
        raise InputError("rule.basis must be request, weighted_tokens, api_value, or token_buckets")
    if debit == ZERO:
        return None, "zero_debit_unbounded"
    return debit, None


def evaluate_pool(pool, rule, workload, api_price, call_usd, rates, data_kind, period_days):
    issues = []
    quota = obj(pool.get("quota"), "pool.quota")
    add_issue(issues, evidence_issue(quota.get("evidence"), data_kind, "quota"))
    add_issue(issues, evidence_issue(rule.get("evidence"), data_kind, "model_rule"))
    klass = pool.get("entitlement_class")
    if klass not in ("guaranteed", "conditional", "promotional"):
        raise InputError("pool.entitlement_class must be guaranteed, conditional, or promotional")
    if klass != "guaranteed":
        add_issue(issues, "non_guaranteed_entitlement")
    unit = pool.get("unit")
    if unit not in ("requests", "credits", "weighted_tokens", "currency", "token_buckets"):
        raise InputError("pool.unit is invalid")
    if unit == "currency":
        string(quota.get("currency"), "pool.quota.currency")
    amount = quota_amount(quota, unit)
    if amount is None:
        add_issue(issues, "quota_unknown")
    windows, window_issue = windows_for(pool, workload, period_days)
    add_issue(issues, window_issue)
    if issues:
        return {"pool_id": pool["id"], "status": "unranked", "reasons": issues,
                "entitlement_value_per_window_usd": None, "reachable_requests": None,
                "reachable_value_usd": None, "active_windows_per_month": windows}
    if unit == "token_buckets":
        if rule.get("basis") != "token_buckets":
            raise InputError("token_buckets pool requires token_buckets debit basis")
        multiplier = number(rule.get("multiplier", "1"), "rule.multiplier")
        if multiplier == ZERO:
            issues.append("zero_debit_unbounded")
            return {"pool_id": pool["id"], "status": "unranked", "reasons": issues,
                    "entitlement_value_per_window_usd": None, "reachable_requests": None,
                    "reachable_value_usd": None, "active_windows_per_month": windows}
        prices = bucket_numbers(api_price["per_million"], "api_price.per_million", nullable=True)
        if any(amount[key] and prices[key] is None for key in BUCKETS):
            issues.append("api_price_missing_token_rate")
            return {"pool_id": pool["id"], "status": "unranked", "reasons": issues,
                    "entitlement_value_per_window_usd": None, "reachable_requests": None,
                    "reachable_value_usd": None, "active_windows_per_month": windows}
        native = sum((Decimal(amount[key]) / multiplier * (prices[key] or ZERO) / MILLION
                      for key in BUCKETS), ZERO)
        entitlement = fx_convert(native, api_price["currency"], rates)
        if entitlement is None:
            issues.append("api_price_fx_missing")
            return {"pool_id": pool["id"], "status": "unranked", "reasons": issues,
                    "entitlement_value_per_window_usd": None, "reachable_requests": None,
                    "reachable_value_usd": None, "active_windows_per_month": windows}
        ratios = [Decimal(amount[key]) / (Decimal(workload["per_request"][key]) * multiplier)
                  for key in BUCKETS if workload["per_request"][key] > 0]
        if not ratios:
            issues.append("zero_usage_per_request")
            return {"pool_id": pool["id"], "status": "unranked", "reasons": issues,
                    "entitlement_value_per_window_usd": entitlement, "reachable_requests": None,
                    "reachable_value_usd": None, "active_windows_per_month": windows}
        per_window_requests = int(min(ratios).to_integral_value(rounding=ROUND_FLOOR))
    else:
        debit, debit_issue = debit_per_request(rule, pool, workload, call_usd, rates)
        if debit_issue:
            issues.append(debit_issue)
            return {"pool_id": pool["id"], "status": "unranked", "reasons": issues,
                    "entitlement_value_per_window_usd": None, "reachable_requests": None,
                    "reachable_value_usd": None, "active_windows_per_month": windows}
        per_window_requests = int((amount / debit).to_integral_value(rounding=ROUND_FLOOR))
        entitlement = Decimal(per_window_requests) * call_usd
    reachable_requests = per_window_requests * windows
    additional_caps = pool.get("additional_caps", [])
    for cap in array(additional_caps, f"pool.{pool['id']}.additional_caps"):
        cap = obj(cap, f"pool.{pool['id']}.additional_cap")
        cap_id = string(cap.get("id"), "additional_cap.id")
        cap_key = f"{pool['id']}:{cap_id}"
        add_issue(issues, evidence_issue(cap.get("evidence"), data_kind, f"additional_cap:{cap_id}"))
        extra_amount = number(cap.get("amount"), f"additional_cap.{cap_id}.amount", nullable=True)
        if extra_amount is None:
            add_issue(issues, f"additional_cap:{cap_id}:unknown")
        extra_windows, extra_issue = windows_for({"id": cap_key, "window": cap.get("window")},
                                                 workload, period_days)
        add_issue(issues, f"additional_cap:{cap_id}:{extra_issue}" if extra_issue else None)
        if unit == "token_buckets":
            add_issue(issues, "token_bucket_additional_cap_unsupported")
        elif extra_amount is not None and extra_windows is not None:
            extra_requests_per_window = int((extra_amount / debit).to_integral_value(rounding=ROUND_FLOOR))
            reachable_requests = min(reachable_requests, extra_requests_per_window * extra_windows)
    if pool.get("daily_cap_requests") is not None:
        daily_cap = integer(pool["daily_cap_requests"], "pool.daily_cap_requests")
        days = workload.get("active_days_per_month")
        if days is None:
            issues.append("active_days_missing_for_daily_cap")
        else:
            days = integer(days, "workload.active_days_per_month")
            if days > period_days:
                raise InputError("workload.active_days_per_month exceeds period_days")
            reachable_requests = min(reachable_requests, daily_cap * days)
    return {"pool_id": pool["id"], "status": "valued" if not issues else "unranked",
            "reasons": issues, "entitlement_value_per_window_usd": entitlement,
            "capacity_requests_per_window": per_window_requests,
            "reachable_requests": reachable_requests if not issues else None,
            "reachable_value_usd": Decimal(reachable_requests) * call_usd if not issues else None,
            "active_windows_per_month": windows, "window_kind": pool["window"]["kind"],
            "window_hours": pool["window"].get("hours"),
            "entitlement_class": klass,
            "unit": unit}


def monthly_cost(price, rates, data_kind):
    issues = []
    add_issue(issues, evidence_issue(price.get("evidence"), data_kind, "plan_price"))
    currency = string(price.get("currency"), "plan.price.currency")
    months = integer(price.get("months"), "plan.price.months", 1)
    tax_rate = number(price.get("tax_rate"), "plan.price.tax_rate", nullable=True)
    tax_included = price.get("tax_included")
    if tax_included is not None and not isinstance(tax_included, bool):
        raise InputError("plan.price.tax_included must be boolean or null")
    if tax_included is None or (tax_included is False and tax_rate is None):
        add_issue(issues, "tax_terms_unknown")
        factor = None
    else:
        factor = Decimal(1) if tax_included else Decimal(1) + tax_rate
    cost = {"currency": currency, "months_per_bill": months, "tax_rate": tax_rate,
            "tax_included": tax_included}
    for label in ("initial", "renewal"):
        amount = number(price.get(label), f"plan.price.{label}", nullable=True)
        native = amount * factor / Decimal(months) if amount is not None and factor is not None else None
        usd = fx_convert(native, currency, rates)
        cost[f"{label}_monthly_original"] = native
        cost[f"{label}_monthly_usd"] = usd
        if amount is None:
            add_issue(issues, f"{label}_cost_unknown")
        elif usd is None and factor is not None:
            add_issue(issues, "plan_price_fx_missing")
    return cost, issues


def ratio(numerator, denominator):
    return numerator / denominator if numerator is not None and denominator not in (None, ZERO) else None


def evaluate_plan_workload(plan, workload, api_prices, rates, data_kind, period_days, fx_issue):
    matching = []
    for pool in plan["pools"]:
        for rule in pool["rules"]:
            if rule["model_id"] == workload["model_id"]:
                matching.append((pool, rule))
    if not matching:
        return None
    issues = []
    price = api_prices.get(workload["api_price_id"])
    needs_fx = (plan["price"].get("currency") != "USD"
                or (price is not None and price.get("currency") != "USD")
                or any(pool["unit"] == "currency" and pool["quota"].get("currency") != "USD"
                       for pool, _ in matching))
    if needs_fx:
        add_issue(issues, fx_issue)
    access_contexts = workload.get("access_by_plan")
    access_context = access_contexts.get(plan["id"]) if isinstance(access_contexts, dict) else None
    plan_access = plan.get("access")
    if data_kind == "live" or access_context is not None:
        if not isinstance(plan_access, dict) or access_context is None:
            add_issue(issues, "access_eligibility_unknown")
        else:
            add_issue(issues, evidence_issue(plan_access.get("evidence"), data_kind, "plan_access"))
            kind = access_context.get("kind")
            if kind == "api":
                if plan_access.get("api_access") is not True:
                    add_issue(issues, "api_access_not_verified_allowed")
            elif kind == "client":
                if access_context.get("name") not in plan_access.get("clients", []):
                    add_issue(issues, "client_access_not_verified_allowed")
            else:
                raise InputError("workload.access_by_plan kind must be client or api")
    if data_kind == "live":
        if not isinstance(plan.get("limits"), dict):
            add_issue(issues, "limits_evidence_missing")
        else:
            add_issue(issues, evidence_issue(plan["limits"].get("evidence"), data_kind, "plan_limits"))
    if price is None:
        add_issue(issues, "api_price_missing")
        call_usd = None
    else:
        add_issue(issues, evidence_issue(price.get("evidence"), data_kind, "api_price"))
        call_usd, price_issue = api_call_cost(workload, price, rates)
        add_issue(issues, price_issue)
    cost, cost_issues = monthly_cost(plan["price"], rates, data_kind)
    for issue in cost_issues:
        add_issue(issues, issue)
    if workload["basis"] == "measured":
        add_issue(issues, evidence_issue(workload.get("evidence"), data_kind, "measured_usage"))
    pools = []
    excluded_pools = []
    if call_usd is not None and price is not None:
        for pool, rule in matching:
            result = evaluate_pool(pool, rule, workload, price, call_usd, rates, data_kind, period_days)
            if "non_guaranteed_entitlement" in result["reasons"]:
                excluded_pools.append(result)
            else:
                pools.append(result)
                for issue in result["reasons"]:
                    add_issue(issues, f"pool:{pool['id']}:{issue}")
    else:
        pools = [{"pool_id": pool["id"], "status": "unranked", "reasons": ["api_price_unusable"]}
                 for pool, _ in matching]
    if not pools:
        add_issue(issues, "no_guaranteed_eligible_pool")
    reachable_requests = None
    reachable_value = None
    realized_requests = None
    realized_value = None
    entitlement_per_window = None
    if not issues:
        reachable_requests = sum(pool["reachable_requests"] for pool in pools)
        reachable_value = Decimal(reachable_requests) * call_usd
        # Entitlements from distinct pools are additive for one model; a shared pool's other models are alternatives.
        window_counts = {(pool["window_kind"], pool["window_hours"], pool["active_windows_per_month"])
                         for pool in pools}
        # Different windows have incompatible per-window units; keep diagnostics in each pool.
        entitlement_per_window = (sum((pool["entitlement_value_per_window_usd"] for pool in pools), ZERO)
                                  if len(window_counts) == 1 else None)
        realized_requests = min(reachable_requests, workload["requests_per_month"])
        realized_value = Decimal(realized_requests) * call_usd
    result = {"plan_id": plan["id"], "provider": plan["provider"], "product": plan["product"],
              "tier": plan["tier"], "region": plan["region"], "billing_regime": plan["billing_regime"],
              "model_id": workload["model_id"], "api_price_id": workload["api_price_id"],
              "workload_id": workload["id"], "workload_basis": workload["basis"],
              "access_context": access_context,
              "status": "valued" if not issues else "unranked", "reasons": issues,
              "api_value_per_request_usd": call_usd, "entitlement_value_per_window_usd": entitlement_per_window,
              "reachable_requests": reachable_requests, "reachable_value_usd": reachable_value,
              "realized_requests": realized_requests, "realized_value_usd": realized_value,
              "effective_utilization": ratio(realized_value, reachable_value),
              "monthly_cost": cost, "pools": pools, "excluded_pools": excluded_pools,
              "valuation_scope": "guaranteed_lower_bound" if excluded_pools else "all_eligible_pools",
              "access": plan.get("access"), "limits": plan.get("limits"),
              "shared_pool_alternatives": {pool["id"]: [rule["model_id"] for rule in pool["rules"]]
                                           for pool, _ in matching if len(pool["rules"]) > 1}}
    nonmonthly = any(pool["window"]["kind"] != "monthly" or
                     any(cap["window"]["kind"] != "monthly" for cap in pool.get("additional_caps", []))
                     for pool, _ in matching)
    operational_limits = data_kind == "live"
    if isinstance(plan.get("limits"), dict):
        operational_limits = operational_limits or any(
            plan["limits"].get(key) is not None for key in ("rate_limit", "concurrency", "fair_use"))
    result["evidence_grade"] = ("insufficient" if issues else
                                "synthetic_scenario" if data_kind == "synthetic" else
                                "verified_measured_mix" if workload["basis"] == "measured" else
                                "verified_scenario_mix")
    result["limitations"] = (["unmodeled_operational_limits"] if operational_limits else [])
    result["reachable_bound_kind"] = ("unvalued" if issues else
                                      "active_window_capacity_upper_bound" if nonmonthly else
                                      "operational_capacity_upper_bound" if operational_limits else
                                      "monthly_workload_capacity")
    result["realized_bound_kind"] = ("unvalued" if issues else
                                     "demand_capped_upper_bound" if nonmonthly or operational_limits
                                     or workload["basis"] == "scenario"
                                     else "measured_count_under_monthly_cap")
    result["value_bounds_usd"] = {
        "reachable_lower": ZERO if reachable_value is not None and (nonmonthly or operational_limits)
                           else reachable_value,
        "reachable_upper": reachable_value,
        "realized_lower": ZERO if realized_value is not None and result["realized_bound_kind"] == "demand_capped_upper_bound"
                          else realized_value,
        "realized_upper": realized_value,
    }
    cny_rate = rates.get("CNY")
    if cny_rate is not None and fx_issue is None:
        for name in ("api_value_per_request", "entitlement_value_per_window", "reachable_value", "realized_value"):
            usd_value = result[f"{name}_usd"]
            result[f"{name}_cny"] = usd_value * cny_rate if usd_value is not None else None
        for period in ("initial", "renewal"):
            usd_cost = cost[f"{period}_monthly_usd"]
            cost[f"{period}_monthly_cny"] = usd_cost * cny_rate if usd_cost is not None else None
    for period in ("initial", "renewal"):
        usd_cost = cost[f"{period}_monthly_usd"]
        result[f"reachable_roi_{period}"] = ratio(reachable_value, usd_cost)
        result[f"realized_roi_{period}"] = ratio(realized_value, usd_cost)
        result[f"break_even_utilization_{period}"] = ratio(usd_cost, reachable_value)
        if usd_cost == ZERO and result["status"] == "valued":
            add_issue(result["reasons"], f"zero_{period}_cost_roi_undefined")
    return result


def index_items(items, key, where):
    result = {}
    for index, item in enumerate(array(items, where)):
        item = obj(item, f"{where}[{index}]")
        ident = string(item.get(key), f"{where}[{index}].{key}")
        if ident in result:
            raise InputError(f"duplicate {where} {key}: {ident}")
        result[ident] = item
    return result


def validate(data):
    obj(data, "input")
    if data.get("schema_version") != 1:
        raise InputError("schema_version must be 1")
    data_kind = data.get("data_kind", "live")
    if data_kind not in ("live", "synthetic"):
        raise InputError("data_kind must be live or synthetic")
    days = integer(data.get("period_days", 30), "period_days", 1)
    fx = obj(data.get("fx"), "fx")
    try:
        if date.fromisoformat(fx.get("as_of", "")).isoformat() != fx.get("as_of"):
            raise ValueError
    except (TypeError, ValueError) as exc:
        raise InputError("fx.as_of must be a real YYYY-MM-DD date") from exc
    raw_rates = obj(fx.get("per_usd"), "fx.per_usd")
    rates = {currency: number(rate, f"fx.per_usd.{currency}", Decimal("0.0000000000000000001"))
             for currency, rate in raw_rates.items()}
    if rates.get("USD") != Decimal(1):
        raise InputError("fx.per_usd.USD must be 1")
    fx_issue = evidence_issue(fx.get("evidence"), data_kind, "fx")
    api_prices = index_items(data.get("api_prices"), "id", "api_prices")
    for ident, price in api_prices.items():
        model_id(price.get("model_id"), f"api_prices.{ident}.model_id")
        string(price.get("currency"), f"api_prices.{ident}.currency")
        bucket_numbers(price.get("per_million"), f"api_prices.{ident}.per_million", nullable=True)
        if not isinstance(price.get("batch"), bool):
            raise InputError(f"api_prices.{ident}.batch must be boolean")
    workloads = index_items(data.get("workloads"), "id", "workloads")
    for ident, workload in workloads.items():
        model_id(workload.get("model_id"), f"workloads.{ident}.model_id")
        string(workload.get("api_price_id"), f"workloads.{ident}.api_price_id")
        integer(workload.get("requests_per_month"), f"workloads.{ident}.requests_per_month")
        workload["per_request"] = bucket_numbers(workload.get("per_request"),
                                                  f"workloads.{ident}.per_request", integer_values=True)
        integer(workload.get("context_tokens"), f"workloads.{ident}.context_tokens")
        if not isinstance(workload.get("batch"), bool):
            raise InputError(f"workloads.{ident}.batch must be boolean")
        if workload.get("basis") not in ("scenario", "measured"):
            raise InputError(f"workloads.{ident}.basis must be scenario or measured")
        if workload["basis"] == "scenario":
            string(workload.get("label"), f"workloads.{ident}.label")
        if workload.get("access_by_plan") is not None:
            contexts = obj(workload["access_by_plan"], f"workloads.{ident}.access_by_plan")
            for plan_id, context in contexts.items():
                string(plan_id, f"workloads.{ident}.access_by_plan key")
                context = obj(context, f"workloads.{ident}.access_by_plan.{plan_id}")
                if context.get("kind") not in ("api", "client"):
                    raise InputError(f"workloads.{ident}.access_by_plan.{plan_id}.kind must be api or client")
                if context["kind"] == "client":
                    string(context.get("name"), f"workloads.{ident}.access_by_plan.{plan_id}.name")
    plans = index_items(data.get("plans"), "id", "plans")
    pool_ids = set()
    for ident, plan in plans.items():
        for key in ("provider", "product", "tier", "region", "billing_regime"):
            string(plan.get(key), f"plans.{ident}.{key}")
        obj(plan.get("price"), f"plans.{ident}.price")
        if plan.get("access") is not None:
            access = obj(plan["access"], f"plans.{ident}.access")
            if "clients" in access:
                for client in array(access["clients"], f"plans.{ident}.access.clients"):
                    string(client, f"plans.{ident}.access.clients[]")
            if access.get("api_access") is not None and not isinstance(access["api_access"], bool):
                raise InputError(f"plans.{ident}.access.api_access must be boolean or null")
            if access.get("notes") is not None:
                string(access["notes"], f"plans.{ident}.access.notes")
        if plan.get("limits") is not None:
            limits = obj(plan["limits"], f"plans.{ident}.limits")
            for key in ("rate_limit", "fair_use", "overage"):
                if limits.get(key) is not None:
                    string(limits[key], f"plans.{ident}.limits.{key}")
            if limits.get("concurrency") is not None:
                integer(limits["concurrency"], f"plans.{ident}.limits.concurrency")
        pools = array(plan.get("pools"), f"plans.{ident}.pools")
        if not pools:
            raise InputError(f"plans.{ident}.pools must not be empty")
        for pool in pools:
            obj(pool, f"plans.{ident}.pool")
            pool_id = string(pool.get("id"), "pool.id")
            if pool.get("entitlement_class") not in ("guaranteed", "conditional", "promotional"):
                raise InputError(f"pool.{pool_id}.entitlement_class is required and must be guaranteed, conditional, or promotional")
            if pool.get("unit") not in ("requests", "credits", "weighted_tokens", "currency", "token_buckets"):
                raise InputError(f"pool.{pool_id}.unit is invalid")
            if pool["unit"] == "currency":
                string(obj(pool.get("quota"), f"pool.{pool_id}.quota").get("currency"),
                       f"pool.{pool_id}.quota.currency")
            if pool_id in pool_ids:
                raise InputError(f"pool.id must be globally unique: {pool_id}")
            pool_ids.add(pool_id)
            cap_ids = set()
            for cap in array(pool.get("additional_caps", []), f"pool.{pool_id}.additional_caps"):
                cap = obj(cap, f"pool.{pool_id}.additional_cap")
                cap_id = string(cap.get("id"), f"pool.{pool_id}.additional_cap.id")
                if cap_id in cap_ids:
                    raise InputError(f"duplicate additional cap in pool {pool_id}: {cap_id}")
                cap_ids.add(cap_id)
            rules = array(pool.get("rules"), f"pool.{pool_id}.rules")
            if not rules:
                raise InputError(f"pool.{pool_id}.rules must not be empty")
            model_rules = set()
            for rule in rules:
                obj(rule, f"pool.{pool_id}.rule")
                mid = model_id(rule.get("model_id"), f"pool.{pool_id}.rule.model_id")
                if mid in model_rules:
                    raise InputError(f"duplicate model rule in pool {pool_id}: {mid}")
                model_rules.add(mid)
        prior = plan.get("upgrade_from")
        if prior is not None:
            string(prior, f"plans.{ident}.upgrade_from")
            if prior == ident or prior not in plans:
                raise InputError(f"plans.{ident}.upgrade_from must refer to another plan")
            old = plans[prior]
            if any(plan[key] != old.get(key) for key in ("provider", "product", "region", "billing_regime")):
                raise InputError(f"plans.{ident}.upgrade_from needs same provider/product/region/billing_regime")
    return data_kind, days, rates, fx_issue, api_prices, workloads, plans


def ranking_row(row, metric):
    return {"plan_id": row["plan_id"], "tier": row["tier"], "model_id": row["model_id"],
            "workload_id": row["workload_id"], "api_price_id": row["api_price_id"],
            "monthly_value_usd": row["reachable_value_usd"] if metric == "reachable_roi_renewal"
                                 else row["realized_value_usd"], "renewal_monthly_cost_usd":
            row["monthly_cost"]["renewal_monthly_usd"], "roi": row[metric],
            "workload_basis": row["workload_basis"], "evidence_grade": row["evidence_grade"],
            "value_bound_kind": row["reachable_bound_kind"] if metric == "reachable_roi_renewal"
                                else row["realized_bound_kind"],
            "access_context": row["access_context"],
            "shared_pool_alternatives": row["shared_pool_alternatives"]}


def rankings(evaluations):
    same = {}
    for row in evaluations:
        if row["reachable_roi_renewal"] is not None:
            key = (row["model_id"], row["api_price_id"], row["workload_id"])
            same.setdefault(key, []).append(row)
    same_groups = []
    for key, rows in sorted(same.items()):
        if len(rows) < 2:
            continue
        rows.sort(key=lambda row: (-row["reachable_roi_renewal"], row["plan_id"]))
        same_groups.append({"model_id": key[0], "api_price_id": key[1], "workload_id": key[2],
                            "rows": [ranking_row(row, "reachable_roi_renewal") for row in rows]})
    own = sorted((row for row in evaluations if row["reachable_roi_renewal"] is not None),
                 key=lambda row: (-row["reachable_roi_renewal"], row["plan_id"], row["model_id"]))
    realized = sorted((row for row in evaluations if row["realized_roi_renewal"] is not None),
                      key=lambda row: (-row["realized_roi_renewal"], row["plan_id"], row["model_id"]))
    return {"same_model": same_groups,
            "own_api_value": [ranking_row(row, "reachable_roi_renewal") for row in own],
            "realized": [ranking_row(row, "realized_roi_renewal") for row in realized]}


def upgrades(plans, evaluations):
    lookup = {(row["plan_id"], row["model_id"], row["api_price_id"], row["workload_id"]): row
              for row in evaluations}
    output = []
    for plan in plans.values():
        prior = plan.get("upgrade_from")
        if prior is None:
            continue
        for row in evaluations:
            if row["plan_id"] != plan["id"]:
                continue
            old = lookup.get((prior, row["model_id"], row["api_price_id"], row["workload_id"]))
            if old is None:
                output.append({"from_plan_id": prior, "to_plan_id": plan["id"],
                               "model_id": row["model_id"], "workload_id": row["workload_id"],
                               "status": "unranked", "reason": "baseline_model_or_workload_missing"})
                continue
            if old["status"] != "valued" or row["status"] != "valued":
                output.append({"from_plan_id": prior, "to_plan_id": plan["id"],
                               "model_id": row["model_id"], "workload_id": row["workload_id"],
                               "status": "unranked", "reason": "baseline_or_upgrade_unvalued"})
                continue
            delta_cost = row["monthly_cost"]["renewal_monthly_usd"] - old["monthly_cost"]["renewal_monthly_usd"]
            delta_initial_cost = row["monthly_cost"]["initial_monthly_usd"] - old["monthly_cost"]["initial_monthly_usd"]
            delta_reachable = row["reachable_value_usd"] - old["reachable_value_usd"]
            delta_realized = row["realized_value_usd"] - old["realized_value_usd"]
            output.append({"from_plan_id": prior, "to_plan_id": plan["id"],
                           "model_id": row["model_id"], "workload_id": row["workload_id"],
                           "status": "valued" if delta_cost > ZERO and delta_reachable >= ZERO else "unranked",
                           "reason": None if delta_cost > ZERO and delta_reachable >= ZERO else "nonpositive_cost_or_entitlement_delta",
                           "incremental_initial_cost_usd": delta_initial_cost,
                           "incremental_cost_usd": delta_cost, "incremental_reachable_value_usd": delta_reachable,
                           "incremental_realized_value_usd": delta_realized,
                           "incremental_initial_reachable_roi": ratio(delta_reachable, delta_initial_cost) if delta_initial_cost > ZERO else None,
                           "incremental_initial_realized_roi": ratio(delta_realized, delta_initial_cost) if delta_initial_cost > ZERO else None,
                           "incremental_reachable_roi": ratio(delta_reachable, delta_cost) if delta_cost > ZERO else None,
                           "incremental_realized_roi": ratio(delta_realized, delta_cost) if delta_cost > ZERO else None})
    return output


def analyze(data):
    data_kind, days, rates, fx_issue, api_prices, workloads, plans = validate(data)
    evaluations = []
    for plan in plans.values():
        for workload in workloads.values():
            row = evaluate_plan_workload(plan, workload, api_prices, rates, data_kind, days, fx_issue)
            if row is not None:
                evaluations.append(row)
        covered_models = {row["model_id"] for row in evaluations if row["plan_id"] == plan["id"]}
        offered_models = {rule["model_id"] for pool in plan["pools"] for rule in pool["rules"]}
        for mid in sorted(offered_models - covered_models):
            cost, cost_issues = monthly_cost(plan["price"], rates, data_kind)
            evaluations.append({"plan_id": plan["id"], "provider": plan["provider"],
                                "product": plan["product"], "tier": plan["tier"], "region": plan["region"],
                                "billing_regime": plan["billing_regime"], "model_id": mid,
                                "api_price_id": None, "workload_id": None, "workload_basis": None,
                                "access_context": None, "status": "unranked",
                                "reasons": ["workload_missing"] + cost_issues,
                                "evidence_grade": "insufficient", "reachable_bound_kind": "unvalued",
                                "realized_bound_kind": "unvalued", "value_bounds_usd": None,
                                "api_value_per_request_usd": None,
                                "entitlement_value_per_window_usd": None, "reachable_requests": None,
                                "reachable_value_usd": None, "realized_requests": None,
                                "realized_value_usd": None, "effective_utilization": None,
                                "monthly_cost": cost, "pools": [], "excluded_pools": [],
                                "valuation_scope": "unvalued", "access": plan.get("access"),
                                "limits": plan.get("limits"), "shared_pool_alternatives": {},
                                "reachable_roi_initial": None, "reachable_roi_renewal": None,
                                "realized_roi_initial": None, "realized_roi_renewal": None,
                                "break_even_utilization_initial": None,
                                "break_even_utilization_renewal": None})
    return {"schema_version": 1, "data_kind": data_kind, "period_days": days,
            "fx_as_of": data["fx"]["as_of"], "evaluations": evaluations,
            "rankings": rankings(evaluations), "upgrades": upgrades(plans, evaluations),
            "portfolio_analysis": {"status": "not_evaluated",
                                   "reason": "shared_demand_and_window_allocation_not_computed"},
            "notes": ["API value is replacement cost, not cash back or equal model quality.",
                      "Shared pool model rows are mutually exclusive alternatives; do not add them.",
                      "Own-API and realized rankings do not imply equal model capability.",
                      "Do not add individual-plan realized values or infer a best bundle without shared-demand allocation."]}


def jsonable(value):
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, dict):
        return {key: jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [jsonable(item) for item in value]
    return value


def markdown(result):
    rows = [f"# Plan value ({result['data_kind']} data)", "",
            "Monthly USD replacement value; model quality is not normalized.", "",
            "| Plan | Model | Workload | Reachable USD | Realized USD | Renewal ROI | Status / reason |",
            "| --- | --- | --- | ---: | ---: | ---: | --- |"]
    for row in result["evaluations"]:
        fmt = lambda x: "unknown" if x is None else format(x, ".4f")
        rows.append("| " + " | ".join((row["plan_id"], row["model_id"], row["workload_id"] or "unknown",
                                      fmt(row["reachable_value_usd"]), fmt(row["realized_value_usd"]),
                                      fmt(row["reachable_roi_renewal"]),
                                      row["status"] + (": " + ", ".join(row["reasons"]) if row["reasons"] else ""))) + " |")
    rows.extend(("", "Shared-pool alternatives are separate what-if rows, never additive.",
                 "Portfolio analysis: not_evaluated. Do not add individual-plan values or infer a best bundle.", ""))
    return "\n".join(rows)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON plan snapshot")
    parser.add_argument("--output", type=Path, help="write machine-readable JSON (default stdout)")
    parser.add_argument("--markdown", type=Path, help="optionally write a Markdown summary")
    args = parser.parse_args(argv)
    try:
        with args.input.open(encoding="utf-8") as handle:
            data = json.load(handle)
        result = analyze(data)
    except (OSError, json.JSONDecodeError, InputError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    serialized = json.dumps(jsonable(result), ensure_ascii=False, indent=2) + "\n"
    try:
        if args.output:
            args.output.write_text(serialized, encoding="utf-8")
        else:
            sys.stdout.write(serialized)
        if args.markdown:
            args.markdown.write_text(markdown(result), encoding="utf-8")
    except OSError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
