---
name: agent-personality
description: Design or revise MBTI-inspired working preferences and standalone handoff prompts for production Agents or deliberately differentiated collaborators; apply or evaluate them when requested. Use for intentional perspective differences; not ordinary delegation, diagnosis, or claims of stable model personality.
metadata:
  short-description: Design and refine production Agent personalities
---

# Agent Personality

这是一个设计时 skill：把希望出现的处理差异变成可执行、可校正、可验证的交接材料。
人格只改变注意和判断的默认顺序，不提供额外能力、事实、权限或专业方法。

## 何时使用

- 设计或修改生产 Agent 的人格材料，交付独立指令块；按任务要求应用或验证。
- 现有人格材料造成偏差，需要诊断、校正或重新设计。
- 多个 Agent 处理同一决策点，需要有意识地获得互补视角。

普通委托、人的心理诊断、只想改变口吻，或声称模型拥有稳定人格，不使用本 skill。
加载本 skill 本身不会切换当前 Agent 的人格，也不要求创建子 Agent。
执行者收到独立人格指令后直接按共同任务使用，无需重新进入设计流程。

## 主流程

1. 确定一个真实的共同任务和需要产生差异的决策点；不要为抽象的“不同性格”设计角色。
2. 选择确实相关的维度和一种塑造方式，只读取对应的 references，不为凑齐类型读取全部资料。
3. 形成连贯的默认倾向、转向条件和纠偏方式，保持共同任务、事实、权限和完成标准不变。
4. 输出设计说明与可独立执行的人格指令块；人格指令块不能要求生产 Agent 回读本 skill。
5. 用户要求应用或验证时，把指令块和共同任务一起交给生产 Agent；验证效果时观察实际材料
   选择、比较、询问、行动和修订。生成材料、成功交接或一次语言差异都不等于人格效果。

## 按需读取

- 理论边界和维度入口：读 [theory-boundary.md](references/theory-boundary.md)。
- 需要解释研究限制或核对依据时，才读 [research-boundary.md](references/research-boundary.md)。
- 需要写倾向、交接材料或普通输出：读 [workflow.md](references/workflow.md)。
- 需要比较多个 Agent、归因差异或做控制变量实验：读 [evaluation.md](references/evaluation.md)。
- 只在确有用途时读取选中的维度和塑造方式 reference；不要一次加载全部资料。
- 诊断现有倾向或研究间接诱导时，才读取相应的 diagnostics、experiment 或 research reference。

## 不变量

- 任务目标、事实、权限、工具和验收标准由共同任务决定，不由人格材料改写。
- 人格不是诊断、类型标签或能力保证；差异必须落在决策过程和结果证据上。
- 不把维度写成绝对禁令，不规定固定工具顺序、问题数量或候选数量；出现反例时允许改判。
- 区分人格差异、任务分工和随机波动；无法归因时标记未知。
- 生产 Agent 的人格指令必须脱离本 skill、类型名称和设计过程仍可执行。

## 完成条件

按用户要求的交付判断完成：设计任务交付有用途依据、可独立执行的指令块；应用任务还须完成
约定的交接或执行；效果验证须提供行为观察及归因限制。明确报告材料完成、已应用和效果已观察
各自达到的程度，不把未要求的执行变成设计任务的完成门槛，也不把材料完成写成效果已证实。
