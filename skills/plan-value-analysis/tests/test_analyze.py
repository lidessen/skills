"""Invented fixtures exercise deterministic plan entitlement valuation, not market facts."""

import copy
import importlib.util
import json
import tempfile
import unittest
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "analyze.py"
SPEC = importlib.util.spec_from_file_location("plan_value_analyze", SCRIPT)
calculator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(calculator)

MODEL = "fictional/alpha@1.0#standard"
OTHER = "fictional/beta@2.0#standard"
SOURCE = {"status": "synthetic"}


def base():
    return {
        "schema_version": 2,
        "data_kind": "synthetic",
        "query_date": "2026-10-21",
        "fx": {"as_of": "2026-10-21", "per_usd": {"USD": "1", "CNY": "7"}, "evidence": SOURCE},
        "api_prices": [
            {"id": "alpha-standard", "model_id": MODEL, "currency": "USD",
             "per_million": {"input": "1", "output": "0", "cache_read": "0", "cache_write": "0"},
             "context_min": 0, "context_max": None, "batch": False, "evidence": SOURCE}
        ],
        "conversion_scenarios": [
            {"id": "generic-operation", "model_id": MODEL, "api_price_id": "alpha-standard",
             "per_operation": {"input": 10000, "output": 0, "cache_read": 0, "cache_write": 0},
             "context_tokens": 10000, "batch": False, "basis": "assumption",
             "label": "Fictional reference operation; not a subscriber's activity"}
        ],
        "plans": [
            {"id": "basic", "provider": "Fictional", "product": "Code", "tier": "Basic",
             "region": "Test", "availability": {"status": "on_sale", "evidence": SOURCE},
             "price": {"currency": "USD", "months": 1, "initial": "10", "renewal": "10",
                       "tax_rate": "0", "tax_included": True, "evidence": SOURCE},
             "access": {"clients": ["Fictional editor"], "api_access": False, "evidence": SOURCE},
             "limits": {"rate_limit": None, "concurrency": None, "fair_use": None,
                        "overage": None, "evidence": SOURCE},
             "pools": [
                 {"id": "basic-pool", "unit": "requests", "entitlement_class": "guaranteed",
                  "quota": {"amount": "100", "evidence": SOURCE}, "window": {"kind": "monthly"},
                  "rules": [{"model_id": MODEL, "api_price_id": "alpha-standard",
                             "basis": "request", "units_per_operation": "1",
                             "evidence": SOURCE}]}
             ]}
        ]
    }


def evaluation(data, plan_id="basic", model=MODEL, today=None):
    result = calculator.analyze(data, today=today)
    return next(item for item in result["evaluations"]
                if item["plan_id"] == plan_id and item["model_id"] == model)


def add_second_plan(data):
    plan = copy.deepcopy(data["plans"][0])
    plan["id"] = "plus"
    plan["tier"] = "Plus"
    plan["pools"][0]["id"] = "plus-pool"
    data["plans"].append(plan)


def mark_live(data, fetched_at="2026-10-21"):
    verified = {"status": "verified", "url": "https://example.test/current",
                "fetched_at": fetched_at, "excerpt": "Fictional test terms"}
    data["data_kind"] = "live"
    data["query_date"] = fetched_at
    data["fx"]["as_of"] = fetched_at
    data["fx"]["evidence"] = verified
    data["api_prices"][0]["evidence"] = verified
    plan = data["plans"][0]
    for field in ("availability", "price", "access", "limits"):
        plan[field]["evidence"] = verified
    plan["pools"][0]["quota"]["evidence"] = verified
    plan["pools"][0]["rules"][0]["evidence"] = verified
    return verified


def estimate_source(kind="official_current", match="exact"):
    source = {"class": kind, "url": "https://example.test/current-estimate",
              "fetched_at": "2026-10-21", "model_match": match,
              "assumptions": {"low": "low sensitivity", "base": "current central scenario",
                              "high": "high sensitivity"}}
    if kind in ("empirical_current", "stale_empirical"):
        source["observed_at"] = "2026-10-20"
    return source


def estimated(data, plan_id="basic"):
    return next(row for row in calculator.analyze(data)["estimated_evaluations"]
                if row["plan_id"] == plan_id)


