"""Behavior tests use invented prices and entitlements, never current provider facts."""

import copy
import importlib.util
import json
import tempfile
import unittest
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
        "schema_version": 1, "data_kind": "synthetic", "period_days": 30,
        "fx": {"as_of": "2026-01-01", "per_usd": {"USD": "1", "CNY": "7"}, "evidence": SOURCE},
        "api_prices": [{"id": "alpha-standard", "model_id": MODEL, "currency": "USD",
                        "per_million": {"input": "1", "output": "0", "cache_read": "0", "cache_write": "0"},
                        "context_min": 0, "context_max": None, "batch": False, "evidence": SOURCE}],
        "workloads": [{"id": "coding", "model_id": MODEL, "api_price_id": "alpha-standard",
                       "requests_per_month": 100, "per_request": {"input": 10000, "output": 0,
                                                                 "cache_read": 0, "cache_write": 0},
                       "context_tokens": 10000, "batch": False, "basis": "scenario",
                       "label": "Invented coding request with measured-style token shape"}],
        "plans": [{"id": "basic", "provider": "Fictional", "product": "Code", "tier": "Basic",
                   "region": "Test", "billing_regime": "fixed requests",
                   "price": {"currency": "USD", "months": 1, "initial": "10", "renewal": "10",
                             "tax_rate": "0", "tax_included": True, "evidence": SOURCE},
                   "pools": [{"id": "basic-pool", "unit": "requests", "entitlement_class": "guaranteed",
                              "quota": {"amount": "100", "evidence": SOURCE},
                              "window": {"kind": "monthly"},
                              "rules": [{"model_id": MODEL, "basis": "request", "units_per_request": "1",
                                         "evidence": SOURCE}]}]}]}


def row(data, plan_id="basic", model=MODEL):
    result = calculator.analyze(data)
    return next(item for item in result["evaluations"] if item["plan_id"] == plan_id
                and item["model_id"] == model)


