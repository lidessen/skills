---
name: agent-guidance
description: Decide whether an Agent method belongs in a skill, prompt, or other guidance carrier; review formation, splitting, merging, expression, discovery, and activation. Use for guidance design and refinement; developing uncertain methods through theory and experiments uses skill-incubator, not ordinary task execution or runtime guarantees.
metadata:
  short-description: Design and review Agent guidance
---

# Agent Guidance

这个 skill 处理“Agent guidance 是否是正确的表达与载体”：让已经有来源边界的任务、方法或
协作关系，变成 Agent 能够发现、理解、行动、失败回报并交还结果的指导。skill 和 prompt
只是其中两类载体；它不靠堆模板、字段或流程长度制造可靠性。

先分清三个对象：**method** 是可复用的判断或行动关系；**guidance carrier** 是承载它的任务
表达、handoff、项目指令、`SKILL.md`、reference 或 focus anchor；**activation** 是某次任务
实际发现、加载并使用指导的过程。Prompt 是一次任务或委派的表达载体；harness 是接收环境；
runtime/base 才拥有权限、工具能力、事务、并发、恢复、持久化和不可绕过的效果边界。

## 何时使用

- 新建、审查、拆分、合并、降级或删除任务 prompt、handoff、`AGENTS.md` 指令、skill、reference
  或 focus anchor。
- 某个 Agent 的判断/行动差距反复出现，需要判断是修任务表达、项目指令、skill、工具还是 runtime。
- 指令越来越长、skill 互相重叠、触发不清，或上下文开始被无关材料占满。
- 需要把已接受的方法写成可独立交接的 Agent 任务或方法材料。
- 设计或审查 Agent 上下文组装中的信息分层、就地帮助、历史翻阅或工具结果展开入口。

概念定义、面向人的文章、委派拓扑、工具实现和运行时硬保证，交给相应
的相邻 owner；不要为了使用本 skill 强行创建一个 skill 文件。
如果主要问题是代码/设计/目录的残留整理，使用 [defrag](https://github.com/lidessen/skills/blob/main/skills/defrag/SKILL.md)；UI 审美使用
[interface-design](https://github.com/lidessen/skills/blob/main/skills/interface-design/SKILL.md)；Agent 行为现场评估使用当前任务环境提供的评估方法；
人格差异设计使用 [agent-personality](https://github.com/lidessen/skills/blob/main/skills/agent-personality/SKILL.md)。本 skill 只拥有指令载体与
方法表达的判断。
若方法本身还需从理论、已有实践与实验反馈中发展，使用
[skill-incubator](https://github.com/lidessen/skills/blob/main/skills/skill-incubator/SKILL.md)。它设计核心方法与工作流并据证据迭代；
本方法继续负责载体成立性、表达和激活。已确定方法的局部编辑无需先孵化。

若问题是整套技能、角色或项目单元如何分工、覆盖任务并共同演进，使用
[architecture](https://github.com/lidessen/skills/blob/main/skills/architecture/SKILL.md) 组织整体审查。本方法继续负责各指导载体的成立性、
表达、发现与激活判断；整体审查带入目标、环境、最近邻冲突和已有证据，复用局部结果。
单份 skill 修改无需先做体系架构，链接也不要求递归加载。

## 主流程

1. **恢复真实压力。** 找到 Agent、环境、行为对象、已观察差距、重复性、正负触发、最近邻
   owner 和下一个会改变判断的未知。不要从用户指定的文件名或“必须产出 skill”开始。
2. **选择最小真实载体。** 比较当前任务表达、项目局部指令、普通文档、reference、skill、
   projection、工具和 runtime。只有可选择加载的方法在相关任务中重复、能由表达改变行为、
   有可观察边界且收益超过上下文与维护成本时，才提出 skill。
3. **写成可行动表达。** 保留对象与目标、来源状态、接收上下文、允许效果、判断与验收、
   未知与失败、返回关系。区分事实、指令、候选、参考和未知；不要把愿望写成权限或现状。
4. **整理加载面。** description 只说明触发和重要排除项；根 `SKILL.md` 做最小路由；只把
   条件分支细节放进按需 reference。不要把理论、研究记录、全仓背景或第二份权威源塞进普通激活。
5. **验证实际激活。** 分开报告格式通过、激活后的行为、边界支持、匹配改善和回归证据；没有
   baseline、反例或重复观察时，保持未知，不把文件存在或一次成功写成效果证明。

## 按需读取

- 判断是否值得沉淀为 skill 或其他持久 guidance、如何拆分/合并/降级：读 [formation.md](references/formation.md)。
- 编写或压缩 Agent-facing 任务、handoff、skill 正文或 focus anchor：读 [composition.md](references/composition.md)。
- 组织上下文内容、状态与操作提示，或设计渐进披露：读 [context-interface.md](references/context-interface.md)。
- 诊断载体层级、重叠、冲突和上下文负担：读 [review.md](references/review.md)。
- 设计行为探针或报告证据强度：读 [evaluation.md](references/evaluation.md)。

只读取会改变当前判断或行动的 reference。理论与研究是本 skill 的生成来源，不是普通激活的
前置阅读；任务事实仍回到任务自己的 canonical source。

## 不变量

- prompt、skill、`AGENTS.md` 或 reference 不会凭文字获得工具、权限、原子性、持久身份、并发、
  恢复、发布或最终接受；这些关系由工具、runtime、项目 owner 或接受者拥有。
- 文件格式通过、skill 被加载、Agent 自称理解和产物生成，分别不能替代行为观察、语义判断和最终接受。
- 保留会改变对象身份、来源地位、范围、判断路径、允许效果、失败处理、返回或验收权的承重语义；
  只压缩重复、礼貌性前言、无信息总结和不会改变下一步的背景。
- 不规定固定工具顺序、问题数量、候选数量或必经阶段；方法应说明条件和转向理由，而不是写成脚本。
- 不创建第二份事实、计划、评估台账或永久协调者；派生视图保留 canonical source 和更新关系。
- 在已授权范围内，可逆的载体编辑、引用修复和本地检查直接推进；只有改变目标、owner、公开契约、
  权限或不可逆效果时，才暂停受影响分支并请求决定。

## 交付

返回一份能让调用者重建决定的紧凑记录：

```md
对象与真实压力：<Agent 在什么环境中反复缺什么判断/行动>
载体决定：<直接表达 / 局部指令 / 文档 / reference / skill / 工具 / runtime / no-proposal>
主要方法：<希望改变的判断、正负触发和最近邻 owner>
实际改动：<正文、description、路由或引用如何变化>
验证与未知：<机械结果、行为观察、边界/回归证据、尚未确认的关系>
```

完成意味着载体选择有据、表达可独立行动、引用和权威关系闭合，并且报告只达到当前证据
支持的强度。若用户要求落地、激活和修复，就继续到同一观察重新验证，不能停在首稿或首个
机械检查通过；仅写出一份漂亮 prompt 或 skill 草稿，不算完成行为验证。