class PlanValueTests(unittest.TestCase):
    def test_monthly_plan_has_api_equivalent_and_cost_ratio_only(self):
        result = calculator.analyze(base())
        found = result["evaluations"][0]
        self.assertEqual(found["status"], "valued")
        self.assertEqual(found["monthly_api_value_usd"], Decimal("1"))
        self.assertEqual(found["roi_renewal"], Decimal("0.1"))
        self.assertEqual(len(result["rankings"]["own_api_value"]), 1)
        for removed in ("realized", "portfolio_analysis", "upgrades"):
            self.assertNotIn(removed, result)
        self.assertNotIn("realized_value_usd", found)

    def test_disjoint_cache_buckets_are_priced_once(self):
        data = base()
        data["api_prices"][0]["per_million"] = {
            "input": "2", "output": "8", "cache_read": "0.2", "cache_write": "2.5"}
        data["conversion_scenarios"][0]["per_operation"] = {
            "input": 1_000_000, "output": 250_000, "cache_read": 500_000, "cache_write": 100_000}
        pool = data["plans"][0]["pools"][0]
        pool.update(unit="token_buckets",
                    quota={"amounts": {"input": 1_000_000, "output": 250_000,
                                       "cache_read": 500_000, "cache_write": 100_000},
                           "evidence": SOURCE},
                    rules=[{"model_id": MODEL, "basis": "token_buckets",
                            "api_price_id": "alpha-standard", "evidence": SOURCE}])
        found = evaluation(data)
        self.assertEqual(found["monthly_api_value_usd"], Decimal("4.35"))
        self.assertEqual(found["value_kind"], "bucket_face_value")

    def test_missing_cache_bucket_is_validation_error(self):
        data = base()
        del data["conversion_scenarios"][0]["per_operation"]["cache_read"]
        with self.assertRaisesRegex(calculator.InputError, "cache tokens are separate"):
            calculator.analyze(data)

    def test_token_bucket_multiplier_reduces_face_value(self):
        data = base()
        pool = data["plans"][0]["pools"][0]
        pool.update(unit="token_buckets",
                    quota={"amounts": {"input": 1_000_000, "output": 0,
                                       "cache_read": 0, "cache_write": 0}, "evidence": SOURCE},
                    rules=[{"model_id": MODEL, "basis": "token_buckets",
                            "api_price_id": "alpha-standard", "multiplier": "2", "evidence": SOURCE}])
        self.assertEqual(evaluation(data)["monthly_api_value_usd"], Decimal("0.5"))

    def test_credit_multiplier_and_fractional_remainder(self):
        data = base()
        pool = data["plans"][0]["pools"][0]
        pool["unit"] = "credits"
        pool["quota"]["amount"] = "101"
        pool["rules"][0]["multiplier"] = "2"
        found = evaluation(data)
        self.assertEqual(found["monthly_api_value_usd"], Decimal("0.50"))
        self.assertEqual(found["value_kind"], "assumption_conversion")

    def test_weighted_tokens_use_each_bucket_once(self):
        data = base()
        data["conversion_scenarios"][0]["per_operation"] = {
            "input": 1_000_000, "output": 250_000, "cache_read": 500_000, "cache_write": 100_000}
        pool = data["plans"][0]["pools"][0]
        pool["unit"] = "weighted_tokens"
        pool["quota"]["amount"] = "10"
        pool["rules"][0] = {
            "model_id": MODEL, "api_price_id": "alpha-standard",
            "basis": "weighted_tokens", "multiplier": "2",
            "per_million": {"input": "1", "output": "2", "cache_read": "0.5", "cache_write": "2.5"},
            "evidence": SOURCE}
        self.assertEqual(evaluation(data)["monthly_api_value_usd"], Decimal("2"))

    def test_annual_promo_renewal_tax_and_foreign_exchange(self):
        data = base()
        data["plans"][0]["price"].update(
            currency="CNY", months=12, initial="120", renewal="720",
            tax_rate="0.1", tax_included=False)
        found = evaluation(data)
        self.assertEqual(found["monthly_cost"]["initial_monthly_original"], Decimal("11"))
        self.assertEqual(found["monthly_cost"]["renewal_monthly_original"], Decimal("66"))
        self.assertEqual(found["monthly_cost"]["initial_monthly_usd"], Decimal(11) / 7)
        self.assertEqual(found["monthly_cost"]["renewal_monthly_usd"], Decimal(66) / 7)
        self.assertNotEqual(found["roi_initial"], found["roi_renewal"])

    def test_currency_pool_converts_its_own_balance(self):
        data = base()
        pool = data["plans"][0]["pools"][0]
        pool["unit"] = "currency"
        pool["quota"].update(amount="7", currency="CNY")
        pool["rules"][0] = {"model_id": MODEL, "basis": "api_value",
                            "api_price_id": "alpha-standard", "evidence": SOURCE}
        self.assertEqual(evaluation(data)["monthly_api_value_usd"], Decimal("1"))

    def test_direct_token_buckets_need_no_operation_mix_and_group_by_model(self):
        data = base()
        data["conversion_scenarios"] = []
        pool = data["plans"][0]["pools"][0]
        pool.update(unit="token_buckets",
                    quota={"amounts": {"input": 1_000_000, "output": 0,
                                       "cache_read": 0, "cache_write": 0}, "evidence": SOURCE},
                    rules=[{"model_id": MODEL, "basis": "token_buckets",
                            "api_price_id": "alpha-standard", "evidence": SOURCE}])
        add_second_plan(data)
        data["plans"][1]["price"]["renewal"] = "15"
        data["plans"][1]["pools"][0]["quota"]["amounts"]["input"] = 2_000_000
        result = calculator.analyze(data)
        self.assertEqual(len(result["evaluations"]), 2)
        self.assertEqual(evaluation(data)["monthly_api_value_usd"], Decimal("1"))
        self.assertEqual(evaluation(data, "plus")["monthly_api_value_usd"], Decimal("2"))
        self.assertEqual(result["rankings"]["same_model"][0]["rows"][0]["plan_id"], "plus")
        self.assertEqual(result["evaluations"][0]["value_kind"], "bucket_face_value")

    def test_direct_currency_api_balance_is_continuous_not_operation_floored(self):
        data = base()
        data["conversion_scenarios"] = []
        pool = data["plans"][0]["pools"][0]
        pool["unit"] = "currency"
        pool["quota"].update(amount="1", currency="USD")
        pool["rules"] = [{"model_id": MODEL, "basis": "api_value",
                          "api_price_id": "alpha-standard", "evidence": SOURCE}]
        add_second_plan(data)
        data["plans"][1]["price"]["renewal"] = "15"
        data["plans"][1]["pools"][0]["quota"]["amount"] = "2"
        result = calculator.analyze(data)
        self.assertEqual(evaluation(data)["monthly_api_value_usd"], Decimal("1"))
        self.assertEqual(evaluation(data, "plus")["monthly_api_value_usd"], Decimal("2"))
        self.assertEqual(result["evaluations"][0]["value_kind"], "api_spend_face_value")
        self.assertEqual(result["rankings"]["same_model"][0]["rows"][0]["plan_id"], "plus")

    def test_shared_pool_models_are_alternative_uses_not_additive(self):
        data = base()
        data["api_prices"].append({
            **copy.deepcopy(data["api_prices"][0]), "id": "beta-standard", "model_id": OTHER,
            "per_million": {"input": "2", "output": "0", "cache_read": "0", "cache_write": "0"}})
        data["conversion_scenarios"].append({
            **copy.deepcopy(data["conversion_scenarios"][0]),
            "id": "other-operation", "model_id": OTHER, "api_price_id": "beta-standard"})
        pool = data["plans"][0]["pools"][0]
        pool["unit"] = "credits"
        pool["rules"].append({"model_id": OTHER, "api_price_id": "beta-standard",
                              "basis": "request",
                              "units_per_operation": "2", "evidence": SOURCE})
        result = calculator.analyze(data)
        self.assertEqual(len(result["evaluations"]), 2)
        self.assertEqual(evaluation(data, model=MODEL)["monthly_api_value_usd"], Decimal("1"))
        self.assertEqual(evaluation(data, model=OTHER)["monthly_api_value_usd"], Decimal("1"))
        self.assertNotIn("total_plan_value_usd", result)
        self.assertIn("basic-pool", result["evaluations"][0]["shared_pool_alternatives"])
        self.assertEqual(result["rankings"]["same_model"], [])

    def test_same_model_regional_api_prices_do_not_cross_apply(self):
        data = base()
        data["api_prices"].append({
            **copy.deepcopy(data["api_prices"][0]), "id": "alpha-cny",
            "currency": "CNY",
            "per_million": {"input": "14", "output": "0",
                            "cache_read": "0", "cache_write": "0"}})
        data["conversion_scenarios"].append({
            **copy.deepcopy(data["conversion_scenarios"][0]),
            "id": "generic-cny", "api_price_id": "alpha-cny"})
        add_second_plan(data)
        data["plans"][1]["region"] = "Other market"
        data["plans"][1]["price"].update(currency="CNY", initial="70", renewal="70")
        data["plans"][1]["pools"][0]["rules"][0]["api_price_id"] = "alpha-cny"
        result = calculator.analyze(data)
        self.assertEqual(len(result["evaluations"]), 2)
        by_plan = {row["plan_id"]: row for row in result["evaluations"]}
        self.assertEqual(by_plan["basic"]["api_price_id"], "alpha-standard")
        self.assertEqual(by_plan["basic"]["monthly_api_value_usd"], Decimal("1"))
        self.assertEqual(by_plan["plus"]["api_price_id"], "alpha-cny")
        self.assertEqual(by_plan["plus"]["monthly_api_value_usd"], Decimal("2"))

    def test_older_single_price_rule_can_infer_id_but_ambiguous_prices_reject(self):
        data = base()
        del data["plans"][0]["pools"][0]["rules"][0]["api_price_id"]
        self.assertEqual(evaluation(data)["monthly_api_value_usd"], Decimal("1"))
        data = base()
        del data["plans"][0]["pools"][0]["rules"][0]["api_price_id"]
        data["api_prices"].append({
            **copy.deepcopy(data["api_prices"][0]), "id": "alpha-other"})
        with self.assertRaisesRegex(calculator.InputError, "api_price_id is required"):
            calculator.analyze(data)

    def test_weekly_reset_may_be_subscription_anchored_or_unknown(self):
        for reset in ("subscription_anchor", "unknown"):
            with self.subTest(reset=reset):
                data = base()
                data["plans"][0]["pools"][0]["window"] = {
                    "kind": "weekly", "reset": reset}
                found = evaluation(data)
                self.assertEqual(found["status"], "unranked")
                self.assertIsNotNone(found["window_api_value_usd_by_pool"])

    def test_independent_request_pools_are_one_whole_plan_value(self):
        data = base()
        second = copy.deepcopy(data["plans"][0]["pools"][0])
        second["id"] = "second-pool"
        data["plans"][0]["pools"].append(second)
        result = calculator.analyze(data)
        valued = [item for item in result["evaluations"] if item["status"] == "valued"]
        self.assertEqual(len(valued), 1)
        self.assertEqual(valued[0]["monthly_api_value_usd"], Decimal("2"))
        self.assertEqual(valued[0]["roi_renewal"], Decimal("0.2"))
        self.assertEqual(len(result["rankings"]["own_api_value"]), 1)

    def test_independent_direct_pools_share_one_subscription_denominator(self):
        data = base()
        data["conversion_scenarios"] = []
        pool = data["plans"][0]["pools"][0]
        pool.update(unit="token_buckets",
                    quota={"amounts": {"input": 1_000_000, "output": 0,
                                       "cache_read": 0, "cache_write": 0}, "evidence": SOURCE},
                    rules=[{"model_id": MODEL, "basis": "token_buckets",
                            "api_price_id": "alpha-standard", "evidence": SOURCE}])
        second = copy.deepcopy(pool)
        second["id"] = "second-pool"
        second["quota"]["amounts"]["input"] = 2_000_000
        data["plans"][0]["pools"].append(second)
        result = calculator.analyze(data)
        valued = [item for item in result["evaluations"] if item["status"] == "valued"]
        self.assertEqual(len(valued), 1)
        self.assertEqual(valued[0]["monthly_api_value_usd"], Decimal("3"))
        self.assertEqual(valued[0]["roi_renewal"], Decimal("0.3"))

    def test_compatible_direct_and_conversion_pools_form_one_whole_plan_roi(self):
        data = base()
        direct = copy.deepcopy(data["plans"][0]["pools"][0])
        direct.update(id="direct-pool", unit="token_buckets",
                      quota={"amounts": {"input": 1_000_000, "output": 0,
                                         "cache_read": 0, "cache_write": 0}, "evidence": SOURCE},
                      rules=[{"model_id": MODEL, "basis": "token_buckets",
                              "api_price_id": "alpha-standard", "evidence": SOURCE}])
        data["plans"][0]["pools"].append(direct)
        result = calculator.analyze(data)
        rows = [item for item in result["evaluations"] if item["plan_id"] == "basic"
                and item["model_id"] == MODEL]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "valued")
        self.assertEqual(rows[0]["monthly_api_value_usd"], Decimal("2"))
        self.assertEqual(rows[0]["roi_renewal"], Decimal("0.2"))
        self.assertEqual(rows[0]["value_kind"], "mixed_direct_and_operation_conversion")
        self.assertEqual(len(result["rankings"]["own_api_value"]), 1)
        data["api_prices"].append({**copy.deepcopy(data["api_prices"][0]),
                                    "id": "different-api-price"})
        direct["rules"][0]["api_price_id"] = "different-api-price"
        conflicting = calculator.analyze(data)
        self.assertEqual(conflicting["rankings"]["own_api_value"], [])
        self.assertTrue(all(item["status"] == "unranked"
                            for item in conflicting["evaluations"] if item["model_id"] == MODEL))

    def test_same_exact_model_tiers_remain_independent_rows(self):
        data = base()
        add_second_plan(data)
        data["plans"][1]["price"]["renewal"] = "15"
        data["plans"][1]["pools"][0]["quota"]["amount"] = "200"
        result = calculator.analyze(data)
        self.assertEqual(len(result["evaluations"]), 2)
        self.assertEqual(len(result["rankings"]["same_model"]), 1)
        self.assertEqual(result["rankings"]["same_model"][0]["rows"][0]["plan_id"], "plus")
        self.assertNotIn("upgrades", result)
        self.assertEqual(evaluation(data, "plus")["monthly_api_value_usd"], Decimal("2"))

    def test_missing_conversion_scenario_stays_unranked(self):
        data = base()
        data["conversion_scenarios"] = []
        result = calculator.analyze(data)
        self.assertEqual(result["evaluations"][0]["status"], "unranked")
        self.assertIn("conversion_scenario_missing", result["evaluations"][0]["reasons"])
        self.assertEqual(result["rankings"]["own_api_value"], [])

    def test_rolling_quota_alone_has_no_monthly_rank_or_roi(self):
        data = base()
        data["plans"][0]["pools"][0]["window"] = {"kind": "rolling_hours", "hours": 5}
        found = evaluation(data)
        self.assertEqual(found["status"], "unranked")
        self.assertEqual(found["window_api_value_usd_by_pool"]["basic-pool"], Decimal("1"))
        self.assertIsNone(found["monthly_api_value_usd"])
        self.assertIsNone(found["roi_renewal"])
        self.assertEqual(calculator.analyze(data)["rankings"]["own_api_value"], [])
        self.assertNotIn("active_windows_per_month", json.dumps(data))

    def test_monthly_cap_on_rolling_pool_is_only_unranked_upper_bound(self):
        data = base()
        pool = data["plans"][0]["pools"][0]
        pool["window"] = {"kind": "rolling_hours", "hours": 5}
        pool["additional_caps"] = [
            {"id": "month", "amount": "250", "window": {"kind": "monthly"}, "evidence": SOURCE}]
        found = evaluation(data)
        self.assertEqual(found["status"], "upper_bound")
        self.assertEqual(found["value_kind"], "monthly_cap_upper_bound")
        self.assertIsNone(found["monthly_api_value_usd"])
        self.assertIsNotNone(found["monthly_api_value_upper_usd"])
        self.assertIsNone(found["roi_renewal"])
        self.assertIsNotNone(found["roi_renewal_upper"])
        self.assertEqual(calculator.analyze(data)["rankings"]["own_api_value"], [])
        reason = "nonmonthly_window_makes_monthly_value_upper_bound"
        self.assertIn(reason, found["reasons"])
        diagnostics = calculator.markdown(calculator.analyze(data)).split(
            "## Bounded and unranked diagnostics", 1)[1]
        self.assertIn(reason, diagnostics)

    def test_monthly_pool_with_extra_short_cap_is_upper_bound(self):
        data = base()
        pool = data["plans"][0]["pools"][0]
        pool["additional_caps"] = [
            {"id": "short", "amount": "20",
             "window": {"kind": "rolling_hours", "hours": 5}, "evidence": SOURCE}]
        found = evaluation(data)
        self.assertEqual(found["status"], "upper_bound")
        self.assertIsNone(found["monthly_api_value_usd"])
        self.assertEqual(calculator.analyze(data)["rankings"]["own_api_value"], [])

    def test_unknown_conflicting_or_off_sale_plans_do_not_rank(self):
        for status in ("undisclosed", "conflicting", "estimated"):
            with self.subTest(quota_status=status):
                data = base()
                data["plans"][0]["pools"][0]["quota"] = {
                    "amount": None, "evidence": {"status": status}}
                self.assertEqual(evaluation(data)["status"], "unranked")
                self.assertEqual(calculator.analyze(data)["rankings"]["own_api_value"], [])
        data = base()
        data["plans"][0]["availability"]["status"] = "off_sale"
        self.assertNotEqual(evaluation(data)["status"], "valued")
        self.assertEqual(calculator.analyze(data)["rankings"]["own_api_value"], [])

    def test_unknown_debit_rule_stays_unranked_instead_of_becoming_zero(self):
        for edit in ("request_units", "multiplier", "weighted_input_rate"):
            with self.subTest(edit=edit):
                data = base()
                pool = data["plans"][0]["pools"][0]
                rule = pool["rules"][0]
                if edit == "request_units":
                    rule["units_per_operation"] = None
                elif edit == "multiplier":
                    rule["multiplier"] = None
                else:
                    pool["unit"] = "credits"
                    rule["basis"] = "weighted_tokens"
                    del rule["units_per_operation"]
                    rule["per_million"] = {
                        "input": None, "output": "0", "cache_read": "0", "cache_write": "0"}
                found = evaluation(data)
                self.assertEqual(found["status"], "unranked")
                self.assertTrue(any(reason.endswith("debit_unknown")
                                    for reason in found["reasons"]))
                self.assertEqual(calculator.analyze(data)["rankings"]["own_api_value"], [])

    def test_live_input_requires_verified_current_offer_evidence(self):
        data = base()
        data["data_kind"] = "live"
        test_day = date(2026, 10, 21)
        self.assertEqual(evaluation(data, today=test_day)["status"], "unranked")
        verified = mark_live(data)
        self.assertEqual(evaluation(data, today=test_day)["status"], "valued")
        data["api_prices"][0]["evidence"] = {**verified, "fetched_at": "2026-10-20"}
        self.assertEqual(evaluation(data, today=test_day)["status"], "unranked")
        data["api_prices"][0]["evidence"] = verified
        data["plans"][0]["price"]["evidence"] = {"status": "conflicting"}
        found = evaluation(data, today=test_day)
        self.assertEqual(found["status"], "valued")
        self.assertEqual(found["monthly_api_value_usd"], Decimal("1"))
        self.assertIsNone(found["roi_renewal"])
        self.assertIsNone(found["roi_renewal_listed"])
        data["plans"][0]["price"]["evidence"] = verified
        data["plans"][0]["availability"]["evidence"] = {"status": "unavailable"}
        self.assertEqual(evaluation(data, today=test_day)["status"], "unranked")

    def test_live_snapshot_from_old_query_day_cannot_rank_as_current(self):
        data = base()
        mark_live(data, fetched_at="2000-01-01")
        with self.assertRaisesRegex(calculator.InputError, "query_date must equal"):
            calculator.analyze(data, today=date(2026, 10, 21))

    def test_live_cross_currency_uses_current_fx_observation_date(self):
        data = base()
        mark_live(data)
        data["plans"][0]["price"]["currency"] = "CNY"
        data["fx"]["as_of"] = "2026-10-20"
        found = evaluation(data, today=date(2026, 10, 21))
        self.assertEqual(found["status"], "valued")
        self.assertEqual(found["monthly_api_value_usd"], Decimal("1"))
        self.assertIsNone(found["roi_renewal"])
        self.assertIsNone(found["roi_renewal_listed"])
        self.assertEqual(calculator.analyze(data, today=date(2026, 10, 21))
                         ["rankings"]["own_api_value"], [])

    def test_exact_model_mode_and_price_tier_are_checked(self):
        data = base()
        data["api_prices"][0]["batch"] = True
        self.assertIn("api_price_batch_mismatch", evaluation(data)["reasons"])
        data["api_prices"][0]["batch"] = False
        data["api_prices"][0]["context_max"] = 10000
        self.assertIn("api_price_context_mismatch", evaluation(data)["reasons"])
        data["conversion_scenarios"][0]["model_id"] = "fictional/alpha@latest#standard"
        with self.assertRaisesRegex(calculator.InputError, "mutable alias"):
            calculator.analyze(data)

    def test_unknown_tax_is_not_zero_and_zero_cost_has_no_infinite_roi(self):
        data = base()
        data["plans"][0]["price"]["tax_rate"] = None
        data["plans"][0]["price"]["tax_included"] = None
        found = evaluation(data)
        self.assertEqual(found["status"], "valued")
        self.assertEqual(found["monthly_api_value_usd"], Decimal("1"))
        self.assertEqual(found["monthly_cost"]["renewal_monthly_listed_usd"], Decimal("10"))
        self.assertIsNone(found["monthly_cost"]["renewal_monthly_usd"])
        self.assertIsNone(found["roi_renewal"])
        self.assertEqual(found["roi_renewal_listed"], Decimal("0.1"))
        self.assertIn("tax_terms_unknown", found["reasons"])
        result = calculator.analyze(data)
        self.assertEqual(result["rankings"]["own_api_value"], [])
        self.assertEqual(len(result["rankings"]["listed_price_own_api_value"]), 1)
        data = base()
        data["plans"][0]["price"]["initial"] = "0"
        data["plans"][0]["price"]["renewal"] = "0"
        found = evaluation(data)
        self.assertIsNone(found["roi_renewal"])
        self.assertIsNone(found["roi_renewal_listed"])
        self.assertEqual(calculator.analyze(data)["rankings"]["own_api_value"], [])

    def test_unknown_initial_cost_does_not_hide_known_renewal(self):
        data = base()
        data["plans"][0]["price"].update(initial=None, tax_rate=None, tax_included=None)
        found = evaluation(data)
        self.assertEqual(found["status"], "valued")
        self.assertEqual(found["monthly_api_value_usd"], Decimal("1"))
        self.assertIsNone(found["roi_initial"])
        self.assertIsNone(found["roi_initial_listed"])
        self.assertIsNone(found["roi_renewal"])
        self.assertEqual(found["roi_renewal_listed"], Decimal("0.1"))
        self.assertIn("initial_cost_unknown", found["reasons"])
        self.assertEqual(len(calculator.analyze(data)["rankings"]
                             ["listed_price_own_api_value"]), 1)

    def test_valued_entitlement_with_unknown_renewal_is_visible_in_diagnostics(self):
        data = base()
        data["plans"][0]["price"].update(initial=None, renewal=None,
                                           tax_rate=None, tax_included=None)
        result = calculator.analyze(data)
        found = result["evaluations"][0]
        self.assertEqual(found["monthly_api_value_usd"], Decimal("1"))
        self.assertIsNone(found["roi_renewal_listed"])
        self.assertEqual(result["rankings"]["listed_price_own_api_value"], [])
        diagnostics = calculator.markdown(result).split("## Bounded and unranked diagnostics", 1)[1]
        self.assertIn("basic", diagnostics)
        self.assertIn("| valued | 1.0000 | unknown |", diagnostics)
        self.assertIn("renewal_cost_unknown", diagnostics)

    def test_live_tax_unknown_keeps_only_conditional_rank_and_excludes_bad_price(self):
        data = base()
        mark_live(data)
        add_second_plan(data)
        data["plans"][0]["price"].update(tax_rate=None, tax_included=None)
        data["plans"][1]["price"].update(tax_rate=None, tax_included=None,
                                           renewal="20")
        result = calculator.analyze(data, today=date(2026, 10, 21))
        self.assertEqual(result["rankings"]["same_model"], [])
        self.assertEqual([row["plan_id"] for row in result["rankings"]
                          ["listed_price_same_model"][0]["rows"]], ["basic", "plus"])
        self.assertEqual(result["rankings"]["listed_price_own_api_value"][0]
                         ["roi_renewal_listed"], Decimal("0.1"))
        rendered = calculator.markdown(result)
        self.assertIn("Listed-price conditional same model ranking", rendered)
        self.assertIn("actual payment and tax may differ", rendered)
        data["plans"][0]["price"]["evidence"] = {"status": "conflicting"}
        invalid = calculator.analyze(data, today=date(2026, 10, 21))
        self.assertEqual(invalid["rankings"]["listed_price_same_model"], [])
        self.assertEqual([row["plan_id"] for row in invalid["rankings"]
                          ["listed_price_own_api_value"]], ["plus"])

    def test_short_window_remains_upper_bound_with_unknown_tax(self):
        data = base()
        data["plans"][0]["price"].update(tax_rate=None, tax_included=None)
        data["plans"][0]["pools"][0]["additional_caps"] = [
            {"id": "five-hour", "amount": "20",
             "window": {"kind": "rolling_hours", "hours": 5}, "evidence": SOURCE}]
        found = evaluation(data)
        self.assertEqual(found["status"], "upper_bound")
        self.assertIsNone(found["roi_renewal_upper"])
        self.assertEqual(found["roi_renewal_listed_upper"], Decimal("0.1"))
        self.assertEqual(calculator.analyze(data)["rankings"]["listed_price_own_api_value"], [])

    def test_cli_renders_json_and_table_without_removed_views(self):
        data = base()
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "input.json"
            out = Path(temp) / "output.json"
            table = Path(temp) / "table.md"
            path.write_text(json.dumps(data), encoding="utf-8")
            self.assertEqual(calculator.main([str(path), "--output", str(out), "--markdown", str(table)]), 0)
            output = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(output["schema_version"], 2)
            self.assertNotIn("portfolio_analysis", output)
            rendered = table.read_text(encoding="utf-8").lower()
            self.assertNotIn("realized", rendered)
            self.assertNotIn("portfolio", rendered)

    def test_markdown_ranks_are_sorted_and_diagnostics_separate(self):
        data = base()
        add_second_plan(data)
        data["plans"][1]["price"]["renewal"] = "30"
        data["plans"][1]["pools"][0]["quota"]["amount"] = "200"
        rolling = copy.deepcopy(data["plans"][0])
        rolling["id"] = "rolling"
        rolling["pools"][0]["id"] = "rolling-pool"
        rolling["pools"][0]["window"] = {"kind": "rolling_hours", "hours": 5}
        data["plans"] = [rolling, data["plans"][1], data["plans"][0]]
        rendered = calculator.markdown(calculator.analyze(data))
        same_title = "## Same model ranking"
        own_title = "## Own API value ranking"
        diagnostics_title = "## Bounded and unranked diagnostics"
        self.assertLess(rendered.index(same_title), rendered.index(own_title))
        self.assertLess(rendered.index(own_title), rendered.index(diagnostics_title))
        same = rendered.split(same_title, 1)[1].split(own_title, 1)[0]
        own = rendered.split(own_title, 1)[1].split(diagnostics_title, 1)[0]
        diagnostics = rendered.split(diagnostics_title, 1)[1]
        self.assertLess(same.index("basic"), same.index("plus"))
        self.assertLess(own.index("basic"), own.index("plus"))
        self.assertNotIn("rolling", same)
        self.assertNotIn("rolling", own)
        self.assertIn("rolling", diagnostics)

    def test_current_additive_flex_and_exact_api_parity_have_no_operation_rounding(self):
        data = base()
        plan = data["plans"][0]
        data["conversion_scenarios"] = []
        plan["representative_scenario_id"] = f"direct:{MODEL}"
        stable = plan["pools"][0]
        stable["id"] = "stable"
        stable["unit"] = "credits"
        stable["quota"]["amount"] = "1000"
        stable["rules"][0] = {
            "model_id": MODEL, "api_price_id": "alpha-standard", "basis": "weighted_tokens",
            "per_million": {"input": "100", "output": "0", "cache_read": "0", "cache_write": "0"},
            "api_parity_credit_usd": "0.01", "api_parity_evidence": SOURCE,
            "evidence": SOURCE,
        }
        extra = copy.deepcopy(stable)
        extra["id"] = "flex"
        extra["entitlement_class"] = "conditional"
        extra["quota"]["amount"] = "500"
        extra["estimate"] = {
            "source": estimate_source(), "presence": {"low": "0", "base": "1", "high": "1"},
            "additive_to": ["stable"], "stacking_evidence": SOURCE,
        }
        plan["pools"].append(extra)
        result = calculator.analyze(data)
        row = result["estimated_evaluations"][0]
        self.assertEqual(row["monthly_api_value_usd"], {
            "low": Decimal("10"), "base": Decimal("15"), "high": Decimal("15")})
        self.assertEqual(row["roi_renewal_listed"]["base"], Decimal("1.5"))
        self.assertEqual(result["rankings"]["estimated_total_plan_value"][0]
                         ["representative"]["scenario_id"], f"direct:{MODEL}")
        self.assertEqual(row["confidence"], "high")
        self.assertEqual(result["evaluations"][0]["monthly_api_value_usd"], Decimal("10"))
        del extra["estimate"]["stacking_evidence"]
        self.assertEqual(estimated(data)["status"], "unranked")
        extra["estimate"]["stacking_evidence"] = SOURCE
        stable["rules"][0]["per_million"]["input"] = "99"
        self.assertIn("credit_to_maker_api_tariff_parity_not_proven",
                      estimated(data)["reasons"][0])

    def test_bonus_must_prove_additive_against_every_component(self):
        data = base()
        plan = data["plans"][0]
        for ident in ("stable-b", "stable-c"):
            pool = copy.deepcopy(plan["pools"][0])
            pool["id"] = ident
            plan["pools"].append(pool)
        extra = copy.deepcopy(plan["pools"][0])
        extra["id"] = "extra"
        extra["entitlement_class"] = "promotional"
        extra["estimate"] = {"source": estimate_source(match="not_applicable"),
                             "presence": {"low": "0", "base": "1", "high": "1"},
                             "additive_to": ["basic-pool"], "stacking_evidence": SOURCE}
        plan["pools"].append(extra)
        self.assertEqual(estimated(data)["status"], "unranked")
        extra["estimate"]["additive_to"] = ["basic-pool", "stable-b", "stable-c"]
        self.assertEqual(estimated(data)["monthly_api_value_usd"]["base"], Decimal("4"))

    def test_short_window_sensitivity_intersects_caps_without_claiming_guarantee(self):
        data = base()
        pool = data["plans"][0]["pools"][0]
        pool["window"] = {"kind": "rolling_hours", "hours": 5}
        pool["additional_caps"] = [
            {"id": "week", "amount": "250", "window": {"kind": "weekly", "reset": "rolling"},
             "evidence": SOURCE}]
        pool["estimate"] = {"source": estimate_source("theoretical_window"),
                            "window_counts": {"primary": {"low": "4", "base": "8", "high": "12"},
                                              "week": {"low": "1", "base": "2", "high": "2"}}}
        row = estimated(data)
        self.assertEqual(row["monthly_api_value_usd"], {
            "low": Decimal("2.5"), "base": Decimal("5"), "high": Decimal("5")})
        self.assertEqual(row["confidence"], "low")
        pool["estimate"]["source"]["class"] = "official_current"
        self.assertEqual(estimated(data)["status"], "unranked")

    def test_source_reported_mixed_bundle_is_separate_and_api_credit_independent(self):
        data = base()
        plan = data["plans"][0]
        plan["pools"] = []
        plan["representative_scenario_id"] = "mixed-weekly"
        plan["estimate_bundle"] = {
            "id": "mixed-weekly", "source": estimate_source("empirical_current", "not_applicable"),
            "weekly_api_value_usd": {"low": "100", "base": "125", "high": "150"},
            "monthly_window_counts": {"low": "4", "base": "4", "high": "4"},
            "api_credit": {"monthly_usd": "10", "presence": {"low": "0", "base": "1", "high": "1"},
                           "source": estimate_source("official_current", "not_applicable"),
                           "independence_evidence": SOURCE},
        }
        result = calculator.analyze(data)
        row = result["estimated_evaluations"][0]
        self.assertEqual(row["monthly_api_value_usd"], {
            "low": Decimal("400"), "base": Decimal("510"), "high": Decimal("610")})
        self.assertEqual(result["rankings"]["estimated_same_model"], [])
        self.assertEqual(result["rankings"]["estimated_own_api_value"], [])
        self.assertEqual(result["rankings"]["estimated_mixed_bundle"][0]["plan_id"], "basic")
        self.assertEqual(result["rankings"]["estimated_total_plan_value"][0]
                         ["representative"]["category"], "mixed_model_bundle")

    def test_raw_meter_observation_prices_disjoint_buckets_and_explicit_projection(self):
        data = base()
        plan = data["plans"][0]
        plan["pools"] = []
        plan["representative_scenario_id"] = "meter-week"
        plan["empirical_observations"] = [{
            "id": "meter-week", "model_id": MODEL, "api_price_id": "alpha-standard",
            "source": estimate_source("empirical_current"),
            "token_buckets": {"input": 1_000_000, "output": 0, "cache_read": 0,
                              "cache_write": 0},
            "accounts": 1, "extra_usage": False, "window_kind": "weekly",
            "meter_start": "0", "meter_end": "0.5", "exhausted": False,
            "linear_meter_projection": True,
            "value_basis": {"low": "observed", "base": "projected", "high": "projected"},
            "monthly_window_counts": {"low": "4", "base": "4", "high": "5"},
            "context_tokens": 10000, "batch": False,
        }]
        row = estimated(data)
        self.assertEqual(row["components"]["observed_window_api_usd"], Decimal("1"))
        self.assertEqual(row["components"]["projected_full_window_api_usd"], Decimal("2"))
        self.assertEqual(row["monthly_api_value_usd"], {
            "low": Decimal("4"), "base": Decimal("8"), "high": Decimal("10")})
        plan["empirical_observations"][0]["linear_meter_projection"] = False
        with self.assertRaisesRegex(calculator.InputError, "needs linear_meter_projection"):
            calculator.analyze(data)

    def test_main_ranking_omits_plan_without_explicit_representative(self):
        data = base()
        result = calculator.analyze(data)
        self.assertEqual(result["rankings"]["estimated_total_plan_value"], [])
        self.assertEqual(result["rankings"]["estimated_total_plan_omissions"][0]["reason"],
                         "representative_scenario_id_missing")

    def test_direct_estimate_uses_stable_reference_id_without_changing_audit_id(self):
        data = base()
        data["conversion_scenarios"] = []
        pool = data["plans"][0]["pools"][0]
        pool["unit"] = "currency"
        pool["quota"] = {"amount": "7", "currency": "CNY", "evidence": SOURCE}
        pool["rules"] = [{"model_id": MODEL, "api_price_id": "alpha-standard",
                          "basis": "api_value", "evidence": SOURCE}]
        data["plans"][0]["representative_scenario_id"] = f"direct:{MODEL}"
        result = calculator.analyze(data)
        self.assertIsNone(result["evaluations"][0]["scenario_id"])
        self.assertEqual(result["estimated_evaluations"][0]["scenario_id"], f"direct:{MODEL}")
        self.assertEqual(result["rankings"]["estimated_total_plan_value"][0]["plan_id"],
                         "basic")

    def test_partial_unknown_token_bucket_estimate_stays_unranked(self):
        data = base()
        data["conversion_scenarios"] = []
        pool = data["plans"][0]["pools"][0]
        pool["unit"] = "token_buckets"
        pool["quota"] = {"amounts": {"input": None, "output": 0, "cache_read": 0,
                                     "cache_write": 0}, "evidence": SOURCE}
        pool["rules"] = [{"model_id": MODEL, "api_price_id": "alpha-standard",
                          "basis": "token_buckets", "evidence": SOURCE}]
        row = estimated(data)
        self.assertEqual(row["status"], "unranked")
        self.assertIn("pool:basic-pool:quota_anchor_missing", row["reasons"])

    def test_explicit_query_timezone_uses_that_date_and_rejects_invalid_zone(self):
        data = base()
        mark_live(data)
        data["query_timezone"] = "Etc/UTC"
        instant = datetime(2026, 10, 21, 17, 38, tzinfo=timezone.utc)
        self.assertEqual(calculator.analyze(data, today=instant)["query_date"], "2026-10-21")
        data["query_timezone"] = "Asia/Shanghai"
        with self.assertRaisesRegex(calculator.InputError, "query_timezone"):
            calculator.analyze(data, today=instant)
        data["query_timezone"] = "No/Such_Zone"
        with self.assertRaisesRegex(calculator.InputError, "valid IANA timezone"):
            calculator.analyze(data, today=instant)


if __name__ == "__main__":
    unittest.main()
