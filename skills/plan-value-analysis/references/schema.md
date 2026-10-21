# Analysis input and output (v1)

Pass one UTF-8 JSON file to `scripts/analyze.py`. Numbers used in money or rates should be decimal strings; token and request counts may be nonnegative integers. The script validates the file and emits JSON with calculated evaluations, rankings, exclusions, and upgrade comparisons. Keep the source snapshot with the output so another person can reproduce the result.

`examples/synthetic.json` is a fabricated fixture. Set `data_kind` to `"live"` (the default) only after checking current official terms. A synthetic output is never a current market recommendation.

## Identity, sources, and unknowns

- `model_id` is a canonical checkpoint/version **and** mode, such as `vendor/model@2026-01#standard`. Resolve mutable aliases before analysis. Two plans enter a same-model comparison only when that exact ID and the applicable API price row, context tier, batch mode, and workload match. Similar names or benchmark quality do not establish equivalence.
- Every live FX observation, API price, subscription price, quota, and model debit rule needs an `evidence` object: `{"status":"verified","url":"https://official.example/...","fetched_at":"YYYY-MM-DD","excerpt":"short relevant passage"}`. Use the actual official page, not this illustrative URL. `fetched_at` is the observation date, not necessarily the effective date. Preserve effective dates and region in the excerpt or notes when they matter.
- Other evidence statuses are `estimated`, `undisclosed`, `conflicting`, and `unavailable`. These do not authorize an exact numeric entitlement or precise ranking. Use `null` for a genuinely unknown amount or rate. Zero means an evidenced zero, never “not found.” If official pages disagree, keep the conflicting evidence and resolve the applicable regime before ranking.
- In a synthetic fixture, use `{"status":"synthetic"}` on sourced fields. This deliberately bypasses the live evidence claim; its numeric results illustrate the calculator only.
- `provider`, `product`, `region`, and `billing_regime` are separate identifiers. Record legacy versus current billing, grandfathered terms, contributor variants, country versions, and client/API scope as distinct plan records when their rights differ. Do not merge similarly named companies or products.

## Top level

| Field | Meaning |
| --- | --- |
| `schema_version` | Integer `1`. |
| `data_kind` | `"live"` or `"synthetic"`; omitted means live. |
| `period_days` | Days in the modeled monthly demand period, for example `30`; this does not create active rolling windows. |
| `fx` | `{as_of, per_usd, evidence}`. `per_usd` maps each currency to units of that currency per USD, such as `{"USD":"1","CNY":"7"}`. Keep original currencies in the input and output. |
| `api_prices` | Official API price rows for exact model/mode/context/batch combinations. |
| `workloads` | Explicit measured usage or labeled scenario mixes and monthly demand. |
| `plans` | One row per provider/product/tier/region/billing regime. |

FX and tax dates need to be compatible with the comparison date. Do not silently convert a first-term promotion into a recurring price. The calculator uses the supplied rate; it does not fetch exchange rates or vendor pages. When `CNY` is in `per_usd`, evaluations also include CNY equivalent fields alongside USD and original-currency cost.

## API price rows and workloads

An `api_prices[]` row contains `id`, `model_id`, `currency`, `per_million`, `context_min`, `context_max`, `batch`, and `evidence`. `per_million` has separate `input`, `output`, `cache_read`, and `cache_write` prices per one million tokens. Use `null` for a price that is not published; a workload using that bucket cannot receive an exact API value. `context_min` is inclusive and optional `context_max` is exclusive; `batch` records batch pricing. Represent a long-context tier or batch price as a separate row, not an averaged price.

A `workloads[]` row contains:

