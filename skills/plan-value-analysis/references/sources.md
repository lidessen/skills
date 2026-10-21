# 当前官方来源入口

以下链接只用于定位**查询时仍在售**的套餐、模型扣费和官方 API 价；不保存报价快照。每次分析重新打开官方页面，核对地区、在售状态、适用模型版本、首期及续费、额度、扣费与有效期，并记录 URL、查询日期和支持字段的短片段。停售页面、过期说明或有冲突的数字不能充作当前权益；先查明适用条款，否则该字段不排名。平台自己的 credit 价格不能无证明地代替模型官方 API 价。

[Models.dev](https://models.dev/) 及其 [provider 数据](https://models.dev/api.json)、[模型元数据](https://models.dev/models.json)、[组合目录](https://models.dev/catalog.json) 可辅助发现模型 ID、开发者、接入服务商和价格候选。它的聚合价格或某接入商报价不自动等于**模型开发者的官方 API 价**；关键版本和费率仍须在模型开发者的官方 API 页面当次核实，也不能靠聚合条目证明某订阅仍在售。

套餐候选可从 [Coding Plan](https://www.codingplan.fyi/) 及其开放的 [plans.json](https://github.com/wmpeng/codingplan/blob/main/plans.json)、[models.json](https://github.com/wmpeng/codingplan/blob/main/models.json)、[platforms.json](https://github.com/wmpeng/codingplan/blob/main/platforms.json)，或 [VibePlan](https://vibeplan.cc/) 的 [数据快照](https://vibeplan.cc/data/latest.json) 发现。聚合数据可能混有实测、推算、请求数估计、未知或不在售的条目；快照的 `generatedAt`/`verifiedAt` 不保证查询当日仍有效，tokens/$ 还取决于固定 cache 与操作场景。它们只帮助寻找候选和官方链接，**不得直接导入数值或排名**；逐项回到官网确认当日仍在售及价格、额度、扣费规则。

| 产品或模型 | 当前核验入口 | 核对重点 |
| --- | --- | --- |
| GitHub Copilot | [套餐](https://github.com/features/copilot/plans)、[个人订阅计费](https://docs.github.com/en/copilot/concepts/billing/usage-based-billing-for-individuals)、[模型与价格](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing) | 当前档位、AI credits、模型费率与缓存扣费。 |
| Claude Max / Code | [Max 套餐](https://support.claude.com/en/articles/11049741-what-is-the-max-plan)、[额度与长度限制](https://support.claude.com/en/articles/11647753-how-do-usage-and-length-limits-work)、[Claude API 价格](https://platform.claude.com/docs/en/about-claude/pricing) | 共用额度与窗口限制；宣传倍率是否有可换算额度。 |
| MiniMax M Plan | [M Plan](https://platform.minimax.io/docs/m-plan/intro)、[API 价格](https://platform.minimax.io/docs/pricing/overview) | 当前在售档位、适用模型与扣费规则。 |
| 小米 MiMo Token Plan | [套餐额度与扣费](https://mimo.mi.com/docs/en-US/quick-start/faq/token-plan/Usage%26Quota)、[API 价格](https://mimo.mi.com/docs/en-US/price/pay-as-you-go) | cache hit/miss/output 权重、时段、额度窗口。 |
| Tencent CodeBuddy | [套餐](https://www.codebuddy.ai/pricing/)、[Credits 说明](https://www.codebuddy.ai/docs/ide/Account/credits) | 产品身份与 credit 扣费；未公布确定映射时不精确估值。 |
| Kimi / Kimi Code | [会员权益](https://www.kimi.com/en/help/membership/membership-overview)、[会员价格](https://www.kimi.com/en/help/membership/membership-pricing)、[模型 API 价格](https://platform.moonshot.cn/docs/pricing/chat) | 当前在售档位、Code 权限及共享额度；会员和 API 为不同产品。 |
| OpenCode Go | [Go 套餐](https://opencode.ai/v2/docs/console/go/) | 当前逐模型金额上限、短窗口与月上限；预估请求数不等于保证额度。 |
| Command Code | [使用限制](https://commandcode.ai/docs/resources/usage-limits)、[价格与限制](https://commandcode.ai/docs/resources/pricing-limits) | 产品身份、共享归一池与窗口；官方页面数字冲突时标记 `conflicting`。 |
| DeepSeek 官方 API | [模型与价格](https://api-docs.deepseek.com/quick_start/pricing/)、[模型列表](https://api-docs.deepseek.com/api/list-models/)、[更新记录](https://api-docs.deepseek.com/updates/) | alias 当次服务 checkpoint、模式及缓存价格；其它平台的模型身份另行核实。 |

其它厂商也须分别找到当前官方**套餐与扣费规则**、**模型身份**及**该模型 API 价格**。任一环节无法核实，就说明缺口，不沿用其它模型或过期套餐的数字。