class PlanValueTests(unittest.TestCase):
    def test_token_buckets_and_cache_are_exclusive(self):
        data = base()
        data["api_prices"][0]["per_million"] = {"input": "2", "output": "8", "cache_read": "0.2",
                                                  "cache_write": "2.5"}
        data["workloads"][0]["per_request"] = {"input": 1_000_000, "output": 250_000,
                                               "cache_read": 500_000, "cache_write": 100_000}
        data["workloads"][0]["requests_per_month"] = 1
        data["plans"][0]["pools"][0] = {"id": "basic-pool", "unit": "token_buckets",
                                           "entitlement_class": "guaranteed",
                                           "quota": {"amounts": {"input": 1_000_000, "output": 250_000,
                                                                 "cache_read": 500_000, "cache_write": 100_000},
                                                     "evidence": SOURCE},
                                           "window": {"kind": "monthly"},
                                           "rules": [{"model_id": MODEL, "basis": "token_buckets", "evidence": SOURCE}]}
        found = row(data)
        self.assertEqual(found["api_value_per_request_usd"], Decimal("4.35"))
        self.assertEqual(found["entitlement_value_per_window_usd"], Decimal("4.35"))
        self.assertEqual(found["realized_value_usd"], Decimal("4.35"))

    def test_token_bucket_multiplier_reduces_physical_capacity_and_face_value(self):
        data = base()
        pool = data["plans"][0]["pools"][0]
        pool["unit"] = "token_buckets"
        pool["quota"] = {"amounts": {"input": 1_000_000, "output": 0, "cache_read": 0,
                                      "cache_write": 0}, "evidence": SOURCE}
        pool["rules"][0] = {"model_id": MODEL, "basis": "token_buckets", "multiplier": "2",
                            "evidence": SOURCE}
        found = row(data)
        self.assertEqual(found["reachable_requests"], 50)
        self.assertEqual(found["entitlement_value_per_window_usd"], Decimal("0.5"))

    def test_missing_bucket_is_rejected_instead_of_double_billing(self):
        data = base()
        del data["workloads"][0]["per_request"]["cache_read"]
        with self.assertRaisesRegex(calculator.InputError, "cache tokens are separate"):
            calculator.analyze(data)

    def test_credit_multiplier_and_fractional_remainder(self):
        data = base()
        pool = data["plans"][0]["pools"][0]
        pool["unit"] = "credits"
        pool["quota"]["amount"] = "101"
        pool["rules"][0]["multiplier"] = "2"
        found = row(data)
        self.assertEqual(found["reachable_requests"], 50)
        self.assertEqual(found["reachable_value_usd"], Decimal("0.50"))

    def test_weighted_token_debit_uses_each_bucket_once(self):
        data = base()
        data["workloads"][0]["per_request"] = {"input": 1_000_000, "output": 250_000,
                                               "cache_read": 500_000, "cache_write": 100_000}
        pool = data["plans"][0]["pools"][0]
        pool["unit"] = "weighted_tokens"
        pool["quota"]["amount"] = "10"
        pool["rules"][0] = {"model_id": MODEL, "basis": "weighted_tokens", "multiplier": "2",
                            "per_million": {"input": "1", "output": "2", "cache_read": "0.5",
                                            "cache_write": "2.5"}, "evidence": SOURCE}
        # Per request: (1 + .5 + .25 + .25) * 2 = 4 debit units.
        self.assertEqual(row(data)["reachable_requests"], 2)

    def test_currency_yearly_promo_renewal_and_tax(self):
        data = base()
        price = data["plans"][0]["price"]
        price.update(currency="CNY", months=12, initial="120", renewal="720", tax_rate="0.1",
                     tax_included=False)
        found = row(data)
        self.assertEqual(found["monthly_cost"]["initial_monthly_original"], Decimal("11"))
        self.assertEqual(found["monthly_cost"]["renewal_monthly_original"], Decimal("66"))
        self.assertEqual(found["monthly_cost"]["initial_monthly_usd"], Decimal(11) / 7)
        self.assertEqual(found["monthly_cost"]["renewal_monthly_usd"], Decimal(66) / 7)
        self.assertNotEqual(found["reachable_roi_initial"], found["reachable_roi_renewal"])

    def test_currency_credit_pool_uses_own_fx(self):
        data = base()
        pool = data["plans"][0]["pools"][0]
        pool["unit"] = "currency"
        pool["quota"].update(amount="7", currency="CNY")
        pool["rules"][0] = {"model_id": MODEL, "basis": "api_value", "evidence": SOURCE}
        found = row(data)
        self.assertEqual(found["reachable_requests"], 100)
        self.assertEqual(found["reachable_value_usd"], Decimal("1.00"))

    def test_rolling_window_requires_activity_and_caps_by_demand_and_days(self):
        data = base()
        workload = data["workloads"][0]
        workload["requests_per_month"] = 2100
        workload["active_windows_per_month"] = {"basic-pool": 30}
        workload["active_days_per_month"] = 30
        pool = data["plans"][0]["pools"][0]
        pool["window"] = {"kind": "rolling_hours", "hours": 5}
        pool["daily_cap_requests"] = 50
        found = row(data)
        self.assertEqual(found["pools"][0]["capacity_requests_per_window"], 100)
        self.assertEqual(found["reachable_requests"], 1500)
        self.assertEqual(found["realized_requests"], 1500)
        del workload["active_windows_per_month"]
        found = row(data)
        self.assertEqual(found["status"], "unranked")
        self.assertIsNone(found["reachable_value_usd"])
        self.assertTrue(any("active_windows_missing" in issue for issue in found["reasons"]))

    def test_simultaneous_rolling_weekly_monthly_caps_intersect(self):
        data = base()
        workload = data["workloads"][0]
        workload["requests_per_month"] = 2100
        workload["active_windows_per_month"] = {"basic-pool": 30, "basic-pool:weekly": 5}
        pool = data["plans"][0]["pools"][0]
        pool["window"] = {"kind": "rolling_hours", "hours": 5}
        pool["additional_caps"] = [
            {"id": "weekly", "amount": "300", "window": {"kind": "weekly"}, "evidence": SOURCE},
            {"id": "monthly", "amount": "1200", "window": {"kind": "monthly"}, "evidence": SOURCE},
        ]
        found = row(data)
        self.assertEqual(found["pools"][0]["capacity_requests_per_window"], 100)
        self.assertEqual(found["reachable_requests"], 1200)  # min(3000, 1500, 1200)
        self.assertEqual(found["realized_requests"], 1200)
        self.assertEqual(found["reachable_bound_kind"], "active_window_capacity_upper_bound")
        self.assertEqual(found["value_bounds_usd"]["realized_lower"], Decimal(0))

    def test_shared_pool_alternatives_not_added(self):
        data = base()
        data["api_prices"].append({**copy.deepcopy(data["api_prices"][0]), "id": "beta-standard",
                                   "model_id": OTHER,
                                   "per_million": {"input": "2", "output": "0", "cache_read": "0", "cache_write": "0"}})
        data["workloads"].append({**copy.deepcopy(data["workloads"][0]), "id": "other-coding",
                                  "model_id": OTHER, "api_price_id": "beta-standard"})
        pool = data["plans"][0]["pools"][0]
        pool["unit"] = "credits"
        pool["rules"].append({"model_id": OTHER, "basis": "request", "units_per_request": "2",
                              "evidence": SOURCE})
        result = calculator.analyze(data)
        self.assertEqual(len(result["evaluations"]), 2)
        self.assertEqual(row(data, model=MODEL)["reachable_value_usd"], Decimal("1"))
        self.assertEqual(row(data, model=OTHER)["reachable_value_usd"], Decimal("1"))
        self.assertIn("basic-pool", result["evaluations"][0]["shared_pool_alternatives"])
        self.assertNotIn("total_plan_value_usd", result)

    def test_independent_pools_share_one_demand(self):
        data = base()
        data["workloads"][0]["requests_per_month"] = 60
        first = data["plans"][0]["pools"][0]
        first["quota"]["amount"] = "50"
        second = copy.deepcopy(first)
        second["id"] = "second-pool"
        data["plans"][0]["pools"].append(second)
        found = row(data)
        self.assertEqual(found["reachable_requests"], 100)
        self.assertEqual(found["realized_requests"], 60)
        self.assertEqual(found["effective_utilization"], Decimal("0.6"))

    def test_portfolio_is_explicitly_not_evaluated(self):
        data = base()
        other_plan = copy.deepcopy(data["plans"][0])
        other_plan["id"] = "other-plan"
        other_plan["pools"][0]["id"] = "other-pool"
        data["plans"].append(other_plan)
        result = calculator.analyze(data)
        self.assertEqual(len(result["evaluations"]), 2)
        self.assertEqual(result["portfolio_analysis"]["status"], "not_evaluated")
        self.assertNotIn("combined_realized_value_usd", result)

    def test_unknown_and_conflicting_quota_are_unranked(self):
        for status in ("undisclosed", "conflicting", "estimated"):
            with self.subTest(status=status):
                data = base()
                data["plans"][0]["pools"][0]["quota"] = {"amount": None,
                                                                "evidence": {"status": status}}
                result = calculator.analyze(data)
                self.assertEqual(result["evaluations"][0]["status"], "unranked")
                self.assertEqual(result["rankings"]["own_api_value"], [])

    def test_live_synthetic_sources_do_not_rank(self):
        data = base()
        del data["data_kind"]  # live is the safe default
        found = row(data)
        self.assertEqual(found["status"], "unranked")
        self.assertTrue(any("evidence_synthetic" in issue for issue in found["reasons"]))

    def test_live_access_permission_is_required_and_checked(self):
        data = base()
        verified = {"status": "verified", "url": "https://example.test/official", "fetched_at": "2026-01-01",
                    "excerpt": "Fictional test evidence"}
        data["data_kind"] = "live"
        data["fx"]["evidence"] = verified
        data["api_prices"][0]["evidence"] = verified
        data["plans"][0]["price"]["evidence"] = verified
        pool = data["plans"][0]["pools"][0]
        pool["quota"]["evidence"] = verified
        pool["rules"][0]["evidence"] = verified
        self.assertIn("access_eligibility_unknown", row(data)["reasons"])
        data["plans"][0]["access"] = {"clients": ["Fictional editor"], "api_access": False,
                                       "evidence": verified}
        data["plans"][0]["limits"] = {"rate_limit": None, "concurrency": None, "fair_use": None,
                                       "overage": None, "evidence": verified}
        data["workloads"][0]["access_by_plan"] = {"basic": {"kind": "api"}}
        self.assertIn("api_access_not_verified_allowed", row(data)["reasons"])
        data["workloads"][0]["access_by_plan"] = {"basic": {"kind": "client", "name": "Fictional editor"}}
        self.assertEqual(row(data)["status"], "valued")
        del data["plans"][0]["limits"]["evidence"]
        self.assertTrue(any("plan_limits" in issue for issue in row(data)["reasons"]))

    def test_usd_only_live_value_does_not_need_fx_source_or_emit_cny(self):
        data = base()
        verified = {"status": "verified", "url": "https://example.test/official", "fetched_at": "2026-01-01",
                    "excerpt": "Fictional test evidence"}
        data["data_kind"] = "live"
        data["fx"]["evidence"] = {"status": "unavailable"}
        data["api_prices"][0]["evidence"] = verified
        plan = data["plans"][0]
        plan["price"]["evidence"] = verified
        plan["pools"][0]["quota"]["evidence"] = verified
        plan["pools"][0]["rules"][0]["evidence"] = verified
        plan["access"] = {"clients": ["Fictional editor"], "api_access": False, "evidence": verified}
        plan["limits"] = {"rate_limit": None, "fair_use": None, "concurrency": None,
                          "overage": None, "evidence": verified}
        data["workloads"][0]["access_by_plan"] = {"basic": {"kind": "client", "name": "Fictional editor"}}
        found = row(data)
        self.assertEqual(found["status"], "valued")
        self.assertNotIn("reachable_value_cny", found)

    def test_exact_model_identity_and_api_mode_gate(self):
        data = base()
        data["api_prices"][0]["batch"] = True
        self.assertIn("api_price_batch_mismatch", row(data)["reasons"])
        data["api_prices"][0]["batch"] = False
        data["api_prices"][0]["context_max"] = 10000
        self.assertIn("api_price_context_mismatch", row(data)["reasons"])
        data["workloads"][0]["model_id"] = "fictional/alpha@latest#standard"
        with self.assertRaisesRegex(calculator.InputError, "mutable alias"):
            calculator.analyze(data)

    def test_upgrade_is_incremental_not_added_and_demand_capped(self):
        data = base()
        data["workloads"][0]["requests_per_month"] = 120
        pro = copy.deepcopy(data["plans"][0])
        pro["id"] = "pro"
        pro["tier"] = "Pro"
        pro["upgrade_from"] = "basic"
        pro["price"]["initial"] = "20"
        pro["price"]["renewal"] = "25"
        pro["pools"][0]["id"] = "pro-pool"
        pro["pools"][0]["quota"]["amount"] = "200"
        data["plans"].append(pro)
        result = calculator.analyze(data)
        upgrade = result["upgrades"][0]
        self.assertEqual(upgrade["incremental_cost_usd"], Decimal("15"))
        self.assertEqual(upgrade["incremental_initial_cost_usd"], Decimal("10"))
        self.assertEqual(upgrade["incremental_reachable_value_usd"], Decimal("1"))
        self.assertEqual(upgrade["incremental_realized_value_usd"], Decimal("0.2"))
        self.assertEqual(row(data, "pro")["realized_requests"], 120)

    def test_non_guaranteed_pool_excluded_from_lower_bound(self):
        data = base()
        extra = copy.deepcopy(data["plans"][0]["pools"][0])
        extra["id"] = "flex-pool"
        extra["quota"]["amount"] = "10000"
        extra["entitlement_class"] = "conditional"
        data["plans"][0]["pools"].append(extra)
        found = row(data)
        self.assertEqual(found["status"], "valued")
        self.assertEqual(found["valuation_scope"], "guaranteed_lower_bound")
        self.assertEqual(found["reachable_requests"], 100)
        self.assertEqual(len(found["excluded_pools"]), 1)

    def test_zero_cost_does_not_create_infinity(self):
        data = base()
        data["plans"][0]["price"]["initial"] = "0"
        data["plans"][0]["price"]["renewal"] = "0"
        result = calculator.analyze(data)
        self.assertIsNone(result["evaluations"][0]["reachable_roi_renewal"])
        self.assertEqual(result["rankings"]["own_api_value"], [])

    def test_missing_tax_terms_are_unknown_not_zero(self):
        data = base()
        data["plans"][0]["price"]["tax_rate"] = None
        data["plans"][0]["price"]["tax_included"] = False
        found = row(data)
        self.assertEqual(found["status"], "unranked")
        self.assertIn("tax_terms_unknown", found["reasons"])
        self.assertIsNone(found["monthly_cost"]["renewal_monthly_usd"])

    def test_tax_inclusive_total_needs_no_tax_rate(self):
        data = base()
        data["plans"][0]["price"]["tax_rate"] = None
        self.assertEqual(row(data)["monthly_cost"]["renewal_monthly_usd"], Decimal("10"))

    def test_missing_entitlement_class_is_schema_error(self):
        data = base()
        del data["plans"][0]["pools"][0]["entitlement_class"]
        with self.assertRaisesRegex(calculator.InputError, "entitlement_class is required"):
            calculator.analyze(data)

    def test_no_workload_is_unranked_and_markdown_renders(self):
        data = base()
        data["workloads"] = []
        result = calculator.analyze(data)
        self.assertEqual(result["evaluations"][0]["reasons"][0], "workload_missing")
        self.assertIn("unknown", calculator.markdown(result))
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "input.json"
            out = Path(temp) / "output.json"
            table = Path(temp) / "table.md"
            path.write_text(json.dumps(data), encoding="utf-8")
            self.assertEqual(calculator.main([str(path), "--output", str(out), "--markdown", str(table)]), 0)
            self.assertIn("workload_missing", table.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
