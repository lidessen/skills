# 输入与输出契约（v2，含当前总权益估计）

将一个 UTF-8 JSON 文件交给 `scripts/analyze.py`。钱与费率用十进制字符串，token 和操作次数用非负整数；估计区间用 `low`、`base`、`high` 三个有序数值。脚本计算并输出 JSON；可另存 Markdown 表格。[合成示例](../examples/synthetic.json) 仅供试算，不能作为市场报价。保存本次输入与结果，才能复核证据和换算。`estimated_evaluations` 是含当期额外权益的主视图，`evaluations` 是基础保证额审计视图。

## 当前性与证据

`data_kind` 为 `live` 或 `synthetic`。正式比较只收录**查询当天当前在售**的产品：每个 `plan.availability` 须为 `{"status":"on_sale","evidence":...}`。在售状态、当期订阅价与权益、模型扣费和官方 API 价格均须重新核查；历史资料或已停售页面不是候选。`query_date` 是查询时区当日的 `YYYY-MM-DD` 日期：可在顶层设置 IANA `query_timezone`（如 `Etc/UTC`），未设置时使用执行主机的本地日期。归档输入和输出保留先前快照供查阅，旧 `live` 输入不能通过新日期的运行校验。新的当前榜单必须当日重新核实并更新日期及证据；`fetched_at` 和现有汇率日期规则仍以 `query_date` 为准。合成样例免除当日门槛。不同地区的在售权益和价格分别建 plan。

正式数据的关键**官方事实**使用 `{"status":"verified","url":"https://官方页面/...","fetched_at":"YYYY-MM-DD","excerpt":"支持该字段的短片段"}`；本次抓取日期须与 `query_date` 一致。官网未公开、资料冲突或页面失效分别标记 `undisclosed`、`conflicting`、`unavailable`，仍需解释原因。估计来源另用下文的 `source` 结构，允许观测日期早于查询日，但来源当次仍须重新检查。未知数值用 `null`，不是零。脚本校验证据结构和状态，但不代替官网取证。`synthetic` 输入使用 `{"status":"synthetic"}`，结果不能当作现价排名。

## 顶层与 API 价格

| 字段 | 含义 |
| --- | --- |
| `schema_version` | 整数 `2`。 |
| `data_kind`, `query_date`, `query_timezone` | 数据身份、查询日期及可选的 IANA 查询时区；未设置时用主机本地日期。 |
| `fx` | `{as_of,per_usd,evidence}`；`per_usd` 是 1 USD 对应的原币数量，如 `{"USD":"1","CNY":"7"}`。保留原币与汇率日期；正式数据涉及跨币种换算时，`as_of` 须等于 `query_date` 并附当日汇率来源；USD 本位不需要外汇来源。 |
| `api_prices` | 每个精确模型、模式、上下文分档及 batch 条件一条官方 API 价。 |
| `conversion_scenarios` | 把请求、credit 或加权 token 套餐换算为 API 金额的**通用技术场景**；按四类 token 分桶或直接给出可扣的 API 金额时无需场景。 |
| `plans` | 每个当前在售的厂商、产品、地区及档位一条。 |

`api_prices[]` 需要 `id`、`model_id`、`currency`、`per_million`、`context_min`、`context_max`、`batch`、`evidence`。`model_id` 应解析到版本或 checkpoint 与模式，如 `vendor/model@2026-01#standard`，不能把未解析的浮动 alias 当成固定版本。`per_million` 分列 `input`、`output`、`cache_read`、`cache_write`；缺价为 `null`。cache write 有不同时长费率时用 `cache_write_duration` 明确本行适用时长。上下文下界含、上界不含；长上下文与 batch 另设价格行，不能平均费率。

`conversion_scenarios[]` 每行有 `id`、`model_id`、`api_price_id`、`per_operation`、`context_tokens`、`batch`、`basis` 和 `label`；全部权益可直接换算时可省略此数组。`per_operation` 是一个通用参考操作所产生、**互不重叠**的四类 token 数；cache token 不再计入 input。一次操作可能包含多次调用，但合并的调用必须同模型、模式、上下文价档和 batch 费率。`basis:"official_usage"` 应附官方 usage 依据；`basis:"assumption"` 是显式换算假设，可用多行低/中/高场景查看敏感性。