| Field | Meaning |
| --- | --- |
| `id`, `model_id`, `api_price_id` | Exact model and applicable API price row. |
| `requests_per_month` | Shared demand for this modeled use, not a vendor's advertised quota. |
| `per_request` | **Disjoint** `input`, `output`, `cache_read`, `cache_write` token counts, including the model calls made to satisfy one user task only if they share the same exact model, mode, batch state, context tier, and API price row. Do not include cache tokens again in `input`. |
| `context_tokens`, `batch` | Used to validate the selected API context tier and batch mode. |
| `basis`, `label` | `"measured"` for observed usage with evidence, or `"scenario"` with an explicit label. A request/message cap without sourced call usage can only be a scenario, not a precise token promise. |
| `access_by_plan` | Map from plan ID to `{kind:"client",name:"exact permitted client"}` or `{kind:"api"}`. Live rows need an explicit access context matching the plan's `access` rights. |
| `active_windows_per_month` | Map of globally unique pool IDs to realistically usable window counts for weekly or rolling limits. Missing counts are unknown, never treated as 24-hour cycling. A count alone does not show how demand is distributed across windows. |
| `active_days_per_month` | Optional active days for a daily cap. |

For uncertainty, enter separate low/base/high workload rows with their assumptions and inspect the range; do not hide it in a single “average request.” One `api_price_id` cannot value a task that switches models, context price tiers, or batch modes. Split only when homogeneous components and their demand allocation are known; otherwise leave the task unranked rather than blending rates. With only monthly demand and an active-window count, even the `realized` result is an upper bound under an assumed distribution that fills the usable windows. Check request timestamps or use a conservative scenario before calling it actual usage. API equivalent is replacement API spend for the specified mix, not a cash refund or a claim that proprietary models have equal ability.

## Plans and entitlement pools

Each `plans[]` row has `id`, `provider`, `product`, `tier`, `region`, `billing_regime`, `price`, `pools`, and optional `upgrade_from` pointing to another plan ID. `access` is `{clients:[...],api_access:true|false|null,notes:string|null,evidence}`; a live ranking needs verified access evidence and an applicable `workload.access_by_plan` choice. `limits` is `{rate_limit:string|null,concurrency:integer|null,fair_use:string|null,overage:string|null,evidence}`. Live rows need official evidence for these restrictions even when a specific rate or concurrency number is undisclosed and therefore `null`. Missing limits/access evidence leaves a live row unranked. They are disclosed with the evaluation but the script does not infer a numeric adjustment from the text. If a fair-use or rate restriction could materially prevent the modeled quota from being used and cannot be modeled, mark the quota uncertain and leave it unranked; a numerical allowance does not override such restrictions.

`price` contains `currency`, `months` (positive integer months per bill, for example `1` monthly or `12` annual), `initial`, `renewal`, `tax_rate`, `tax_included`, and `evidence`. `initial` and `renewal` are each the **total paid for one term** in the original currency. The script divides by `months` to compare monthly cost, reports first-term and renewal results separately, and adds `tax_rate` only when `tax_included` is false. `tax_rate` and `tax_included` are required; `null` or unknown tax leaves cost unranked, rather than silently treating it as zero.

Each pool has a globally unique `id`, `unit`, `quota`, `window`, `rules`, and optional `daily_cap_requests`:

| Field | Meaning |
| --- | --- |
| `unit` | `requests`, `credits`, `weighted_tokens`, `currency`, or `token_buckets`. |
| `entitlement_class` | Required: `guaranteed`, `conditional`, or `promotional`. Only a verified guaranteed base belongs in a precise ranking; record flex, “up to,” or conditional additions separately. |
| `quota` | `{amount, evidence}` for a scalar pool; `{amounts:{input,output,cache_read,cache_write},evidence}` for `token_buckets`; `currency` is required for a currency pool. `null` amount means unknown. |
| `window` | `{kind:"monthly"}`, `{kind:"weekly"}`, or `{kind:"rolling_hours",hours:5}`. A nonmonthly window needs the workload's explicit active-window count. For `weekly`, the official reset anchor and calendar versus rolling semantics must be recorded in the evidence and workload label; this format does not infer them. If unresolved, leave active windows unknown and the row unranked. |
| `rules` | One deduction rule per eligible exact model. The rule has `model_id`, `basis`, and `evidence`; optional numeric fields depend on `basis`. Omitted models are ineligible for that pool. |
| `daily_cap_requests` | Optional additional requests/day limit, applied only when active days are supplied. |
| `additional_caps` | Optional caps on the **same** scalar balance and debit unit: `[{id,amount,window,evidence}]`. The engine intersects them with the primary quota. For a weekly/rolling additional cap, provide its usable count as `active_windows_per_month["pool-id:cap-id"]`. `token_buckets` plus an additional cap is unsupported and unranked. |

