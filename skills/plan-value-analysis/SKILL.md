---
name: plan-value-analysis
description: 估计当前在售 AI coding/token 订阅各档的官方 API 等值与标价倍率，纳入当期 flex、bonus 和促销权益并展示区间。用于跨厂商或同产品套餐性价比排名；不同模型的金额不代表能力相同。
metadata:
  short-description: 当前套餐 API 等值估计
---

# Plan Value Analysis · 套餐性价比

估计**查询时仍在售**的每档套餐，当期总权益能替代多少同模型官方 API 花费，以及相对网页公示订阅价的倍率。API 等值是替代成本，不是现金返还或模型能力分数。所有月度换算、倍率和排序交给 `scripts/analyze.py`，不要心算补齐未知值。

## 取证与估计

1. 当次核对地区、档位、现价及续费、当前 flex/bonus/促销的适用条件、额度、共享关系、有效期、实际模型扣费、访问路径与限制。停售和旧版本不能作为候选。每个关键字段保留官方 URL、查询日和证据片段；[来源入口](references/sources.md) 只用于导航。
2. 解析模型的固定版本、模式或当次 checkpoint；按实际适用的 input/output/cache read/cache write、长上下文与 batch 官方 API 价估值。同系列模型和不同托管商的价格不得混同，token 桶不得重复计费。
3. **主估值包含当期总权益**：基础额度与当前额外额度分池记录，只有证明可叠加才求和；额外额度的可得条件用低/中/高场景表达。共享池的不同模型是互斥估值。只有窗口额度、请求数或未公开 token 上限时，主动寻找公开原始用量与额度计量证据，再用有依据的技术场景估计；不把实际已用金额冒充总容量，也不把理论上限冒充实测。[证据与推断规则](references/evidence.md) 说明所需元数据和置信边界。
4. 请求、credits、加权 token 的换算须有模型扣费映射和完整调用 token 构成，或显式通用 workload 假设；一次操作可能包含多次调用。短窗口折月须写明可用窗口数的低/中/高假设和官方月上限。确实没有可信锚点时说明缺口，不能用 `0`、过期套餐或别的模型价格填空。

## 计算与呈现

按 [输入契约](references/schema.md) 编写 JSON；[合成示例](examples/synthetic.json) 只演示格式，**不是现行报价**。正式输入的 `query_date` 和关键官方证据须当日复核；任务时区不同于主机时，在顶层设置 IANA `query_timezone`。归档旧输入仅供回看，不能改日期重当新榜。运行：

```sh
python3 scripts/analyze.py INPUT.json --output RESULT.json --markdown TABLE.md
```

以 `estimated_evaluations` 及 `rankings.estimated_*` 给出每档**当前总权益**的低/中/高 API 等值、按续费网页标价的倍率、证据层级及限制；基础保证额和额外额在 `components` 中拆开。每档选一个有依据的 `representative_scenario_id` 进入 `estimated_total_plan_value`，其余互斥模型/负载场景不相加。同精确模型与费率行放入 `estimated_same_model`；独有模型放入按各自官方 API 价计的 `estimated_own_api_value`；混合模型公开测量只放 `estimated_mixed_bundle`，不得当作单一模型价值或质量统一排名。基础额度的 `evaluations` 只是审计视图，不替代主榜。

保留原币、首期与续费、当前优惠时效、税费状态、短窗口与公平使用限制。网页标价倍率须注明税费或结账调整未计；实付成本未知时不声称实付 ROI。上下界、证据等级与场景假设随排名呈现。不要索取个人用量，也不要按个人活跃时间另造榜单。