## 当前套餐与额度池

`plans[]` 每行包括 `id`、`provider`、`product`、`tier`、`region`、`availability`、`price`、`access`、`limits`、`pools`；可用 `representative_scenario_id` 为跨套餐总价值榜选一个**代表性技术场景**。`access` 记录客户端/API 权限及官方证据；若没有已确认可用的客户端或 API 路径，该行不排名。`limits` 记录限速、并发、公平使用、超额费用及其证据。文字限制保留在结果中，脚本不会把未量化条款假装成可精确扣减的金额。

`price` 为 `{currency,months,initial,renewal,tax_rate,tax_included,evidence}`。`initial` 与 `renewal` 分别是**当前在售条款**下首个账期和续费账期的原币网页标价；任一项未能确认时填 `null`，另一项仍可单独估值。脚本除以 `months` 得月成本。现行促销须注明生效条件和结束时间。税额或结账调整未知时，实际付款成本与倍率为 `null`，不默认零；网页标价只供明确标记的条件倍率使用。

每个 `pools[]` 有全局唯一 `id`、`unit`、`entitlement_class`、`quota`、`window`、`rules`，可带 `additional_caps`、`daily_cap_requests`：

| 字段 | 含义 |
| --- | --- |
| `unit` | `requests`、`credits`、`weighted_tokens`、`currency` 或 `token_buckets`。 |
| `entitlement_class` | `guaranteed`、`conditional` 或 `promotional`。当期额外额度进入**主估计**，仍与基础保证额分解展示，并记录可得性及可叠加证据。 |
| `quota` | 标量池为 `{amount,evidence}`；`token_buckets` 为 `{amounts:{input,output,cache_read,cache_write},evidence}`；金额池还要 `currency`。未知额度用 `null`。 |
| `window` | `{kind:"monthly"}`、`{kind:"weekly",reset:"calendar|rolling|subscription_anchor|unknown"}` 或 `{kind:"rolling_hours",hours:5}`；来源要说明已知的重置起点和有效期，未公开时用 `unknown`。 |
| `rules` | 每个可用精确模型一条扣费规则，含 `model_id`、对应的 `api_price_id`、`basis`、`evidence` 及该 basis 所需费率。同模型在不同地区或费率档不得交叉套用；缺某模型规则即不可给它估值。旧输入省略 `api_price_id` 仅在该模型恰有唯一 API 价格行时自动解析，存在多个价格行则报错。 |
| `additional_caps` | 同一余额、同一扣费单位上的其它上限，如官方月上限；各 cap 有 `id`、`amount`、`window`、`evidence`，可用 `unit` 显式核对与主池同单位。它们与主额度取交集，不能当独立池相加。 |
| `daily_cap_requests` | 额外日限制，只作为原生限制，不外推月度额度。 |

`basis:"request"` 用 `units_per_operation`；`basis:"weighted_tokens"` 用四类 `per_million` 扣费权重及可选 `multiplier`。`basis:"token_buckets"` 的规则用 `api_price_id` 指向该精确模型的官方 API 价，直接将四类互不重叠的 token 权益乘以对应费率求和（有官方扣费倍率时先调整权益）。`unit:"currency"` 且有官方证据证明 `basis:"api_value"` 的池，也用 `api_price_id` 绑定可用的精确模型与官方费率行，再将金额额度按池币种换为 USD、按扣费倍率调整；不把金额切成假想的整数操作。两种直接换算均**无需场景**，但仍须核实模型身份、官方费率行适用的模式或 API 金额扣费口径。请求、消息或 credit 数字本身不等于固定 token 量；若无官方映射，只能依据上述通用场景估值。共享池的多模型结果互斥，不能相加。`token_buckets` 与额外窗口 cap 无法联合估值时，明确未排名。

## 当期总权益的估计输入

