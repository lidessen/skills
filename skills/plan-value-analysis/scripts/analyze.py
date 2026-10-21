#!/usr/bin/env python3
"""Value current on-sale coding plans against sourced official API prices."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_FLOOR, getcontext
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

getcontext().prec = 40

BUCKETS = ("input", "output", "cache_read", "cache_write")
LEVELS = ("low", "base", "high")
ESTIMATE_CLASSES = (
    "official_current", "empirical_current", "stale_empirical",
    "explicit_assumption", "theoretical_window",
)
MODEL_ID = re.compile(
    r"^[a-z0-9][a-z0-9._-]*/[a-z0-9][a-z0-9._-]*@[a-z0-9][a-z0-9._-]*#[a-z0-9][a-z0-9._-]*$"
)
EVIDENCE_STATUSES = {
    "verified", "synthetic", "estimated", "undisclosed", "conflicting", "unavailable"
}
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


def real_date(value, where):
    try:
        parsed = date.fromisoformat(value)
        if parsed.isoformat() != value:
            raise ValueError
    except (TypeError, ValueError) as exc:
        raise InputError(f"{where} must be a real YYYY-MM-DD date") from exc
    return value


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
    return {
        key: None if nullable and value[key] is None else parse(value[key], f"{where}.{key}")
        for key in BUCKETS
    }


def evidence_issue(evidence, data_kind, where, query_date):
    if not isinstance(evidence, dict):
        return f"{where}:missing_evidence"
    status = evidence.get("status")
    if status not in EVIDENCE_STATUSES:
        return f"{where}:invalid_evidence_status"
    if data_kind == "synthetic" and status == "synthetic":
        return None
    if status != "verified":
        return f"{where}:evidence_{status}"
    try:
        fetched = real_date(evidence.get("fetched_at"), f"{where}.fetched_at")
    except InputError:
        return f"{where}:incomplete_verified_evidence"
    if not (
        isinstance(evidence.get("url"), str)
        and evidence["url"].startswith(("https://", "http://"))
        and isinstance(evidence.get("excerpt"), str)
        and evidence["excerpt"].strip()
    ):
        return f"{where}:incomplete_verified_evidence"
    if data_kind == "live" and fetched != query_date:
        return f"{where}:not_rechecked_on_query_date"
    return None


def add_issue(issues, issue):
    if issue and issue not in issues:
        issues.append(issue)


def fx_convert(amount, currency, rates):
    if amount is None or currency not in rates:
        return None
    return amount / rates[currency]


def price_per_operation(scenario, api_price, rates):
    if api_price is None:
        return None, "api_price_missing"
    if api_price["model_id"] != scenario["model_id"]:
        return None, "api_price_model_mismatch"
    if api_price["batch"] is not scenario["batch"]:
        return None, "api_price_batch_mismatch"
    context = scenario["context_tokens"]
    lower = integer(api_price.get("context_min", 0), "api_price.context_min")
    upper = api_price.get("context_max")
    if upper is not None:
        upper = integer(upper, "api_price.context_max", 1)
        if upper <= lower:
            raise InputError("api_price.context_max must exceed context_min")
    if context < lower or (upper is not None and context >= upper):
        return None, "api_price_context_mismatch"
    prices = bucket_numbers(api_price.get("per_million"), "api_price.per_million", nullable=True)
    if any(scenario["per_operation"][bucket] and prices[bucket] is None for bucket in BUCKETS):
        return None, "api_price_missing_token_rate"
    native = sum(
        (Decimal(scenario["per_operation"][bucket]) * (prices[bucket] or ZERO) / MILLION
         for bucket in BUCKETS),
        ZERO,
    )
    usd = fx_convert(native, api_price["currency"], rates)
    return (usd, None) if usd is not None else (None, "api_price_fx_missing")


def quota_amount(quota, unit):
    if unit == "token_buckets":
        if quota.get("amounts") is None:
            return None
        return bucket_numbers(
            quota["amounts"], "pool.quota.amounts", integer_values=True, nullable=True
        )
    return number(quota.get("amount"), "pool.quota.amount", nullable=True)


def is_direct_entitlement(pool, rule):
    return pool["unit"] in ("token_buckets", "currency") or "api_parity_credit_usd" in rule


def verified_credit_api_parity(pool, rule, api_price, rates, data_kind, query_date):
    """A continuous credit face rate is valid only when every maker tariff bucket matches."""
    if "api_parity_credit_usd" not in rule:
        return None, None
    parity = number(rule["api_parity_credit_usd"], "rule.api_parity_credit_usd",
                    Decimal("0.0000000000000000001"))
    if pool["unit"] != "credits" or rule.get("basis") != "weighted_tokens":
        raise InputError("api_parity_credit_usd requires weighted-token credit rules")
    issue = evidence_issue(rule.get("api_parity_evidence"), data_kind,
                           f"api_parity:{pool['id']}", query_date)
    if issue:
        return parity, issue
    weights = bucket_numbers(rule.get("per_million"), "rule.per_million", nullable=True)
    maker_prices = bucket_numbers(api_price.get("per_million"),
                                  "api_price.per_million", nullable=True)
    for bucket in BUCKETS:
        maker_usd = fx_convert(maker_prices[bucket], api_price["currency"], rates)
        if maker_prices[bucket] is not None and maker_usd is None:
            return parity, "api_price_fx_missing"
        if (maker_prices[bucket] is None) != (weights[bucket] is None) or (
            maker_usd is not None and weights[bucket] * parity != maker_usd
        ):
            return parity, "credit_to_maker_api_tariff_parity_not_proven"
    return parity, None


def debit_per_operation(rule, pool, scenario, api_usd, rates):
    allowed = {
        "requests": {"request"},
        "credits": {"request", "weighted_tokens"},
        "weighted_tokens": {"weighted_tokens"},
        "token_buckets": {"token_buckets"},
    }
    basis = rule.get("basis")
    if basis not in allowed[pool["unit"]]:
        raise InputError(f"pool unit {pool['unit']} cannot use debit basis {basis}")
    multiplier = number(rule.get("multiplier", "1"), "rule.multiplier", nullable=True)
    if multiplier is None:
        return None, "debit_unknown"
    if multiplier == ZERO:
        return None, "zero_debit_unbounded"
    if basis == "token_buckets":
        return None, None
    if basis == "request":
        units = number(rule.get("units_per_operation"), "rule.units_per_operation", nullable=True)
        if units is None:
            return None, "debit_unknown"
        debit = units * multiplier
    elif basis == "weighted_tokens":
        weights = bucket_numbers(rule.get("per_million"), "rule.per_million", nullable=True)
        if any(scenario["per_operation"][bucket] and weights[bucket] is None
               for bucket in BUCKETS):
            return None, "debit_unknown"
        debit = sum(
            (Decimal(scenario["per_operation"][bucket]) * (weights[bucket] or ZERO) / MILLION
             for bucket in BUCKETS),
            ZERO,
        ) * multiplier
    else:
        raise InputError("invalid rule basis")
    return (debit, None) if debit != ZERO else (None, "zero_debit_unbounded")


def cap_window(cap, where):
    window = obj(cap.get("window"), f"{where}.window")
    kind = window.get("kind")
    if kind not in ("monthly", "weekly", "rolling_hours"):
        raise InputError(f"{where}.window.kind must be monthly, weekly, or rolling_hours")
    if kind == "rolling_hours":
        integer(window.get("hours"), f"{where}.window.hours", 1)
    if kind == "weekly":
        # Weekly reset policy is evidence, not an inferred monthly multiplier.
        reset = window.get("reset")
        if reset not in ("calendar", "rolling", "subscription_anchor", "unknown"):
            raise InputError(
                f"{where}.window.reset must be calendar, rolling, "
                "subscription_anchor, or unknown"
            )
    return kind


def pool_value(pool, rule, scenario, api_price, api_usd, rates, data_kind, query_date):
    issues = []
    quota = obj(pool.get("quota"), "pool.quota")
    add_issue(issues, evidence_issue(quota.get("evidence"), data_kind, "quota", query_date))
    add_issue(issues, evidence_issue(rule.get("evidence"), data_kind, "model_rule", query_date))
    klass = pool["entitlement_class"]
    if klass != "guaranteed":
        add_issue(issues, "non_guaranteed_entitlement")
    unit = pool["unit"]
    amount = quota_amount(quota, unit)
    if amount is None or isinstance(amount, dict) and any(x is None for x in amount.values()):
        add_issue(issues, "quota_unknown")
    kind = cap_window(pool, f"pool.{pool['id']}")
    result = {
        "pool_id": pool["id"], "unit": unit, "window_kind": kind,
        "entitlement_class": klass, "status": "unranked", "reasons": issues,
        "window_api_value_usd": None, "monthly_api_value_usd": None,
        "monthly_api_value_upper_usd": None,
    }
    if issues:
        return result

    if unit == "token_buckets":
        if rule.get("basis") != "token_buckets":
            raise InputError("token_buckets pool requires token_buckets debit basis")
        multiplier = number(rule.get("multiplier", "1"), "rule.multiplier", nullable=True)
        if multiplier is None:
            result["reasons"].append("debit_unknown")
            return result
        if multiplier == ZERO:
            result["reasons"].append("zero_debit_unbounded")
            return result
        prices = bucket_numbers(api_price["per_million"], "api_price.per_million", nullable=True)
        if any(amount[bucket] and prices[bucket] is None for bucket in BUCKETS):
            result["reasons"].append("api_price_missing_token_rate")
            return result
        native = sum(
            (Decimal(amount[bucket]) / multiplier * (prices[bucket] or ZERO) / MILLION
             for bucket in BUCKETS),
            ZERO,
        )
        face_usd = fx_convert(native, api_price["currency"], rates)
        if face_usd is None:
            result["reasons"].append("api_price_fx_missing")
            return result
        if pool.get("additional_caps") or pool.get("daily_cap_requests") is not None:
            result["reasons"].append("token_bucket_additional_cap_unsupported")
            return result
        if kind == "monthly":
            result["status"] = "valued"
            result["monthly_api_value_usd"] = face_usd
        else:
            result["window_api_value_usd"] = face_usd
            result["reasons"].append("nonmonthly_quota_no_monthly_cap")
        return result

    if "api_parity_credit_usd" in rule:
        parity, parity_issue = verified_credit_api_parity(
            pool, rule, api_price, rates, data_kind, query_date
        )
        if parity_issue:
            result["reasons"].append(parity_issue)
            return result

        def face_value(balance):
            return balance * parity
    elif unit == "currency":
        if rule.get("basis") != "api_value":
            raise InputError("currency pool requires api_value debit basis")
        multiplier = number(rule.get("multiplier", "1"), "rule.multiplier", nullable=True)
        if multiplier is None:
            result["reasons"].append("debit_unknown")
            return result
        currency = string(quota.get("currency"), "pool.quota.currency")
        if multiplier == ZERO:
            result["reasons"].append("zero_debit_unbounded")
            return result
        if currency not in rates:
            result["reasons"].append("pool_currency_fx_missing")
            return result

        def face_value(balance):
            return balance / rates[currency] / multiplier
    else:
        debit, debit_issue = debit_per_operation(rule, pool, scenario, api_usd, rates)
        if debit_issue:
            result["reasons"].append(debit_issue)
            return result

        def face_value(balance):
            operations = (balance / debit).to_integral_value(rounding=ROUND_FLOOR)
            return operations * api_usd

    primary_usd = face_value(amount)
    if kind == "monthly":
        monthly_usd = primary_usd
    else:
        monthly_usd = None
        result["window_api_value_usd"] = primary_usd

    nonmonthly_restriction = kind != "monthly"
    monthly_cap_found = kind == "monthly"
    for cap in pool.get("additional_caps", []):
        cap_id = cap["id"]
        add_issue(result["reasons"], evidence_issue(
            cap.get("evidence"), data_kind, f"additional_cap:{cap_id}", query_date
        ))
        cap_amount = number(cap.get("amount"), f"additional_cap.{cap_id}.amount", nullable=True)
        if cap_amount is None:
            add_issue(result["reasons"], f"additional_cap:{cap_id}:unknown")
            continue
        cap_kind = cap_window(cap, f"additional_cap.{cap_id}")
        if cap_kind == "monthly":
            cap_usd = face_value(cap_amount)
            monthly_usd = cap_usd if monthly_usd is None else min(monthly_usd, cap_usd)
            monthly_cap_found = True
        else:
            nonmonthly_restriction = True
    if pool.get("daily_cap_requests") is not None:
        integer(pool["daily_cap_requests"], "pool.daily_cap_requests")
        nonmonthly_restriction = True
        add_issue(result["reasons"], "daily_cap_not_monthly_scaled")
    if result["reasons"] and any(
        item not in ("daily_cap_not_monthly_scaled",) for item in result["reasons"]
    ):
        return result
    if not monthly_cap_found or monthly_usd is None:
        add_issue(result["reasons"], "nonmonthly_quota_no_monthly_cap")
        return result

    if nonmonthly_restriction:
        result["status"] = "upper_bound"
        result["monthly_api_value_upper_usd"] = monthly_usd
        add_issue(result["reasons"], "short_window_or_daily_cap_makes_monthly_value_upper_bound")
    else:
        result["status"] = "valued"
        result["monthly_api_value_usd"] = monthly_usd
    return result


def monthly_cost(price, rates, data_kind, query_date):
    issues = []
    add_issue(issues, evidence_issue(price.get("evidence"), data_kind, "plan_price", query_date))
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
    cost = {
        "currency": currency, "months_per_bill": months,
        "tax_rate": tax_rate, "tax_included": tax_included,
    }
    for term in ("initial", "renewal"):
        amount = number(price.get(term), f"plan.price.{term}", nullable=True)
        listed = amount / Decimal(months) if amount is not None else None
        cost[f"{term}_monthly_listed_original"] = listed
        cost[f"{term}_monthly_listed_usd"] = fx_convert(listed, currency, rates)
        original = amount * factor / Decimal(months) if amount is not None and factor is not None else None
        usd = fx_convert(original, currency, rates)
        cost[f"{term}_monthly_original"] = original
        cost[f"{term}_monthly_usd"] = usd
        if amount is None:
            add_issue(issues, f"{term}_cost_unknown")
        elif usd is None and factor is not None:
            add_issue(issues, "plan_price_fx_missing")
    return cost, issues


def ratio(numerator, denominator):
    return numerator / denominator if numerator is not None and denominator not in (None, ZERO) else None


def estimate_levels(value, where, maximum=None):
    value = obj(value, where)
    if set(value) != set(LEVELS):
        raise InputError(f"{where} must have low, base, high")
    result = {level: number(value[level], f"{where}.{level}") for level in LEVELS}
    if not result["low"] <= result["base"] <= result["high"]:
        raise InputError(f"{where} must be ordered low <= base <= high")
    if maximum is not None and result["high"] > maximum:
        raise InputError(f"{where} must not exceed {maximum}")
    return result


def estimate_source(source, data_kind, query_date, where):
    source = obj(source, f"{where}.source")
    klass = source.get("class")
    if klass not in ESTIMATE_CLASSES:
        raise InputError(f"{where}.source.class is invalid")
    url = string(source.get("url"), f"{where}.source.url")
    if not url.startswith(("https://", "http://")):
        raise InputError(f"{where}.source.url must be HTTP(S)")
    fetched = real_date(source.get("fetched_at"), f"{where}.source.fetched_at")
    if data_kind == "live" and fetched != query_date:
        raise InputError(f"{where}.source must be rechecked on query_date")
    if klass in ("empirical_current", "stale_empirical"):
        observed = real_date(source.get("observed_at"), f"{where}.source.observed_at")
        if observed > query_date:
            raise InputError(f"{where}.source.observed_at is after query_date")
    match = source.get("model_match")
    if match not in ("exact", "not_applicable", "mismatch"):
        raise InputError(f"{where}.source.model_match is required")
    if match == "mismatch":
        string(source.get("mismatch_reason"), f"{where}.source.mismatch_reason")
    labels = obj(source.get("assumptions"), f"{where}.source.assumptions")
    if set(labels) != set(LEVELS):
        raise InputError(f"{where}.source.assumptions needs low, base, high labels")
    for level in LEVELS:
        string(labels[level], f"{where}.source.assumptions.{level}")
    return source


def estimated_face_value(pool, rule, scenario, api_price, api_usd, rates, amount):
    unit = pool["unit"]
    multiplier = number(rule.get("multiplier", "1"), "rule.multiplier", nullable=True)
    if multiplier in (None, ZERO):
        return None, "debit_unknown" if multiplier is None else "zero_debit_unbounded"
    if unit == "token_buckets":
        if rule.get("basis") != "token_buckets":
            raise InputError("token_buckets pool requires token_buckets debit basis")
        prices = bucket_numbers(api_price["per_million"], "api_price.per_million", nullable=True)
        if any(amount[bucket] and prices[bucket] is None for bucket in BUCKETS):
            return None, "api_price_missing_token_rate"
        native = sum((amount[bucket] / multiplier * (prices[bucket] or ZERO) / MILLION
                      for bucket in BUCKETS), ZERO)
        value = fx_convert(native, api_price["currency"], rates)
        return (value, None) if value is not None else (None, "api_price_fx_missing")
    if unit == "currency":
        if rule.get("basis") != "api_value":
            raise InputError("currency pool requires api_value debit basis")
        currency = string(pool["quota"].get("currency"), "pool.quota.currency")
        value = fx_convert(amount / multiplier, currency, rates)
        return (value, None) if value is not None else (None, "pool_currency_fx_missing")
    debit, issue = debit_per_operation(rule, pool, scenario, api_usd, rates)
    if issue:
        return None, issue
    operations = (amount / debit).to_integral_value(rounding=ROUND_FLOOR)
    return operations * api_usd, None


def estimated_pool(pool, rule, scenario, api_price, api_usd, rates, data_kind,
                   query_date, matching_pool_ids):
    ident = pool["id"]
    issues = []
    add_issue(issues, evidence_issue(rule.get("evidence"), data_kind, f"model_rule:{ident}", query_date))
    estimate = pool.get("estimate")
    quota = obj(pool.get("quota"), f"pool.{ident}.quota")
    amount = quota_amount(quota, pool["unit"])
    if isinstance(amount, dict) and any(value is None for value in amount.values()):
        amount = None
    if amount is not None:
        add_issue(issues, evidence_issue(quota.get("evidence"), data_kind, f"quota:{ident}", query_date))
    needs_estimate = (
        pool["entitlement_class"] != "guaranteed"
        or amount is None
        or pool["window"]["kind"] != "monthly"
        or any(cap["window"]["kind"] != "monthly" for cap in pool.get("additional_caps", []))
        or pool.get("daily_cap_requests") is not None
    )
    if needs_estimate and estimate is None:
        add_issue(issues, "estimate_missing_for_current_total")
    source = None
    if estimate is not None:
        estimate = obj(estimate, f"pool.{ident}.estimate")
        source = estimate_source(estimate.get("source"), data_kind, query_date, f"pool.{ident}.estimate")
        if source["model_match"] == "mismatch" or (estimate.get("quota_anchor") is not None
            and source["model_match"] != "exact"):
            add_issue(issues, "estimate_model_or_plan_mismatch")
    if amount is None:
        if estimate is None or estimate.get("quota_anchor") is None:
            add_issue(issues, "quota_anchor_missing")
            quotas = None
        elif pool["unit"] == "token_buckets":
            raise InputError(f"pool.{ident}.estimate.quota_anchor cannot replace token buckets")
        else:
            quotas = estimate_levels(estimate["quota_anchor"], f"pool.{ident}.estimate.quota_anchor")
            multiplier = number(estimate.get("quota_multiplier", "1"),
                                f"pool.{ident}.estimate.quota_multiplier")
            if multiplier != 1:
                add_issue(issues, evidence_issue(estimate.get("multiplier_evidence"),
                          data_kind, f"quota_multiplier:{ident}", query_date))
            quotas = {level: quotas[level] * multiplier for level in LEVELS}
    else:
        if estimate is not None and estimate.get("quota_anchor") is not None:
            raise InputError(f"pool.{ident}.estimate.quota_anchor conflicts with official quota")
        quotas = {level: amount for level in LEVELS}
    if pool["entitlement_class"] != "guaranteed":
        if estimate is None or estimate.get("presence") is None:
            add_issue(issues, "current_extra_presence_missing")
            presence = None
        else:
            presence = estimate_levels(estimate["presence"],
                                       f"pool.{ident}.estimate.presence", maximum=Decimal(1))
        other_ids = matching_pool_ids - {ident}
        if other_ids:
            additive_to = set(estimate.get("additive_to", [])) if estimate is not None else set()
            if additive_to != other_ids:
                add_issue(issues, "extra_additivity_not_proven")
            else:
                add_issue(issues, evidence_issue(estimate.get("stacking_evidence"),
                          data_kind, f"stacking:{ident}", query_date))
    else:
        presence = {level: Decimal(1) for level in LEVELS}
        if estimate is not None and estimate.get("presence") is not None:
            raise InputError(f"pool.{ident}.estimate.presence applies only to extra entitlements")
    counts = obj(estimate.get("window_counts", {}), f"pool.{ident}.estimate.window_counts") \
        if estimate is not None else {}
    has_short_window = pool["window"]["kind"] != "monthly" or any(
        cap["window"]["kind"] != "monthly" for cap in pool.get("additional_caps", [])
    )
    if has_short_window and source is not None and source["class"] == "official_current":
        add_issue(issues, "window_extrapolation_needs_estimate_class")

    def window_factor(key, window):
        kind = cap_window({"window": window}, f"pool.{ident}.{key}")
        if kind == "monthly":
            return {level: Decimal(1) for level in LEVELS}
        if key not in counts:
            add_issue(issues, f"window_counts_missing:{key}")
            return None
        return estimate_levels(counts[key], f"pool.{ident}.estimate.window_counts.{key}")

    primary_counts = window_factor("primary", pool["window"])
    cap_counts = {}
    for cap in pool.get("additional_caps", []):
        add_issue(issues, evidence_issue(cap.get("evidence"), data_kind,
                  f"additional_cap:{ident}:{cap['id']}", query_date))
        cap_counts[cap["id"]] = window_factor(cap["id"], cap["window"])
        if cap.get("amount") is None:
            add_issue(issues, f"additional_cap_unknown:{cap['id']}")
    if pool.get("daily_cap_requests") is not None:
        add_issue(issues, "daily_cap_estimate_unsupported")
    if pool["unit"] == "token_buckets" and pool.get("additional_caps"):
        add_issue(issues, "token_bucket_additional_cap_unsupported")
    parity, parity_issue = verified_credit_api_parity(
        pool, rule, api_price, rates, data_kind, query_date
    )
    add_issue(issues, parity_issue)
    values = {level: None for level in LEVELS}
    budgets = {level: None for level in LEVELS}
    if not issues and quotas is not None and presence is not None and primary_counts is not None:
        for level in LEVELS:
            if pool["unit"] == "token_buckets":
                budget = {bucket: Decimal(quotas[level][bucket]) * primary_counts[level]
                          * presence[level] for bucket in BUCKETS}
            else:
                budget = quotas[level] * primary_counts[level]
                for cap in pool.get("additional_caps", []):
                    cap_amount = number(cap.get("amount"), f"additional_cap.{cap['id']}.amount")
                    budget = min(budget, cap_amount * cap_counts[cap["id"]][level])
                budget *= presence[level]
            budgets[level] = budget
            if parity is not None:
                value, issue = budget * parity, None
            else:
                value, issue = estimated_face_value(
                    pool, rule, scenario, api_price, api_usd, rates, budget
                )
            add_issue(issues, issue)
            values[level] = value
    return {
        "pool_id": ident, "entitlement_class": pool["entitlement_class"],
        "source_class": source["class"] if source else "official_current",
        "source": source, "api_parity_credit_usd": parity, "monthly_budget": budgets,
        "monthly_api_value_usd": values, "reasons": issues,
    }


def evaluate_plan_scenario(plan, scenario, api_prices, rates, data_kind, query_date, fx_issue,
                           direct=False):
    convertible = [
        (pool, rule)
        for pool in plan["pools"]
        for rule in pool["rules"]
        if rule["model_id"] == scenario["model_id"]
        and not is_direct_entitlement(pool, rule)
        and rule["api_price_id"] == scenario["api_price_id"]
    ]
    direct_matching = [
        (pool, rule)
        for pool in plan["pools"]
        for rule in pool["rules"]
        if rule["model_id"] == scenario["model_id"]
        and is_direct_entitlement(pool, rule)
        and rule["api_price_id"] == scenario["api_price_id"]
    ]
    if direct and not direct_matching:
        return None
    if not direct and not any(
        pool["entitlement_class"] == "guaranteed" for pool, _ in convertible
    ):
        return None
    matching = direct_matching if direct else convertible + direct_matching
    issues = []
    availability = plan["availability"]
    if availability.get("status") != "on_sale":
        add_issue(issues, "plan_not_verified_currently_on_sale")
    add_issue(issues, evidence_issue(
        availability.get("evidence"), data_kind, "plan_availability", query_date
    ))
    api_price = api_prices.get(scenario["api_price_id"])
    valuation_needs_fx = (
        (api_price is not None and api_price.get("currency") != "USD")
        or any(pool["unit"] == "currency" and pool["quota"].get("currency") != "USD"
               for pool, _ in matching)
    )
    if valuation_needs_fx:
        add_issue(issues, fx_issue)
    if data_kind == "live":
        for field in ("access", "limits"):
            info = plan.get(field)
            if not isinstance(info, dict):
                add_issue(issues, f"plan_{field}:missing_evidence")
            else:
                add_issue(issues, evidence_issue(
                    info.get("evidence"), data_kind, f"plan_{field}", query_date
                ))
    access = plan.get("access")
    if isinstance(access, dict) and access.get("api_access") is not True and not access.get("clients"):
        add_issue(issues, "no_verified_access_path")
    if api_price is not None:
        add_issue(issues, evidence_issue(
            api_price.get("evidence"), data_kind, "api_price", query_date
        ))
    if direct:
        api_usd = ZERO if api_price is not None else None
        if api_price is None:
            add_issue(issues, "api_price_missing")
        elif api_price["model_id"] != scenario["model_id"]:
            add_issue(issues, "api_price_model_mismatch")
    else:
        api_usd, api_issue = price_per_operation(scenario, api_price, rates)
        add_issue(issues, api_issue)
    if scenario["basis"] == "official_usage":
        add_issue(issues, evidence_issue(
            scenario.get("evidence"), data_kind, "official_usage", query_date
        ))
    cost, cost_issues = monthly_cost(plan["price"], rates, data_kind, query_date)
    pools = []
    excluded_pools = []
    if api_usd is not None and api_price is not None:
        for pool, rule in matching:
            result = pool_value(
                pool, rule, scenario, api_price, api_usd, rates, data_kind, query_date
            )
            if "non_guaranteed_entitlement" in result["reasons"]:
                excluded_pools.append(result)
            else:
                pools.append(result)
                for issue in result["reasons"]:
                    if result["status"] == "unranked" or issue not in (
                        "daily_cap_not_monthly_scaled",
                        "short_window_or_daily_cap_makes_monthly_value_upper_bound",
                    ):
                        add_issue(issues, f"pool:{pool['id']}:{issue}")
    else:
        pools = [
            {"pool_id": pool["id"], "status": "unranked", "reasons": ["api_price_unusable"]}
            for pool, _ in matching
            if pool["entitlement_class"] == "guaranteed"
        ]
    if not pools:
        add_issue(issues, "no_guaranteed_eligible_pool")
    has_direct_component = any(is_direct_entitlement(pool, rule) for pool, rule in matching
                               if pool["entitlement_class"] == "guaranteed")

    status = "unranked"
    value_kind = "unvalued"
    monthly_value = None
    monthly_upper = None
    window_values = {
        item["pool_id"]: item["window_api_value_usd"]
        for item in pools
        if item.get("window_api_value_usd") is not None
    }
    if not issues:
        if any(item["status"] == "unranked" for item in pools):
            status = "unranked"
            add_issue(issues, "pool_monthly_value_unavailable")
        elif any(item["status"] == "upper_bound" for item in pools):
            status = "upper_bound"
            monthly_upper = sum(
                (item["monthly_api_value_usd"] if item["monthly_api_value_usd"] is not None
                 else item["monthly_api_value_upper_usd"]
                 for item in pools),
                ZERO,
            )
            value_kind = "monthly_cap_upper_bound"
            add_issue(issues, "nonmonthly_window_makes_monthly_value_upper_bound")
        else:
            status = "valued"
            monthly_value = sum((item["monthly_api_value_usd"] for item in pools), ZERO)
            value_kind = (
                "bucket_face_value" if all(item["unit"] == "token_buckets" for item in pools)
                else "api_spend_face_value" if all(item["unit"] == "currency" for item in pools)
                else "mixed_direct_face_value" if direct
                else "mixed_direct_and_operation_conversion" if has_direct_component
                else "official_usage_conversion" if scenario["basis"] == "official_usage"
                else "assumption_conversion"
            )
    for issue in cost_issues:
        add_issue(issues, issue)
    if plan["price"].get("currency") != "USD":
        add_issue(issues, fx_issue)
    quote_verified = not any(issue.startswith("plan_price:") for issue in cost_issues) and not (
        plan["price"].get("currency") != "USD" and fx_issue
    )
    result = {
        "plan_id": plan["id"], "provider": plan["provider"], "product": plan["product"],
        "tier": plan["tier"], "region": plan["region"],
        "availability": availability, "model_id": scenario["model_id"],
        "scenario_id": scenario["id"], "scenario_basis": scenario["basis"],
        "scenario_label": scenario["label"], "api_price_id": scenario["api_price_id"],
        "status": status, "reasons": issues, "value_kind": value_kind,
        "evidence_grade": (
            "insufficient" if issues and status == "unranked"
            else "synthetic" if data_kind == "synthetic"
            else "official_entitlement" if direct
            else "official_terms_with_assumption" if scenario["basis"] == "assumption"
            else "official_terms_and_usage"
        ),
        "api_value_per_operation_usd": None if direct else api_usd,
        "window_api_value_usd_by_pool": window_values,
        "monthly_api_value_usd": monthly_value,
        "monthly_api_value_upper_usd": monthly_upper,
        "monthly_cost": cost,
        "roi_initial": ratio(monthly_value, cost["initial_monthly_usd"])
        if quote_verified else None,
        "roi_renewal": ratio(monthly_value, cost["renewal_monthly_usd"])
        if quote_verified else None,
        "roi_initial_listed": ratio(
            monthly_value, cost["initial_monthly_listed_usd"]
        ) if quote_verified else None,
        "roi_renewal_listed": ratio(
            monthly_value, cost["renewal_monthly_listed_usd"]
        ) if quote_verified else None,
        "roi_initial_upper": ratio(monthly_upper, cost["initial_monthly_usd"])
        if quote_verified else None,
        "roi_renewal_upper": ratio(monthly_upper, cost["renewal_monthly_usd"])
        if quote_verified else None,
        "roi_initial_listed_upper": ratio(
            monthly_upper, cost["initial_monthly_listed_usd"]
        ) if quote_verified else None,
        "roi_renewal_listed_upper": ratio(
            monthly_upper, cost["renewal_monthly_listed_usd"]
        ) if quote_verified else None,
        "component_pool_ids": [item["pool_id"] for item in pools],
        "pools": pools, "excluded_pools": excluded_pools,
        "shared_pool_alternatives": {
            pool["id"]: sorted(
                rule["model_id"] for rule in pool["rules"]
                if rule["model_id"] != scenario["model_id"]
            )
            for pool, _ in matching
            if len(pool["rules"]) > 1
        },
        "access": plan.get("access"), "limits": plan.get("limits"),
    }
    if status == "valued":
        for term in ("initial", "renewal"):
            if cost[f"{term}_monthly_usd"] == ZERO:
                add_issue(result["reasons"], f"zero_{term}_cost_roi_undefined")
    cny_rate = rates.get("CNY")
    if cny_rate is not None and fx_issue is None:
        for key in ("api_value_per_operation", "monthly_api_value", "monthly_api_value_upper"):
            usd = result[f"{key}_usd"]
            result[f"{key}_cny"] = usd * cny_rate if usd is not None else None
        for term in ("initial", "renewal"):
            usd = cost[f"{term}_monthly_usd"]
            cost[f"{term}_monthly_cny"] = usd * cny_rate if usd is not None else None
    return result


def evaluate_estimated_plan_scenario(plan, scenario, api_prices, rates, data_kind,
                                     query_date, fx_issue, direct=False):
    matching = [
        (pool, rule) for pool in plan["pools"] for rule in pool["rules"]
        if rule["model_id"] == scenario["model_id"]
        and rule["api_price_id"] == scenario["api_price_id"]
        and (not direct or is_direct_entitlement(pool, rule))
    ]
    if not matching:
        return None
    if direct and any(not is_direct_entitlement(pool, rule) for pool, rule in matching):
        raise InputError("direct estimate cannot include converted pool")
    if not direct and all(is_direct_entitlement(pool, rule) for pool, rule in matching):
        return None
    issues = []
    availability = plan["availability"]
    if availability.get("status") != "on_sale":
        add_issue(issues, "plan_not_verified_currently_on_sale")
    add_issue(issues, evidence_issue(
        availability.get("evidence"), data_kind, "plan_availability", query_date
    ))
    for field in ("access", "limits"):
        if data_kind == "live":
            info = plan.get(field)
            add_issue(issues, evidence_issue(
                info.get("evidence") if isinstance(info, dict) else None,
                data_kind, f"plan_{field}", query_date
            ))
    access = plan.get("access")
    if isinstance(access, dict) and access.get("api_access") is not True and not access.get("clients"):
        add_issue(issues, "no_verified_access_path")
    api_price = api_prices.get(scenario["api_price_id"])
    if api_price is None:
        add_issue(issues, "api_price_missing")
        api_usd = None
    else:
        add_issue(issues, evidence_issue(
            api_price.get("evidence"), data_kind, "api_price", query_date
        ))
        if api_price["model_id"] != scenario["model_id"]:
            add_issue(issues, "api_price_model_mismatch")
        if direct:
            api_usd = ZERO
        else:
            api_usd, api_issue = price_per_operation(scenario, api_price, rates)
            add_issue(issues, api_issue)
    if scenario["basis"] == "official_usage":
        add_issue(issues, evidence_issue(
            scenario.get("evidence"), data_kind, "official_usage", query_date
        ))
    valuation_fx = (
        (api_price is not None and api_price.get("currency") != "USD")
        or any(pool["unit"] == "currency" and pool["quota"].get("currency") != "USD"
               for pool, _ in matching)
    )
    if valuation_fx:
        add_issue(issues, fx_issue)
    cost, cost_issues = monthly_cost(plan["price"], rates, data_kind, query_date)
    components = []
    if api_usd is not None and api_price is not None:
        ids = {pool["id"] for pool, _ in matching}
        for pool, rule in matching:
            component = estimated_pool(
                pool, rule, scenario, api_price, api_usd, rates,
                data_kind, query_date, ids
            )
            components.append(component)
            for issue in component["reasons"]:
                add_issue(issues, f"pool:{pool['id']}:{issue}")
    else:
        add_issue(issues, "api_price_unusable")
    values = {level: None for level in LEVELS}
    if not issues:
        values = {
            level: sum((component["monthly_api_value_usd"][level]
                        for component in components), ZERO)
            for level in LEVELS
        }
    for issue in cost_issues:
        add_issue(issues, issue)
    if plan["price"].get("currency") != "USD":
        add_issue(issues, fx_issue)
    quote_verified = not any(issue.startswith("plan_price:") for issue in cost_issues) and not (
        plan["price"].get("currency") != "USD" and fx_issue
    )
    sources = sorted({component["source_class"] for component in components})
    status = "estimated" if values["base"] is not None else "unranked"
    return {
        "plan_id": plan["id"], "provider": plan["provider"], "product": plan["product"],
        "tier": plan["tier"], "region": plan["region"],
        "model_id": scenario["model_id"], "api_price_id": scenario["api_price_id"],
        "scenario_id": f"direct:{scenario['model_id']}" if direct else scenario["id"],
        "scenario_label": scenario["label"],
        "category": "exact_model", "status": status, "reasons": issues,
        "source_classes": sources, "components": components,
        "component_pool_ids": [component["pool_id"] for component in components],
        "monthly_api_value_usd": values,
        "monthly_cost": cost,
        "roi_initial": {level: ratio(values[level], cost["initial_monthly_usd"])
                        if quote_verified else None for level in LEVELS},
        "roi_renewal": {level: ratio(values[level], cost["renewal_monthly_usd"])
                        if quote_verified else None for level in LEVELS},
        "roi_initial_listed": {
            level: ratio(values[level], cost["initial_monthly_listed_usd"])
            if quote_verified else None for level in LEVELS
        },
        "roi_renewal_listed": {
            level: ratio(values[level], cost["renewal_monthly_listed_usd"])
            if quote_verified else None for level in LEVELS
        },
        "shared_pool_alternatives": {
            pool["id"]: sorted(other["model_id"] for other in pool["rules"]
                               if other["model_id"] != scenario["model_id"])
            for pool, _ in matching if len(pool["rules"]) > 1
        },
    }


def evaluate_estimate_bundle(plan, rates, data_kind, query_date, fx_issue):
    """Value a reported mixed-model API-equivalent observation, without model parity claims."""
    bundle = plan.get("estimate_bundle")
    if bundle is None:
        return None
    bundle = obj(bundle, f"plans.{plan['id']}.estimate_bundle")
    bundle_id = string(bundle.get("id"), "estimate_bundle.id")
    source = estimate_source(bundle.get("source"), data_kind, query_date,
                             f"plans.{plan['id']}.estimate_bundle")
    if source["class"] == "official_current":
        raise InputError("estimate_bundle source must identify an empirical or assumed API value")
    if source["model_match"] == "exact":
        raise InputError("mixed estimate_bundle cannot claim an exact-model match")
    weekly = estimate_levels(bundle.get("weekly_api_value_usd"),
                             "estimate_bundle.weekly_api_value_usd")
    counts = estimate_levels(bundle.get("monthly_window_counts"),
                             "estimate_bundle.monthly_window_counts")
    issues = []
    if source["model_match"] == "mismatch":
        add_issue(issues, "bundle_plan_or_model_mismatch")
    if plan["availability"].get("status") != "on_sale":
        add_issue(issues, "plan_not_verified_currently_on_sale")
    add_issue(issues, evidence_issue(plan["availability"].get("evidence"), data_kind,
                                     "plan_availability", query_date))
    if data_kind == "live":
        for field in ("access", "limits"):
            info = plan.get(field)
            add_issue(issues, evidence_issue(info.get("evidence") if isinstance(info, dict)
                                         else None, data_kind, f"plan_{field}", query_date))
    if isinstance(plan.get("access"), dict) and not (
        plan["access"].get("api_access") is True or plan["access"].get("clients")
    ):
        add_issue(issues, "no_verified_access_path")
    interactive = {level: weekly[level] * counts[level] for level in LEVELS}
    credit = {level: ZERO for level in LEVELS}
    credit_source = None
    credit_input = bundle.get("api_credit")
    if credit_input is not None:
        credit_input = obj(credit_input, "estimate_bundle.api_credit")
        credit_source = estimate_source(credit_input.get("source"), data_kind, query_date,
                                        "estimate_bundle.api_credit")
        monthly_credit = number(credit_input.get("monthly_usd"),
                                "estimate_bundle.api_credit.monthly_usd")
        presence = estimate_levels(credit_input.get("presence"),
                                   "estimate_bundle.api_credit.presence", maximum=Decimal(1))
        add_issue(issues, evidence_issue(credit_input.get("independence_evidence"),
                  data_kind, "estimate_bundle.api_credit.independence", query_date))
        if credit_source["model_match"] == "mismatch":
            add_issue(issues, "api_credit_plan_mismatch")
        credit = {level: monthly_credit * presence[level] for level in LEVELS}
    values = {level: interactive[level] + credit[level] for level in LEVELS}
    if issues:
        values = {level: None for level in LEVELS}
    cost, cost_issues = monthly_cost(plan["price"], rates, data_kind, query_date)
    for issue in cost_issues:
        add_issue(issues, issue)
    if plan["price"].get("currency") != "USD":
        add_issue(issues, fx_issue)
    quote_verified = not any(issue.startswith("plan_price:") for issue in cost_issues) and not (
        plan["price"].get("currency") != "USD" and fx_issue
    )
    status = "estimated" if values["base"] is not None else "unranked"
    return {
        "plan_id": plan["id"], "provider": plan["provider"], "product": plan["product"],
        "tier": plan["tier"], "region": plan["region"], "category": "mixed_model_bundle",
        "model_id": None, "api_price_id": None, "scenario_id": bundle_id,
        "scenario_label": "Source-reported mixed-model weekly API value; sensitivity across source assumptions",
        "status": status, "reasons": issues, "source_classes": sorted({source["class"]} | (
            {credit_source["class"]} if credit_source is not None else set()
        )),
        "source": source, "components": {
            "interactive_mixed_usd": interactive,
            "api_credit_usd": credit,
            "api_credit_source": credit_source,
            "weekly_source_reported_usd": weekly,
            "monthly_window_counts": counts,
        },
        "component_pool_ids": [], "monthly_api_value_usd": values,
        "monthly_cost": cost,
        "roi_initial": {level: ratio(values[level], cost["initial_monthly_usd"])
                        if quote_verified else None for level in LEVELS},
        "roi_renewal": {level: ratio(values[level], cost["renewal_monthly_usd"])
                        if quote_verified else None for level in LEVELS},
        "roi_initial_listed": {level: ratio(values[level], cost["initial_monthly_listed_usd"])
                               if quote_verified else None for level in LEVELS},
        "roi_renewal_listed": {level: ratio(values[level], cost["renewal_monthly_listed_usd"])
                               if quote_verified else None for level in LEVELS},
        "shared_pool_alternatives": {},
    }


def evaluate_empirical_observation(plan, observation, api_prices, rates, data_kind,
                                   query_date, fx_issue):
    """Reprice disjoint observed token buckets; only explicit meter projection estimates capacity."""
    observation = obj(observation, f"plans.{plan['id']}.empirical_observation")
    ident = string(observation.get("id"), "empirical_observation.id")
    mid = model_id(observation.get("model_id"), f"empirical_observation.{ident}.model_id")
    price_id = string(observation.get("api_price_id"),
                      f"empirical_observation.{ident}.api_price_id")
    source = estimate_source(observation.get("source"), data_kind, query_date,
                             f"empirical_observation.{ident}")
    if source["class"] not in ("empirical_current", "stale_empirical"):
        raise InputError("empirical_observation needs an empirical source class")
    raw = bucket_numbers(observation.get("token_buckets"),
                         f"empirical_observation.{ident}.token_buckets", integer_values=True)
    if not any(raw.values()):
        raise InputError("empirical_observation.token_buckets cannot all be zero")
    if observation.get("accounts") != 1 or observation.get("extra_usage") is not False:
        raise InputError("empirical_observation requires one account and no paid extra usage")
    if observation.get("window_kind") != "weekly":
        raise InputError("empirical_observation.window_kind must be weekly")
    start = number(observation.get("meter_start"), "empirical_observation.meter_start")
    end = number(observation.get("meter_end"), "empirical_observation.meter_end")
    if not ZERO <= start < end <= 1:
        raise InputError("empirical_observation meter must rise within [0,1]")
    exhausted = observation.get("exhausted")
    if not isinstance(exhausted, bool) or exhausted and end < Decimal("0.99"):
        raise InputError("empirical_observation.exhausted contradicts meter_end")
    linear = observation.get("linear_meter_projection")
    if not isinstance(linear, bool):
        raise InputError("empirical_observation.linear_meter_projection must be boolean")
    basis = obj(observation.get("value_basis"), "empirical_observation.value_basis")
    if set(basis) != set(LEVELS) or any(basis[level] not in ("observed", "projected")
                                             for level in LEVELS):
        raise InputError("empirical_observation.value_basis needs observed/projected low, base, high")
    if "projected" in basis.values() and not linear:
        raise InputError("projected empirical capacity needs linear_meter_projection=true")
    counts = estimate_levels(observation.get("monthly_window_counts"),
                             "empirical_observation.monthly_window_counts")
    context = integer(observation.get("context_tokens"),
                      "empirical_observation.context_tokens")
    if not isinstance(observation.get("batch"), bool):
        raise InputError("empirical_observation.batch must be boolean")
    scenario = {"model_id": mid, "api_price_id": price_id,
                "context_tokens": context, "batch": observation["batch"],
                "per_operation": raw}
    issues = []
    if source["model_match"] != "exact":
        add_issue(issues, "empirical_model_or_plan_mismatch")
    if plan["availability"].get("status") != "on_sale":
        add_issue(issues, "plan_not_verified_currently_on_sale")
    add_issue(issues, evidence_issue(plan["availability"].get("evidence"), data_kind,
                                     "plan_availability", query_date))
    if data_kind == "live":
        for field in ("access", "limits"):
            info = plan.get(field)
            add_issue(issues, evidence_issue(info.get("evidence") if isinstance(info, dict)
                                         else None, data_kind, f"plan_{field}", query_date))
    api_price = api_prices.get(price_id)
    if api_price is not None:
        add_issue(issues, evidence_issue(api_price.get("evidence"), data_kind,
                                         "api_price", query_date))
        if raw["cache_write"]:
            duration = string(observation.get("cache_write_duration"),
                              "empirical_observation.cache_write_duration")
            if duration != api_price.get("cache_write_duration"):
                add_issue(issues, "cache_write_duration_price_mismatch")
    observed_usd, price_issue = price_per_operation(scenario, api_price, rates)
    add_issue(issues, price_issue)
    if api_price is not None and api_price["currency"] != "USD":
        add_issue(issues, fx_issue)
    cost, cost_issues = monthly_cost(plan["price"], rates, data_kind, query_date)
    if plan["price"].get("currency") != "USD":
        add_issue(issues, fx_issue)
    quote_verified = not any(issue.startswith("plan_price:") for issue in cost_issues) and not (
        plan["price"].get("currency") != "USD" and fx_issue
    )
    projected_usd = observed_usd / (end - start) if observed_usd is not None and linear else None
    if not linear and not (exhausted and start == ZERO):
        add_issue(issues, "observed_usage_only_not_total_capacity")
    if basis["base"] == "observed" and not (exhausted and start == ZERO):
        add_issue(issues, "base_observation_is_only_lower_bound")
    weekly = {level: (observed_usd if basis[level] == "observed" else projected_usd)
              for level in LEVELS}
    values = {level: (weekly[level] * counts[level] if weekly[level] is not None else None)
              for level in LEVELS}
    if all(value is not None for value in values.values()) and not (
        values["low"] <= values["base"] <= values["high"]
    ):
        raise InputError("empirical_observation estimated values must order low <= base <= high")
    if issues:
        values = {level: None for level in LEVELS}
    for issue in cost_issues:
        add_issue(issues, issue)
    return {
        "plan_id": plan["id"], "provider": plan["provider"], "product": plan["product"],
        "tier": plan["tier"], "region": plan["region"], "category": "exact_model",
        "model_id": mid, "api_price_id": price_id, "scenario_id": ident,
        "scenario_label": "Disjoint raw token buckets valued at maker API tariff",
        "status": "estimated" if values["base"] is not None else "unranked",
        "reasons": issues, "source_classes": [source["class"]], "source": source,
        "components": {"observed_window_api_usd": observed_usd,
                       "projected_full_window_api_usd": projected_usd,
                       "meter_start": start, "meter_end": end, "exhausted": exhausted,
                       "capacity_basis": basis, "monthly_window_counts": counts,
                       "token_buckets": raw},
        "component_pool_ids": [], "monthly_api_value_usd": values, "monthly_cost": cost,
        "roi_initial": {level: ratio(values[level], cost["initial_monthly_usd"])
                        if quote_verified else None for level in LEVELS},
        "roi_renewal": {level: ratio(values[level], cost["renewal_monthly_usd"])
                        if quote_verified else None for level in LEVELS},
        "roi_initial_listed": {level: ratio(values[level], cost["initial_monthly_listed_usd"])
                               if quote_verified else None for level in LEVELS},
        "roi_renewal_listed": {level: ratio(values[level], cost["renewal_monthly_listed_usd"])
                               if quote_verified else None for level in LEVELS},
        "shared_pool_alternatives": {},
    }


def index_items(items, key, where):
    result = {}
    for index, item in enumerate(array(items, where)):
        item = obj(item, f"{where}[{index}]")
        ident = string(item.get(key), f"{where}[{index}].{key}")
        if ident in result:
            raise InputError(f"duplicate {where} {key}: {ident}")
        result[ident] = item
    return result


def validate(data, today=None):
    obj(data, "input")
    if data.get("schema_version") != 2:
        raise InputError("schema_version must be 2; old plan snapshots are not current-plan inputs")
    data_kind = data.get("data_kind", "live")
    if data_kind not in ("live", "synthetic"):
        raise InputError("data_kind must be live or synthetic")
    query_date = real_date(data.get("query_date"), "query_date")
    zone_name = data.get("query_timezone")
    if zone_name is not None:
        zone_name = string(zone_name, "query_timezone")
        try:
            query_zone = ZoneInfo(zone_name)
        except (ZoneInfoNotFoundError, ValueError) as exc:
            raise InputError("query_timezone must be a valid IANA timezone") from exc
    else:
        query_zone = None
    if today is None:
        execution_date = datetime.now(query_zone).date() if query_zone else date.today()
    elif isinstance(today, datetime):
        if today.tzinfo is None:
            raise InputError("today datetime must have a timezone")
        execution_date = today.astimezone(query_zone).date() if query_zone else today.astimezone().date()
    elif isinstance(today, date):
        execution_date = today
    else:
        raise InputError("today must be a date or timezone-aware datetime")
    if data_kind == "live" and query_date != execution_date.isoformat():
        raise InputError("live query_date must equal today's date in query_timezone (or host local date)")
    fx = obj(data.get("fx"), "fx")
    real_date(fx.get("as_of"), "fx.as_of")
    raw_rates = obj(fx.get("per_usd"), "fx.per_usd")
    rates = {
        currency: number(rate, f"fx.per_usd.{currency}", Decimal("0.0000000000000000001"))
        for currency, rate in raw_rates.items()
    }
    if rates.get("USD") != Decimal(1):
        raise InputError("fx.per_usd.USD must be 1")
    fx_issue = evidence_issue(fx.get("evidence"), data_kind, "fx", query_date)
    if data_kind == "live" and fx["as_of"] != query_date and fx_issue is None:
        fx_issue = "fx:rate_not_as_of_query_date"
    api_prices = index_items(data.get("api_prices"), "id", "api_prices")
    for ident, price in api_prices.items():
        model_id(price.get("model_id"), f"api_prices.{ident}.model_id")
        string(price.get("currency"), f"api_prices.{ident}.currency")
        bucket_numbers(price.get("per_million"), f"api_prices.{ident}.per_million", nullable=True)
        if not isinstance(price.get("batch"), bool):
            raise InputError(f"api_prices.{ident}.batch must be boolean")
        integer(price.get("context_min", 0), f"api_prices.{ident}.context_min")
        if price.get("context_max") is not None:
            integer(price["context_max"], f"api_prices.{ident}.context_max", 1)
    scenarios = index_items(data.get("conversion_scenarios", []), "id", "conversion_scenarios")
    for ident, scenario in scenarios.items():
        model_id(scenario.get("model_id"), f"conversion_scenarios.{ident}.model_id")
        string(scenario.get("api_price_id"), f"conversion_scenarios.{ident}.api_price_id")
        scenario["per_operation"] = bucket_numbers(
            scenario.get("per_operation"),
            f"conversion_scenarios.{ident}.per_operation", integer_values=True
        )
        if not any(scenario["per_operation"].values()):
            raise InputError(f"conversion_scenarios.{ident}.per_operation cannot be all zero")
        integer(scenario.get("context_tokens"), f"conversion_scenarios.{ident}.context_tokens")
        if not isinstance(scenario.get("batch"), bool):
            raise InputError(f"conversion_scenarios.{ident}.batch must be boolean")
        if scenario.get("basis") not in ("official_usage", "assumption"):
            raise InputError(f"conversion_scenarios.{ident}.basis must be official_usage or assumption")
        string(scenario.get("label"), f"conversion_scenarios.{ident}.label")
    plans = index_items(data.get("plans"), "id", "plans")
    pool_ids = set()
    for ident, plan in plans.items():
        for forbidden in ("billing_regime", "upgrade_from"):
            if forbidden in plan:
                raise InputError(f"plans.{ident}.{forbidden} is obsolete in current-plan schema")
        for key in ("provider", "product", "tier", "region"):
            string(plan.get(key), f"plans.{ident}.{key}")
        availability = obj(plan.get("availability"), f"plans.{ident}.availability")
        string(availability.get("status"), f"plans.{ident}.availability.status")
        obj(plan.get("price"), f"plans.{ident}.price")
        if plan.get("access") is not None:
            access = obj(plan["access"], f"plans.{ident}.access")
            if "clients" in access:
                for client in array(access["clients"], f"plans.{ident}.access.clients"):
                    string(client, f"plans.{ident}.access.clients[]")
            if access.get("api_access") is not None and not isinstance(access["api_access"], bool):
                raise InputError(f"plans.{ident}.access.api_access must be boolean or null")
        if plan.get("limits") is not None:
            limits = obj(plan["limits"], f"plans.{ident}.limits")
            for key in ("rate_limit", "fair_use", "overage"):
                if limits.get(key) is not None:
                    string(limits[key], f"plans.{ident}.limits.{key}")
            if limits.get("concurrency") is not None:
                integer(limits["concurrency"], f"plans.{ident}.limits.concurrency")
        pools = array(plan.get("pools"), f"plans.{ident}.pools")
        if not pools and plan.get("estimate_bundle") is None and not plan.get("empirical_observations"):
            raise InputError(f"plans.{ident}.pools must not be empty without an estimate bundle or empirical observation")
        if plan.get("estimate_bundle") is not None and plan.get("empirical_observations"):
            raise InputError(f"plans.{ident} cannot combine alternative bundle and raw observations")
        for pool in pools:
            pool = obj(pool, f"plans.{ident}.pool")
            pool_id = string(pool.get("id"), "pool.id")
            if pool_id in pool_ids:
                raise InputError(f"pool.id must be globally unique: {pool_id}")
            pool_ids.add(pool_id)
            if pool.get("entitlement_class") not in ("guaranteed", "conditional", "promotional"):
                raise InputError(f"pool.{pool_id}.entitlement_class is required")
            if pool.get("unit") not in ("requests", "credits", "weighted_tokens", "currency", "token_buckets"):
                raise InputError(f"pool.{pool_id}.unit is invalid")
            quota = obj(pool.get("quota"), f"pool.{pool_id}.quota")
            if pool["unit"] == "currency":
                string(quota.get("currency"), f"pool.{pool_id}.quota.currency")
            cap_window(pool, f"pool.{pool_id}")
            cap_ids = set()
            for cap in array(pool.get("additional_caps", []), f"pool.{pool_id}.additional_caps"):
                cap = obj(cap, f"pool.{pool_id}.additional_cap")
                cap_id = string(cap.get("id"), f"pool.{pool_id}.additional_cap.id")
                if cap_id in cap_ids:
                    raise InputError(f"duplicate additional cap in pool {pool_id}: {cap_id}")
                cap_ids.add(cap_id)
                if cap.get("unit", pool["unit"]) != pool["unit"]:
                    raise InputError(f"additional_cap.{cap_id}.unit must match its pool")
                cap_window(cap, f"additional_cap.{cap_id}")
            rules = array(pool.get("rules"), f"pool.{pool_id}.rules")
            if not rules:
                raise InputError(f"pool.{pool_id}.rules must not be empty")
            mids = set()
            for rule in rules:
                rule = obj(rule, f"pool.{pool_id}.rule")
                mid = model_id(rule.get("model_id"), f"pool.{pool_id}.rule.model_id")
                if rule.get("api_price_id") is None:
                    compatible_prices = [price_id for price_id, api_price in api_prices.items()
                                         if api_price["model_id"] == mid]
                    if len(compatible_prices) != 1:
                        raise InputError(
                            f"pool.{pool_id}.rule.api_price_id is required when "
                            f"{mid} has {len(compatible_prices)} API price rows"
                        )
                    rule["api_price_id"] = compatible_prices[0]
                string(rule.get("api_price_id"), f"pool.{pool_id}.rule.api_price_id")
                if is_direct_entitlement(pool, rule):
                    if pool["unit"] == "token_buckets" and rule.get("basis") != "token_buckets":
                        raise InputError(f"pool.{pool_id}.rule.basis must be token_buckets")
                    if pool["unit"] == "currency" and rule.get("basis") != "api_value":
                        raise InputError(f"pool.{pool_id}.rule.basis must be api_value")
                if mid in mids:
                    raise InputError(f"duplicate model rule in pool {pool_id}: {mid}")
                mids.add(mid)
    return data_kind, query_date, rates, fx_issue, api_prices, scenarios, plans


def ranking_row(row):
    return {
        "plan_id": row["plan_id"], "tier": row["tier"], "model_id": row["model_id"],
        "scenario_id": row["scenario_id"], "api_price_id": row["api_price_id"],
        "component_pool_ids": row["component_pool_ids"],
        "monthly_api_value_usd": row["monthly_api_value_usd"],
        "renewal_monthly_cost_usd": row["monthly_cost"]["renewal_monthly_usd"],
        "roi_renewal": row["roi_renewal"], "value_kind": row["value_kind"],
        "renewal_monthly_listed_usd": row["monthly_cost"]["renewal_monthly_listed_usd"],
        "roi_renewal_listed": row["roi_renewal_listed"],
        "evidence_grade": row["evidence_grade"],
        "shared_pool_alternatives": row["shared_pool_alternatives"],
    }


def rankings(evaluations):
    def ordered(metric):
        eligible = [row for row in evaluations if row["status"] == "valued"
                    and row[metric] is not None]
        groups = {}
        for row in eligible:
            key = (row["model_id"], row["api_price_id"], row["scenario_id"])
            groups.setdefault(key, []).append(row)
        same_model = []
        for key, rows in sorted(groups.items(), key=lambda item: (
            item[0][0], item[0][1], item[0][2] or ""
        )):
            if len(rows) < 2:
                continue
            rows.sort(key=lambda row: (-row[metric], row["plan_id"]))
            same_model.append({
                "model_id": key[0], "api_price_id": key[1], "scenario_id": key[2],
                "rows": [ranking_row(row) for row in rows],
            })
        own = sorted(eligible, key=lambda row: (-row[metric], row["plan_id"], row["model_id"]))
        return same_model, [ranking_row(row) for row in own]

    exact_same, exact_own = ordered("roi_renewal")
    listed_same, listed_own = ordered("roi_renewal_listed")
    return {
        "same_model": exact_same, "own_api_value": exact_own,
        "listed_price_same_model": listed_same,
        "listed_price_own_api_value": listed_own,
    }


def estimate_confidence(row):
    if row["status"] != "estimated":
        return "insufficient"
    classes = set(row["source_classes"])
    if row["category"] == "mixed_model_bundle" or classes.intersection(
        {"empirical_current", "stale_empirical", "explicit_assumption", "theoretical_window"}
    ):
        return "low"
    if row["category"] == "exact_model" and (
        row["scenario_id"].startswith("direct:") or all(
            component.get("api_parity_credit_usd") is not None
            for component in row["components"]
        )
    ):
        return "high"
    return "medium"


def estimated_rankings(rows, plans):
    for row in rows:
        row["confidence"] = estimate_confidence(row)
    eligible = [row for row in rows if row["status"] == "estimated"
                and row["roi_renewal_listed"]["base"] is not None]
    exact_groups = {}
    for row in eligible:
        if row["category"] != "exact_model":
            continue
        key = (row["model_id"], row["api_price_id"], row["scenario_id"])
        exact_groups.setdefault(key, []).append(row)
    same = []
    for key, group in sorted(exact_groups.items(), key=lambda item: (
        item[0][0], item[0][1], item[0][2] or ""
    )):
        if len(group) < 2:
            continue
        group.sort(key=lambda row: (-row["roi_renewal_listed"]["base"], row["plan_id"]))
        same.append({"model_id": key[0], "api_price_id": key[1],
                     "scenario_id": key[2], "rows": group})
    own = sorted((row for row in eligible if row["category"] == "exact_model"), key=lambda row: (
        -row["roi_renewal_listed"]["base"], row["plan_id"],
        row["model_id"] or ""
    ))
    mixed = sorted((row for row in eligible if row["category"] == "mixed_model_bundle"),
                   key=lambda row: (-row["roi_renewal_listed"]["base"], row["plan_id"]))
    by_plan = {}
    for row in rows:
        by_plan.setdefault(row["plan_id"], []).append(row)
    total = []
    omitted = []
    for plan in plans.values():
        reference = plan.get("representative_scenario_id")
        if reference is None:
            omitted.append({"plan_id": plan["id"], "reason": "representative_scenario_id_missing"})
            continue
        string(reference, f"plans.{plan['id']}.representative_scenario_id")
        candidates = [row for row in by_plan.get(plan["id"], [])
                      if row["scenario_id"] == reference]
        if len(candidates) != 1:
            omitted.append({"plan_id": plan["id"],
                            "reason": "representative_scenario_id_not_unique_or_missing"})
            continue
        selected = candidates[0]
        if selected not in eligible:
            omitted.append({"plan_id": plan["id"],
                            "reason": "representative_scenario_unrankable"})
            continue
        total.append({"plan_id": plan["id"], "representative": selected,
                      "other_scenario_ids": sorted({row["scenario_id"]
                                                    for row in by_plan[plan["id"]]
                                                    if row is not selected})})
    total.sort(key=lambda item: (-item["representative"]["roi_renewal_listed"]["base"],
                                 item["plan_id"]))
    return {"estimated_same_model": same, "estimated_own_api_value": own,
            "estimated_mixed_bundle": mixed,
            "estimated_total_plan_value": total,
            "estimated_total_plan_omissions": omitted,
            "ranking_basis": "base estimate divided by current quoted renewal price"}


def unrank_partial_plan_value(row, reason):
    row["status"] = "unranked"
    row["value_kind"] = "unvalued"
    row["evidence_grade"] = "insufficient"
    add_issue(row["reasons"], reason)
    for field in ("monthly_api_value_usd", "monthly_api_value_upper_usd", "roi_initial",
                  "roi_renewal", "roi_initial_upper", "roi_renewal_upper",
                  "roi_initial_listed", "roi_renewal_listed",
                  "roi_initial_listed_upper", "roi_renewal_listed_upper",
                  "monthly_api_value_cny", "monthly_api_value_upper_cny"):
        if field in row:
            row[field] = None


def analyze(data, today=None):
    data_kind, query_date, rates, fx_issue, api_prices, scenarios, plans = validate(data, today)
    evaluations = []
    estimated_evaluations = []
    for plan in plans.values():
        converted_models = {
            rule["model_id"] for pool in plan["pools"] for rule in pool["rules"]
            if not is_direct_entitlement(pool, rule)
            and pool["entitlement_class"] == "guaranteed"
        }
        direct_keys = {
            (rule["model_id"], rule["api_price_id"])
            for pool in plan["pools"] for rule in pool["rules"]
            if is_direct_entitlement(pool, rule)
        }
        converted_estimate_keys = {
            (rule["model_id"], rule["api_price_id"])
            for pool in plan["pools"] for rule in pool["rules"]
            if not is_direct_entitlement(pool, rule)
        }
        for mid, price_id in sorted(direct_keys):
            if mid in converted_models:
                continue
            direct_scenario = {
                "id": None, "model_id": mid, "api_price_id": price_id,
                "basis": "direct_entitlement", "label": "Published entitlement face value",
                "per_operation": {bucket: 0 for bucket in BUCKETS},
            }
            row = evaluate_plan_scenario(
                plan, direct_scenario, api_prices, rates, data_kind,
                query_date, fx_issue, direct=True
            )
            if row is not None:
                evaluations.append(row)
            if (mid, price_id) not in converted_estimate_keys:
                estimated = evaluate_estimated_plan_scenario(
                    plan, direct_scenario, api_prices, rates, data_kind,
                    query_date, fx_issue, direct=True
                )
                if estimated is not None:
                    estimated_evaluations.append(estimated)
        for scenario in scenarios.values():
            row = evaluate_plan_scenario(
                plan, scenario, api_prices, rates, data_kind, query_date, fx_issue
            )
            if row is not None:
                evaluations.append(row)
            estimated = evaluate_estimated_plan_scenario(
                plan, scenario, api_prices, rates, data_kind, query_date, fx_issue
            )
            if estimated is not None:
                estimated_evaluations.append(estimated)
        bundle_row = evaluate_estimate_bundle(
            plan, rates, data_kind, query_date, fx_issue
        )
        if bundle_row is not None:
            estimated_evaluations.append(bundle_row)
        for observation in array(plan.get("empirical_observations", []),
                                 f"plans.{plan['id']}.empirical_observations"):
            estimated_evaluations.append(evaluate_empirical_observation(
                plan, observation, api_prices, rates, data_kind, query_date, fx_issue
            ))
        direct_prices_by_model = {}
        for pool in plan["pools"]:
            if pool["entitlement_class"] != "guaranteed":
                continue
            for rule in pool["rules"]:
                if is_direct_entitlement(pool, rule):
                    direct_prices_by_model.setdefault(rule["model_id"], set()).add(
                        rule["api_price_id"]
                    )
        for row in evaluations:
            if row["plan_id"] != plan["id"]:
                continue
            prices = direct_prices_by_model.get(row["model_id"], set())
            if prices and prices != {row["api_price_id"]}:
                unrank_partial_plan_value(row, "incompatible_direct_api_price_ids_not_aggregated")
        covered = {row["model_id"] for row in evaluations
                   if row["plan_id"] == plan["id"] and row["scenario_id"] is not None}
        offered = {rule["model_id"] for pool in plan["pools"] for rule in pool["rules"]
                   if not is_direct_entitlement(pool, rule)}
        for mid in sorted(offered - covered):
            cost, cost_issues = monthly_cost(plan["price"], rates, data_kind, query_date)
            evaluations.append({
                "plan_id": plan["id"], "provider": plan["provider"], "product": plan["product"],
                "tier": plan["tier"], "region": plan["region"],
                "availability": plan["availability"], "model_id": mid,
                "scenario_id": None, "scenario_basis": None, "scenario_label": None,
                "api_price_id": None, "status": "unranked",
                "reasons": [
                    "conversion_scenario_missing" if mid in converted_models
                    else "no_guaranteed_eligible_pool"
                ] + cost_issues,
                "value_kind": "unvalued", "evidence_grade": "insufficient",
                "api_value_per_operation_usd": None, "window_api_value_usd_by_pool": {},
                "monthly_api_value_usd": None, "monthly_api_value_upper_usd": None,
                "monthly_cost": cost, "roi_initial": None, "roi_renewal": None,
                "roi_initial_upper": None, "roi_renewal_upper": None,
                "roi_initial_listed": None, "roi_renewal_listed": None,
                "roi_initial_listed_upper": None, "roi_renewal_listed_upper": None,
                "component_pool_ids": [
                    pool["id"] for pool in plan["pools"]
                    if pool["entitlement_class"] == "guaranteed"
                    and any(rule["model_id"] == mid for rule in pool["rules"])
                ],
                "pools": [], "excluded_pools": [], "shared_pool_alternatives": {},
                "access": plan.get("access"), "limits": plan.get("limits"),
            })
    return {
        "schema_version": 2, "data_kind": data_kind, "query_date": query_date,
        "fx_as_of": data["fx"]["as_of"], "evaluations": evaluations,
        "estimated_evaluations": estimated_evaluations,
        "rankings": {**rankings(evaluations), **estimated_rankings(estimated_evaluations, plans)},
        "notes": [
            "API equivalent is replacement cost, not cash back or equal model quality.",
            "Assumption-based operation mixes are technical conversion scenarios.",
            "Rows using one shared pool for different models are mutually exclusive, not additive.",
            "Estimated short-window values are named sensitivity scenarios, not measured monthly capacity.",
            "Mixed-model source-reported weekly API values are separate from strict same-model comparisons.",
            "Main plan ranking uses one explicit representative scenario per plan; alternatives are not summed.",
            "Low/base/high are assumption sensitivity values, not statistical confidence intervals.",
            "Listed-price ratios assume the published quote without unverified checkout adjustments; exact paid-cost ratios require tax terms.",
        ],
    }


def jsonable(value):
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, dict):
        return {key: jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [jsonable(item) for item in value]
    return value


def markdown(result):
    fmt = lambda value: "unknown" if value is None else format(value, ".4f")
    rows = [
        f"# Current plan API-equivalent value ({result['data_kind']}, {result['query_date']})",
        "", "API equivalent is replacement cost; model quality is not normalized.",
        "Exact paid-cost ROI requires verified checkout tax terms. Listed-price ROI uses the published quote without unverified checkout adjustments.",
        "Low/base/high are explicit sensitivity assumptions, not statistical intervals or personal utilization.",
        "", "## Estimated current total plan value (representative scenarios)", "",
        "One explicitly selected scenario per plan; other model uses of a shared pool are alternatives. Ratios are conditional on the current listed renewal price.", "",
        "| Rank | Plan | Category | Model / scenario | Monthly API USD low / base / high | Listed-price ROI low / base / high | Evidence | Confidence |",
        "| ---: | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for rank, item in enumerate(result["rankings"]["estimated_total_plan_value"], 1):
        row = item["representative"]
        model = row["model_id"] or "mixed models"
        values = " / ".join(fmt(row["monthly_api_value_usd"][level]) for level in LEVELS)
        ratios = " / ".join(fmt(row["roi_renewal_listed"][level]) for level in LEVELS)
        rows.append(f"| {rank} | {row['plan_id']} | {row['category']} | "
                    f"{model} · {row['scenario_id']} | {values} | {ratios} | "
                    f"{', '.join(row['source_classes'])} | {row['confidence']} |")
    if not result["rankings"]["estimated_total_plan_value"]:
        rows.append("| — | No rankable representative scenario | — | — | — | — | — | — |")
    rows.extend(("", "## Estimated same exact model", "",
                 "Only identical canonical model, API tariff row, and conversion scenario share a comparison group.", ""))
    if not result["rankings"]["estimated_same_model"]:
        rows.extend(("No comparable exact-model pair.", ""))
    for group in result["rankings"]["estimated_same_model"]:
        rows.extend((f"### {group['model_id']} · {group['api_price_id']} · {group['scenario_id']}", "",
                     "| Rank | Plan | API USD low / base / high | Conditional ROI low / base / high | Confidence |",
                     "| ---: | --- | --- | --- | --- |"))
        for rank, row in enumerate(group["rows"], 1):
            values = " / ".join(fmt(row["monthly_api_value_usd"][level]) for level in LEVELS)
            ratios = " / ".join(fmt(row["roi_renewal_listed"][level]) for level in LEVELS)
            rows.append(f"| {rank} | {row['plan_id']} | {values} | {ratios} | {row['confidence']} |")
        rows.append("")
    rows.extend(("## Estimated own-model API value", "",
                 "Each row uses its own maker API price; cross-model dollars do not imply equal capability.", "",
                 "| Rank | Plan | Model | Scenario | API USD low / base / high | Conditional ROI base | Confidence |",
                 "| ---: | --- | --- | --- | --- | ---: | --- |"))
    for rank, row in enumerate(result["rankings"]["estimated_own_api_value"], 1):
        values = " / ".join(fmt(row["monthly_api_value_usd"][level]) for level in LEVELS)
        rows.append(f"| {rank} | {row['plan_id']} | {row['model_id']} | {row['scenario_id']} | "
                    f"{values} | {fmt(row['roi_renewal_listed']['base'])} | {row['confidence']} |")
    if not result["rankings"]["estimated_own_api_value"]:
        rows.append("| — | No rankable exact-model estimate | — | — | — | — | — |")
    rows.extend(("", "## Estimated mixed-model bundles", "",
                 "Source-reported weekly API value is converted to monthly by stated window counts; it is not a single-model tariff comparison.", "",
                 "| Rank | Plan | Interactive API USD base | Separate API credit USD base | Total API USD low / base / high | Conditional ROI base | Evidence |",
                 "| ---: | --- | ---: | ---: | --- | ---: | --- |"))
    for rank, row in enumerate(result["rankings"]["estimated_mixed_bundle"], 1):
        components = row["components"]
        values = " / ".join(fmt(row["monthly_api_value_usd"][level]) for level in LEVELS)
        rows.append(f"| {rank} | {row['plan_id']} | "
                    f"{fmt(components['interactive_mixed_usd']['base'])} | "
                    f"{fmt(components['api_credit_usd']['base'])} | {values} | "
                    f"{fmt(row['roi_renewal_listed']['base'])} | {', '.join(row['source_classes'])} |")
    if not result["rankings"]["estimated_mixed_bundle"]:
        rows.append("| — | No rankable mixed-model observation | — | — | — | — | — |")
    rows.extend(("", "## Estimated exclusions", "",
                 "| Plan | Scenario | Reason |", "| --- | --- | --- |"))
    for row in result["estimated_evaluations"]:
        if row["status"] != "estimated":
            rows.append(f"| {row['plan_id']} | {row['scenario_id']} | "
                        f"{', '.join(row['reasons']) or 'unknown'} |")
    for item in result["rankings"]["estimated_total_plan_omissions"]:
        rows.append(f"| {item['plan_id']} | representative | {item['reason']} |")
    rows.extend(("", "## Guaranteed/direct audit", "",
                 "The following v2 audit uses only guaranteed directly monthly convertible entitlement.",
                 "", "## Same model ranking", ""))
    if not result["rankings"]["same_model"]:
        rows.extend(("No comparable pair with the same exact model, API price, and conversion scenario.", ""))
    for group in result["rankings"]["same_model"]:
        label = group["scenario_id"] or "direct entitlement"
        rows.extend((f"### {group['model_id']} · {group['api_price_id']} · {label}", "",
                     "| Rank | Plan | Monthly API USD | Renewal ROI | Basis |",
                     "| ---: | --- | ---: | ---: | --- |"))
        for rank, row in enumerate(group["rows"], 1):
            rows.append(f"| {rank} | {row['plan_id']} | {fmt(row['monthly_api_value_usd'])} | "
                        f"{fmt(row['roi_renewal'])} | {row['value_kind']} |")
        rows.append("")
    rows.extend(("## Own API value ranking", "",
                 "Each model uses its own official API price; values do not imply equal capability.", "",
                 "| Rank | Plan | Model | Conversion | Monthly API USD | Renewal ROI | Basis |",
                 "| ---: | --- | --- | --- | ---: | ---: | --- |"))
    for rank, row in enumerate(result["rankings"]["own_api_value"], 1):
        rows.append(f"| {rank} | {row['plan_id']} | {row['model_id']} | "
                    f"{row['scenario_id'] or 'direct entitlement'} | "
                    f"{fmt(row['monthly_api_value_usd'])} | {fmt(row['roi_renewal'])} | "
                    f"{row['value_kind']} |")
    if not result["rankings"]["own_api_value"]:
        rows.append("| — | No rankable monthly entitlement | — | — | — | — | — |")
    rows.extend(("", "## Listed-price conditional same model ranking", "",
                 "Ratios use the published subscription quote; actual payment and tax may differ.", ""))
    if not result["rankings"]["listed_price_same_model"]:
        rows.extend(("No comparable pair with a verified listed price and monthly API equivalent.", ""))
    for group in result["rankings"]["listed_price_same_model"]:
        label = group["scenario_id"] or "direct entitlement"
        rows.extend((f"### {group['model_id']} · {group['api_price_id']} · {label}", "",
                     "| Rank | Plan | Monthly API USD | Listed renewal USD/month | Conditional ROI | Basis |",
                     "| ---: | --- | ---: | ---: | ---: | --- |"))
        for rank, row in enumerate(group["rows"], 1):
            rows.append(f"| {rank} | {row['plan_id']} | {fmt(row['monthly_api_value_usd'])} | "
                        f"{fmt(row['renewal_monthly_listed_usd'])} | "
                        f"{fmt(row['roi_renewal_listed'])} | {row['value_kind']} |")
        rows.append("")
    rows.extend(("## Listed-price conditional own API value ranking", "",
                 "Each model uses its own maker API price; different models are not quality-equivalent.", "",
                 "| Rank | Plan | Model | Conversion | Monthly API USD | Listed renewal USD/month | Conditional ROI | Basis |",
                 "| ---: | --- | --- | --- | ---: | ---: | ---: | --- |"))
    for rank, row in enumerate(result["rankings"]["listed_price_own_api_value"], 1):
        rows.append(f"| {rank} | {row['plan_id']} | {row['model_id']} | "
                    f"{row['scenario_id'] or 'direct entitlement'} | "
                    f"{fmt(row['monthly_api_value_usd'])} | "
                    f"{fmt(row['renewal_monthly_listed_usd'])} | "
                    f"{fmt(row['roi_renewal_listed'])} | {row['value_kind']} |")
    if not result["rankings"]["listed_price_own_api_value"]:
        rows.append("| — | No conditional monthly rank | — | — | — | — | — | — |")
    rows.extend(("", "## Bounded and unranked diagnostics", "",
                 "Short-window upper bounds are not part of the sorted rankings.", "",
                 "| Plan | Model | Status | Monthly API USD | Monthly upper USD | Listed-price ROI upper | Window USD by pool | Reason |",
                 "| --- | --- | --- | ---: | ---: | ---: | --- | --- |"))
    for row in result["evaluations"]:
        if row["status"] == "valued" and (
            row["roi_renewal"] is not None or row["roi_renewal_listed"] is not None
        ):
            continue
        windows = ", ".join(f"{key}: {fmt(value)}" for key, value in
                            row["window_api_value_usd_by_pool"].items()) or "unknown"
        rows.append("| " + " | ".join((
            row["plan_id"], row["model_id"], row["status"],
            fmt(row["monthly_api_value_usd"]),
            fmt(row["monthly_api_value_upper_usd"]),
            fmt(row["roi_renewal_listed_upper"]), windows,
            ", ".join(row["reasons"]) or "none",
        )) + " |")
    rows.extend(("", "Shared-pool model alternatives are mutually exclusive.", ""))
    return "\n".join(rows)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON snapshot of current on-sale plans")
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