`basis:"request"` uses `units_per_request`, including the model's credit multiplier if appropriate. `basis:"weighted_tokens"` uses `per_million` bucket weights and optional `multiplier`; this represents a published token/credit deduction formula. `basis:"api_value"` deducts the workload's API replacement cost, converted to the pool currency where needed. `basis:"token_buckets"` deducts each disjoint token class from its matching allowance. The face value of all token buckets can exceed the value reachable by one fixed workload mix if some buckets are stranded. Use only a rule actually supported by plan terms; do not infer a fixed token count from marketing request estimates or a “5× usage” statement.

One shared pool may list several eligible models. Each model's full-pool value is an **alternative use of that same balance**, not additive inventory. Enter separate pools only for genuinely independent balances. Weekly, rolling, monthly, and daily caps on the **same** balance are intersecting constraints, never additive pools; use `additional_caps` and `daily_cap_requests` where applicable. A tier with `upgrade_from` replaces its lower tier; its full entitlements do not stack on top of the lower tier.

## Output and interpretation

The JSON output includes `evaluations`, `rankings.same_model`, `rankings.own_api_value`, `rankings.realized`, `upgrades`, and `portfolio_analysis`. Each evaluation retains plan/tier, model, workload, `status`, `reasons`, `evidence_grade`, original-currency and USD monthly cost, per-window entitlement diagnostic, reachable value under the modeled active windows, demand-capped value, `effective_utilization`, `valuation_scope`, `reachable_bound_kind`, `realized_bound_kind`, `value_bounds_usd`, `limitations`, and disclosed access and limits. `value_bounds_usd` states lower and upper values: only a modeled monthly capacity without unresolved operational limits can have equal reachable bounds. Live capacity can remain an upper bound because fair-use, rate, and concurrency terms may bind; rolling-window reachability also has zero as a conservative lower bound. Demand-capped value retains a zero lower bound unless actual use is established. The `pools` array explains each eligible pool; `excluded_pools` exposes conditional or promotional pools. `valuation_scope:"guaranteed_lower_bound"` means the evaluation values only guaranteed pools. `entitlement_value_per_window_usd` is a pool-level face-value diagnostic, not a monthly amount; unlike `reachable_value_usd`, it may include token bucket value not consumable with the given workload. A pool-level `reasons` list or evaluation `status:"unranked"` explains missing quota, price, FX, active-window assumptions, or evidence. The same-model view groups identical checkpoint/mode, API price row, and workload and includes only groups with at least two eligible plan rows. The own-API view lets each proprietary model use **its own official API price**; dollar figures there are not quality-normalized. The realized view reflects modeled use under stated assumptions, not guaranteed consumption or resale value.

ROI is API replacement value divided by the corresponding subscription cost. The supplied rankings sort by **renewal** ROI: reachable ROI for `same_model` and `own_api_value`, demand-capped ROI for `realized`. Initial-term ROI is still in each evaluation, based on the same guaranteed entitlement; an excluded promotional quota is not silently added to initial value. Break-even utilization is subscription cost divided by the reachable API value. A zero subscription cost makes ROI undefined; an unbounded or unknown allowance cannot have a finite exact ROI. Do not invent ranks for missing prices, FX, quotas, incompatible modes, or unresolved conflicting source terms. `portfolio_analysis.status:"not_evaluated"` means no plan bundle has been valued. Never sum individual `reachable` or `realized` rows into combined coverage, combined ROI, or a “best few plans” claim. That requires a deterministic allocation of shared demand across plans, models, and usable windows, followed by marginal cost/value calculation. Report overage separately unless its cost has been explicitly modeled.