基础池的已知额度沿用 `quota`。有当期 flex、bonus 或促销时，**另建** `entitlement_class:"conditional"` 或 `"promotional"` 池；不要把总额度抄成基础池后又加一次。`estimated_evaluations` 会按同一模型和场景合并可叠加的池，按池保留 `components`。每个需估计的池加 `estimate`：

| `pool.estimate` 字段 | 规则 |
| --- | --- |
| `source` | `{class,url,fetched_at,observed_at?,model_match,mismatch_reason?,assumptions:{low,base,high}}`。`class` 可为 `official_current`、`empirical_current`、`stale_empirical`、`explicit_assumption`、`theoretical_window`；当次核查的 `fetched_at` 与 `query_date` 同日。经验来源需 `observed_at`；`model_match` 为 `exact`、`not_applicable` 或 `mismatch`，不相符时解释原因并不排名。三个 `assumptions` 值是说明文字，不是数值。详见[证据与推断规则](evidence.md)。 |
| `quota_anchor` | 只在官方 `quota.amount:null` 且标量池有可辩护额度锚点时填 `{low,base,high}`；不能替换 `token_buckets`，也不能覆盖已公布数值。模型特定锚点须 `source.model_match:"exact"`。 |
| `quota_multiplier`, `multiplier_evidence` | 可选的单个换算系数；不为 1 时要有官方来源证据。不能凭宣传“x 倍”推算 token。 |
| `presence` | 仅对额外池必填 `{low,base,high}`，每项在 0–1 内，表示当前权益在对应场景下的可得份额/适用条件；基础池不得填。数值并非对用户个体利用率的推断。 |
| `additive_to`, `stacking_evidence` | 当额外池与其它同模型池共同估值时，`additive_to` 必须列出**全部其它匹配池 ID**，并附可叠加的官方证据；缺证据则整行不排名。 |
| `window_counts` | 短窗口主池用 `primary:{low,base,high}`；每个短窗口 `additional_caps[].id` 也须有同名键。是每月可用窗口数的技术估计，不是个人活跃时段。短窗口外推的 `source.class` 不能标 `official_current`；标出理论高值与较可辩护的中值。已有月 cap 与窗口额度取交集，不能当独立池相加。 |

这些数值必须满足 `low ≤ base ≤ high`。若有公开官方 credits 对原厂 API 的**逐 token 费率完全等价**，可在 `basis:"weighted_tokens"` 的 credit 规则中填 `api_parity_credit_usd` 及 `api_parity_evidence`。脚本逐一校验四类扣费权重乘该美元/credit 系数后等于同一模型官方 API 费率，再按面值换算；平台 credit 的售价、估算请求数或模糊宣传不能用此捷径。

### 未公布 token 配额的公开测量

原始日志足够完整时，在 `plan.empirical_observations[]` 放同一精确模型及费率行的一条窗口观测。必填 `id`、`model_id`、`api_price_id`、`source`（`empirical_current` 或 `stale_empirical` 且 `model_match:"exact"`）、互不重叠的四类 `token_buckets`、`context_tokens`、`batch`、`accounts:1`、`extra_usage:false`、`window_kind:"weekly"`、`meter_start`、`meter_end`、`exhausted`、`linear_meter_projection`、`value_basis:{low,base,high}` 和 `monthly_window_counts:{low,base,high}`。meter 是 0–1 的额度比例且终值大于初值；cache write 非零时，`cache_write_duration` 须与 API 价格行的写入时长一致。多个账户、未分开的混合模型或额外付费，不得假装一条单模型观测。

`value_basis` 每档为 `observed` 或 `projected`：脚本先按官方 API 四类费率算实际已消费的窗口金额；仅当显式启用 `linear_meter_projection` 时，才能按 meter 增量外推完整窗口。未从零到耗尽的 `observed` 只是容量下界，不能作主估值的 `base`。窗口数量及 API 价影响月度区间，低/中/高并非统计置信区间。观察数据不足以重算 token 时，不编造分桶；可用下述**来源报告的估值**，明确它是外部已派生输入。

