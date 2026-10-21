# 输入与输出契约（v2）

将一个 UTF-8 JSON 文件交给 `scripts/analyze.py`。钱与费率用十进制字符串，token 和操作次数用非负整数。脚本计算并输出 JSON；可另存 Markdown 表格。[合成示例](../examples/synthetic.json) 仅供试算，不能作为市场报价。保存本次输入与结果，才能复核证据和换算。

## 当前性与证据

`data_kind` 为 `live` 或 `synthetic`。正式比较只收录**查询当天当前在售**的产品：每个 `plan.availability` 须为 `{"status":"on_sale","evidence":...}`。在售状态、当期订阅价与权益、模型扣费和官方 API 价格均须重新核查；历史资料或已停售页面不是候选。`query_date` 是执行环境当日的本地 `YYYY-MM-DD` 日期；归档输入和输出保留先前快照供查阅，旧 `live` 输入不能通过新日期的运行校验。新的当前榜单必须当日重新核实并更新日期及证据。合成样例免除当日门槛。不同地区的在售权益和价格分别建 plan。

正式数据的关键来源使用 `{"status":"verified","url":"https://官方页面/...","fetched_at":"YYYY-MM-DD","excerpt":"支持该字段的短片段"}`；本次抓取日期须与 `query_date` 一致。官网未公开、资料冲突或页面失效分别标记 `undisclosed`、`conflicting`、`unavailable`，仍需解释原因。未知数值用 `null`，不是零。官方 URL 与片段由执行者核实，脚本校验证据结构和状态，但不代替官网取证。`synthetic` 输入使用 `{"status":"synthetic"}`，结果不能当作现价排名。

## 顶层与 API 价格

| 字段 | 含义 |
| --- | --- |
| `schema_version` | 整数 `2`。 |
| `data_kind`, `query_date` | 数据身份与查询日期。 |
| `fx` | `{as_of,per_usd,evidence}`；`per_usd` 是 1 USD 对应的原币数量，如 `{"USD":"1","CNY":"7"}`。保留原币与汇率日期；正式数据涉及跨币种换算时，`as_of` 须等于 `query_date` 并附当日汇率来源；USD 本位不需要外汇来源。 |
| `api_prices` | 每个精确模型、模式、上下文分档及 batch 条件一条官方 API 价。 |
| `conversion_scenarios` | 把请求、credit 或加权 token 套餐换算为 API 金额的**通用技术场景**；按四类 token 分桶或直接给出可扣的 API 金额时无需场景。 |
| `plans` | 每个当前在售的厂商、产品、地区及档位一条。 |

`api_prices[]` 需要 `id`、`model_id`、`currency`、`per_million`、`context_min`、`context_max`、`batch`、`evidence`。`model_id` 应解析到版本或 checkpoint 与模式，如 `vendor/model@2026-01#standard`，不能把未解析的浮动 alias 当成固定版本。`per_million` 分列 `input`、`output`、`cache_read`、`cache_write`；缺价为 `null`。上下文下界含、上界不含；长上下文与 batch 另设价格行，不能平均费率。

`conversion_scenarios[]` 每行有 `id`、`model_id`、`api_price_id`、`per_operation`、`context_tokens`、`batch`、`basis` 和 `label`；全部权益可直接换算时可省略此数组。`per_operation` 是一个通用参考操作所产生、**互不重叠**的四类 token 数；cache token 不再计入 input。一次操作可能包含多次调用，但合并的调用必须同模型、模式、上下文价档和 batch 费率。`basis:"official_usage"` 应附官方 usage 依据；`basis:"assumption"` 是显式换算假设，可用多行低/中/高场景查看敏感性。

## 当前套餐与额度池

`plans[]` 每行包括 `id`、`provider`、`product`、`tier`、`region`、`availability`、`price`、`access`、`limits`、`pools`。`access` 记录客户端/API 权限及官方证据；若没有已确认可用的客户端或 API 路径，该行不排名。`limits` 记录限速、并发、公平使用、超额费用及其证据。文字限制保留在结果中，脚本不会把未量化条款假装成可精确扣减的金额。

`price` 为 `{currency,months,initial,renewal,tax_rate,tax_included,evidence}`。`initial` 与 `renewal` 分别是**当前在售条款**下首个账期和续费账期的原币总付款；脚本除以 `months` 得月成本。现行促销须注明生效条件和结束时间。税额未知使该成本不可精确估值，不默认零。

