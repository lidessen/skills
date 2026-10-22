# 任务与模型选路

## 使用当期证据，不写固定榜单

先从实际 Magpie 目录和 runner 能识别的 route 找候选，再查模型开发者当期官方能力与上下文
说明：[OpenAI 模型目录](https://developers.openai.com/api/docs/models)、
[Anthropic 模型目录](https://docs.anthropic.com/en/docs/about-claude/models)、
[Gemini 模型目录](https://ai.google.dev/gemini-api/docs/models)。
[Models.dev](https://models.dev/) 可帮助发现 ID、上下文和价格候选，但聚合条目不是当前
账户权限、官方费率或质量排名的证明。

性能可参考 [Artificial Analysis 模型测量](https://artificialanalysis.ai/models)及其
[方法](https://artificialanalysis.ai/methodology)，编码任务可参考
[SWE-bench 官方榜](https://www.swebench.com/)。记录评测日期、测试集与 harness；综合分数
不自动适用于具体任务或 runner。保留当前任务的成功/失败与端到端延迟作为后续修正证据，
一次失败不永久拉黑 route。没有可比实时数据时写明不确定，不捏造排名。

按顺序判断：

1. **能力门槛**：任务类别、工具调用可靠性、所需上下文、语言或多模态能力、权限与输出
   格式；不满足者即使免费也不入选。
2. **通道门槛**：当前 runner 识别 route，当前认证身份与官方允许的计费路径已核实。
   已有套餐优先，但套餐声明不是当前认证，也不是可在任意 API 使用的凭据。官方支持的
   套餐集成须经用户主动授权；私有代理或绕过条款的转接不作候选。
3. **权衡**：满足质量门槛者比较预计端到端延迟、可用额度和边际成本。共享套餐池只算一次；
   窗口、并发、速率和剩余用量未知时保持未知，不假设无限。选路模型调用也计入成本和额度。
4. **决策记录**：写出 route（runner、provider、模型准确版本、推理档）、选择理由、查证
   日期与来源、已知共享池与用量限制、预计付费影响及不确定处。不要按旧型号名单自动选。

对现有 group 或 fallback，检查其每个成员是否都满足禁止与付费限制；Magpie 的自动切换
不能替主 Agent 审核。429 可能是短期限流、并发限制、共享池窗口耗尽或 API 支付/认证问题，
须按返回错误及 `Retry-After` 分类；不同 route 若共用同一池，不是有效的额度 fallback。
预算或付费 API fallback 未获允许时，等待明确重置、改用已核实的合规候选或返回阻塞。

当模型、runner CLI、套餐/计费条款、目录、任务类型变化，相关证据过时、反复失败或遇
429 时刷新受影响项；无需每轮全网重搜。具体套餐读当前官方条款，尤其区分 Codex 等
原生订阅、[官方授权的第三方套餐共享](https://help.openai.com/en/articles/20001542-using-your-chatgpt-plan-in-other-apps-and-sites)
与普通 API 计费。[Claude Code 认证说明](https://docs.anthropic.com/en/docs/claude-code/iam)
及 [Cursor CLI 认证说明](https://cursor.com/docs/cli/reference/authentication)展示同一 runner
可能有不同登录方式，不能从工具名称推断收费方式。
