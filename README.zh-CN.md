# Skills

[English](README.md)

> 面向可检查、可替换的 AI 辅助生产性工作的可复用 Agent 方法与实验性评估运行时。

这是一个面向实践者和贡献者的方法仓库，帮助他们构建或评估 AI 辅助的生产性工作。仓库包含
[Agent Skills](https://agentskills.io) 和实验性的 Work Cell（工作单元）。它只是项目的一个工作
界面，而不是整个项目、模型提供商或不透明的 AI 平台。其语义根是单行的
[原则序列](principles/SEQUENCE.md)；每个 P-ID 都有一份持续演进且来源可追溯的
[解读](principles/interpretations/)，每个 skill 则是在具体语境中对所选条目的表达。

项目的[创始使命](design/FOUNDING-MANDATE.md)是使生产性 AI 成为广泛可及、开放、可替换的
公共能力：让普通人能以经济的开源模型工程系统完成有边界的生产性工作，并以具体证据而非对
不透明平台的依赖来证明能力。它的伦理边界是解放而非攫取：人和 AI 的能力都不得被组织成
不受问责的剥削来源。

请按你眼前要作出的判断选择入口：

- **使用或改造一种方法：** 从下方的活跃 skills 开始。
- **检查或评估一个有边界的 Agent 任务：** 参阅[实验性 Work Cell](packages/work-cell/README.md)。
- **评估项目的目的、权责与运行边界：** 阅读[创始使命](design/FOUNDING-MANDATE.md)和
  [运行协议](design/operations/OPERATING-PROTOCOL.md)。

## 活跃 Skills

| Skill | 命令 | 用途 |
|-------|------|------|
| [principle-cultivation](skills/principle-cultivation/SKILL.md) | `/principle-cultivation` | 原则序列的自身验证守护者。先保留带引文的研究，再提出候选、召开选择性的 P-ID 审议，并试行由人指定的替代项；只有经人批准的采纳才能进入核心。 |
| [harness](skills/harness/SKILL.md) | `/harness` | 设计并验证可持续的 Agent 上下文架构。先映射真实运行时，再分配 L1/L2/L3；把连续性保存在可发现的载体中，并验证上下文确实抵达 Agent 行动。 |
| [skill-engineering](skills/skill-engineering/SKILL.md) | `/skill-engineering` | 设计、改写、审查和测试能改善重复性 Agent 行动的 skills。为目标 skill 形成所选的原则表达小组，携带可单独安装的序列快照，并要求行为证据而非提示词修辞。 |
| [practice-cycle](skills/practice-cycle/SKILL.md) | `/practice-cycle` | 将一次完成、失败或含混的非平凡实践转化为已定结论、下一项最小测试，或转交给尚未解决判断的责任方。 |
| [form-guidance](skills/form-guidance/SKILL.md) | `/form-guidance` | 在实施前判断一个重复性需求应以 skill、决策记录、运行时、投影、有限期运动还是无需新增形式来存在。 |
| [naming-and-articulation](skills/naming-and-articulation/SKILL.md) | `/naming-and-articulation` | 为共享项目概念命名，定义其可操作边界，将解释放在正确的来源处，并拒绝不必要的术语。 |
| [work-estimation](skills/work-estimation/SKILL.md) | `/work-estimation` | 在将任务转换为模型预算、时间或成本前，恢复必要工作及其探索分支。 |
| [strategic-advisory](skills/strategic-advisory/SKILL.md) | `/strategic-advisory` | 基于阶段证据准备供人审议的 Strategy Case；它连接长期方向、中期能力和短期任务候选，但不自行作出承诺。 |
| [artifact-organization](skills/artifact-organization/SKILL.md) | `/artifact-organization` | 审计工件的角色和路径是否仍体现已接受的设计；只有存在实质缺口时才执行一次最小的组织转换。 |

## 实验性运行时

[`packages/work-cell`](packages/work-cell/README.md) 是本集合独立的实践与评估单元。一个
Cell 会表达一个任务特定的主导 P-ID 和至多三个支持项，仅加载这些解读，在隔离工作区内运行
一个有边界的 Agent 任务，并保留已声明的输出工件、结构化输出、终结工具证据、用量、成本和
工作区差异。本地实验运行器会比较盲化的基线/处理变体。它是基础设施，不是可直接调用的
方法论 skill，也不会修改原则序列。

对于日常仓库分析，它的只读 `probe` 交互会从当前目录发现宿主原则序列，将明确的人类意图与
验收条件降解为同一核心契约，并渲染可审查的理由链。精确的 JSON `run` 和 `experiment`
接口仍保留，用于可移植的 fixtures 和配对评估。

## 何时使用哪个 Skill？

| 如果你正在…… | 使用 |
|---|---|
| 研究重复出现的证据是否足以形成可复用的核心原则 | `/principle-cultivation research` |
| 为一个项目搭建 Agent 上下文架构 | `/harness` |
| 创建、改写或进行行为测试一个 Agent skill | `/skill-engineering` |
| 将已完成或失败的非平凡尝试转化为下一项有边界的实践 | `/practice-cycle` |
| 判断一项能力需要 skill、记录、运行时、投影，还是无需新增形式 | `/form-guidance` |
| 为共享概念命名、定义术语，或决定解释应放在哪里 | `/naming-and-articulation` |
| 比较替代方案的真实工作、选择估计精度，或在预算前设定误差容忍度 | `/work-estimation` |
| 从已完成阶段的已验证证据中准备战略方向 | `/strategic-advisory` |
| 检查项目布局是否仍符合既定设计 | `/artifact-organization audit`；仅在有实质缺口时使用 `transition` |
| 审计多个已建立方法如何协作 | 先阅读项目的组织运行模型；使用拥有已观察扰动的角色，而不是新建一个通用总控 skill |

原则序列是根，`principle-cultivation` 负责维护它。**Harness** 组织 Agent 上下文，
**Skill-engineering** 再生并测试 skill 表达，**Artifact-organization** 负责项目根据地与活动
架构；“整理”是一次运动，而不是该 skill 的名称。请参阅各个 SKILL.md 了解交接信号。
[组织运行模型](design/decisions/012-bounded-adaptive-organization.md)规定这些角色如何条件化协作；
它是一份由人治理的设计契约，而不是另一个命令或中心 Agent。

## 归档

再生前的方法 skills（`design-driven`、`goal-driven`、`evidence-driven`、`reframe`、写作
skills）、旧的 `setup-lidessen-skills` 宿主适配器、再生工作笔记、已完成蓝图、文章和幻灯片都
保存在 [`archive/`](archive/README.md)。它们是保留的证据，而不是安装目标。仓库不再维护
根目录的 `blueprints/` 任务编排工作流。此仓库的 `CLAUDE.md` / `AGENTS.md` 中 L1 指引已内联；
若该投影发生改变，请编辑
[`archive/skills/setup-lidessen-skills/references/cross-cutting-principles.md`](archive/skills/setup-lidessen-skills/references/cross-cutting-principles.md)
并手动同步标记。

## 安装

```bash
npx skills install lidessen/skills
```

安装一个指定的活跃 skill：

```bash
npx skills install lidessen/skills/principle-cultivation
npx skills install lidessen/skills/harness
npx skills install lidessen/skills/skill-engineering
npx skills install lidessen/skills/practice-cycle
npx skills install lidessen/skills/form-guidance
npx skills install lidessen/skills/naming-and-articulation
npx skills install lidessen/skills/work-estimation
npx skills install lidessen/skills/strategic-advisory
npx skills install lidessen/skills/artifact-organization
```

命令示例：

```
/harness                    # 上下文分层方法
/harness audit              # 评估现有项目的上下文架构
/harness init               # 首次项目设置
/harness verify             # 证明运行时加载并使用了上下文

/skill-engineering create   # 创建一个能改变行为的 skill
/skill-engineering rewrite  # 重新构成一个继承而来的 skill
/skill-engineering review   # 审计一个 skill 的表达与证据
/skill-engineering test     # 以行动和边界探针测试一个 skill
/skill-engineering sync-sequence-snapshot # 重新生成打包的序列快照

/artifact-organization audit
/artifact-organization transition

/principle-cultivation research <question|paths>
/principle-cultivation propose <research-note>
/principle-cultivation review <candidate|sequence>
/principle-cultivation adopt <candidate>
```

开发评估运行时时，可直接运行 Work Cell 包：

```bash
cd packages/work-cell
bun install
bun run typecheck
bun test
bun run live:p23 # 需要 DEEPSEEK_API_KEY

# 从本仓库或任一子目录运行
bun src/cli.ts probe "Inspect a bounded project question" \
  --accept "Return traceable evidence" \
  --scope packages/work-cell
```

## 许可证

[MIT](LICENSE)