每个 `pools[]` 有全局唯一 `id`、`unit`、`entitlement_class`、`quota`、`window`、`rules`，可带 `additional_caps`、`daily_cap_requests`：

| 字段 | 含义 |
| --- | --- |
| `unit` | `requests`、`credits`、`weighted_tokens`、`currency` 或 `token_buckets`。 |
| `entitlement_class` | `guaranteed`、`conditional` 或 `promotional`。有条件的额外额度不可混入保证额度排名。 |
| `quota` | 标量池为 `{amount,evidence}`；`token_buckets` 为 `{amounts:{input,output,cache_read,cache_write},evidence}`；金额池还要 `currency`。未知额度用 `null`。 |
| `window` | `{kind:"monthly"}`、`{kind:"weekly"}` 或 `{kind:"rolling_hours",hours:5}`；来源要说明重置起点和有效期。 |
| `rules` | 每个可用精确模型一条扣费规则，含 `model_id`、`basis`、`evidence` 及该 basis 所需费率。缺某模型规则即不可给它估值。 |
| `additional_caps` | 同一余额、同一扣费单位上的其它上限，如官方月上限；各 cap 有 `id`、`amount`、`window`、`evidence`，可用 `unit` 显式核对与主池同单位。它们与主额度取交集，不能当独立池相加。 |
| `daily_cap_requests` | 额外日限制，只作为原生限制，不外推月度额度。 |

`basis:"request"` 用 `units_per_operation`；`basis:"weighted_tokens"` 用四类 `per_million` 扣费权重及可选 `multiplier`。`basis:"token_buckets"` 的规则用 `api_price_id` 指向该精确模型的官方 API 价，直接将四类互不重叠的 token 权益乘以对应费率求和（有官方扣费倍率时先调整权益）。`unit:"currency"` 且有官方证据证明 `basis:"api_value"` 的池，也用 `api_price_id` 绑定可用的精确模型与官方费率行，再将金额额度按池币种换为 USD、按扣费倍率调整；不把金额切成假想的整数操作。两种直接换算均**无需场景**，但仍须核实模型身份、官方费率行适用的模式或 API 金额扣费口径。请求、消息或 credit 数字本身不等于固定 token 量；若无官方映射，只能依据上述通用场景估值。共享池的多模型结果互斥，不能相加。`token_buckets` 与额外窗口 cap 无法联合估值时，明确未排名。

## 输出边界

`evaluations` 为每档、每模型的独立行；请求/credit/加权 token 行还按通用换算场景区分，直算行的 `scenario_id` 为 `null`。`rankings.same_model` 只比较精确模型和 API 价格行相同的至少两档；需场景换算的行还须场景相同。`rankings.own_api_value` 展示各模型按**各自官方 API 价**的套餐等值。后者的美元数不是能力或质量统一分数。一个 plan 的同一共享池在不同模型下是互斥估值，不是多份额度。

月度池可输出 `monthly_api_value_usd` 与首期/续费 `roi_initial`、`roi_renewal`；请求/credit/加权 token 的结果标 `value_kind:"official_usage_conversion"` 或 `"assumption_conversion"`，token 桶面值标 `"bucket_face_value"`，API 金额池面值标 `"api_spend_face_value"`。同一精确模型和 API 价格行的独立直算池与场景换算池兼容并可相加时，标 `"mixed_direct_and_operation_conversion"`；总额仍取决于该场景。`component_pool_ids` 列出本行包含的池。ROI 是 API 替代成本除以相应月度订阅成本，零成本的 ROI 为未定义。数值是公布额度在指定费率下的 API 面值；未量化的限速、公平使用等限制仍可能妨碍用满。独立且兼容的额度池可求和；任一池无法估值或不能证明可相加时，整行不排名且不展示部分套餐 ROI。共享池的不同模型仍是互斥替代方案。脚本保留原币成本、证据等级、限制和未排名原因。

只有周/滚动额度而没有官方月上限时，`window_api_value_usd_by_pool` 按池列出单窗口诊断值，`status:"unranked"`，不生成月度 ROI。若同一池还有官方月上限，或月度池同时受短窗口/日 cap 约束，脚本只输出 `status:"upper_bound"`、`monthly_api_value_upper_usd` 和相应 `roi_initial_upper`/`roi_renewal_upper`；这些理论上界**不进入精确排名**。限速与公平使用等未量化限制仍须随行披露。没有可信官方价格、额度或扣费映射的行保持未排名，不能沿用过期数字补空。