### 混合模型来源报告估值

若公开测量已经给出一项混合模型套餐的**每周原厂 API 等值**，可用 `plan.estimate_bundle`：`{id,source,weekly_api_value_usd:{low,base,high},monthly_window_counts:{low,base,high}}`，并令 `pools:[]`。来源需当日复核，`model_match` 用 `not_applicable`，不能标 `exact`。输入每周金额是**来源自己的推算**，脚本只计算折月、附加权益和 ROI，不声称重算了原始 token。来源若按网关价或不明模型 mix 算美元，先拆解口径，否则只能作为较低置信的假设场景。

额外官方 API credit 如确为独立权益，可在 bundle 下附 `api_credit:{monthly_usd,presence:{low,base,high},source,independence_evidence}`。必须证明观测金额没有包含它，及它当前仍适用；否则不加。单模型分池估值和混合模型 bundle 代表不同技术场景，不能相加。同一 plan 不能同时以 `estimate_bundle` 和 `empirical_observations` 申报同一测量。

跨套餐主榜需要 `representative_scenario_id` 对应**恰好一条**本 plan 的估计行：请求/credit 技术场景用 `conversion_scenarios[].id`，公开混合模型估值用 `estimate_bundle.id`，原始单模型测量用 `empirical_observations[].id`，只有直接额度时用 `direct:<canonical model_id>`。它是公开、可解释的比较条件，不是自动挑每个套餐金额最大的模型。未指定、重复或不可排名时，该 plan 进入 `estimated_total_plan_omissions`，仍可保留其它场景的诊断行。

## 输出与排名边界

`estimated_evaluations` 是每档当前总权益的主视图。`category:"exact_model"` 的行绑定精确模型、API 价格行和技术场景；`category:"mixed_model_bundle"` 的行保留来源报告的混合模型估计，不分摊给某一型号。每行 `monthly_api_value_usd`、`roi_initial_listed`、`roi_renewal_listed` 均为 `{low,base,high}`；`components` 拆出分池估值、原始观测或 bundle 的独立 API credit，`source_classes` 与 `confidence` 标识证据。`confidence` 的 `high`、`medium`、`low`、`insufficient` 是来源与换算路径的**定性标签**，不是区间的统计覆盖率；低/中/高是敏感性场景。`reasons` 给出不可排名原因，不能把未知当零。

`rankings.estimated_total_plan_value` 每档最多一条，按所选代表场景的**中值估计 / 当前续费网页标价**排序，并提供 `other_scenario_ids`；不能把其它互斥场景累加或自动选择最高者。`estimated_same_model` 只在同一固定模型、模式、API 费率行与技术场景内比较至少两档。`estimated_own_api_value` 展示各自原厂 API 价下的单模型估计；`estimated_mixed_bundle` 单列混合模型观测。这些美元并非跨模型能力统一分数。未入跨套餐主榜的计划及原因在 `estimated_total_plan_omissions`。

`monthly_cost.initial_monthly_listed_original` / `renewal_monthly_listed_original` 保留原币月度标价，对应 `_usd` 按当日汇率换算。`roi_initial_listed` / `roi_renewal_listed` 按网页标价，税费或结账调整未知时**不表示实付**。已知实付时相应 `roi_initial` / `roi_renewal` 可计算；零成本、价格或汇率缺失时倍率为 `null`，独立可核实的 API 等值仍可保留。主榜按标价的续费中值排序，报告需注明这一统一口径。

`evaluations` 与旧 `rankings.same_model` / `own_api_value` 保留基础保证额的审计口径，不能取代当期总权益主榜。它们的短窗口 `window_api_value_usd_by_pool` 是单窗口诊断值；官方月 cap 给出的 `monthly_api_value_upper_usd` 和对应 `_upper` 倍率只是理论上界，不进入该精确审计榜。主估计可另外按有据的 `window_counts` 折月，并明确来源和理论高值。请求/credit 场景仍取决于 token mix；共享池的不同模型行互斥。限速、公平使用、资格变化等未量化限制随行披露，不能写成精确扣减。
