---
name: defrag
description: Consolidate stale, duplicated, or misplaced code, documentation, and references while preserving valid responsibilities and behavior. Use for cleanup and ownership repair; not deciding which Agent methods deserve separate skills, redefining architecture, or visual design critique.
---

# Defrag

整理一个机制、概念或职责，使它的实现、说明和目录归属重新清楚。目标是降低理解、查找和
修改成本，保留仍有效的行为、设计意图和必要依据；删除数量或目录整齐度不是目标。

主要产物是清楚的维护归属与闭合的入口、引用和实现关系。整理可能暴露设计问题，但
不能用合并文件、删除名称或移动目录代替决定一份责任是否仍然需要。

## 主流程

1. **界定问题。** 从用户请求中确定一个待回答的问题、范围、必须保留的行为和交付结果。
   大范围工作先选一个能独立闭合的局部；不要为了开始而建立全仓地图。
2. **恢复关系。** 找到实际入口、消费者、维护位置、注册或动态加载、构建发布和相关说明。
   先读能改变当前判断的片段；区分当前实现、目标设计、派生视图、生成物和历史依据。
3. **判断碎片。** 用来源证据判断对象是残留、重复、分散还是错位，同时记录最有力的保留
   理由、影响和未知。没有引用、很久未改或文件很短都不足以证明失效。
4. **处置并收束。** 用户只要求 review 时交付发现和建议；要求整理时执行最小的完整修改，
   补齐入口、引用、构建和测试关系。沿同一个问题复查，说明已确认、未确认和验证边界。

## 按需读取

只在当前问题需要时读取 supporting docs：

- 需要判断证据和归属时读 [evidence.md](references/evidence.md)。
- 需要组织交付内容时读 [report.md](references/report.md)。
- 需要实际改动时读 [change-and-verify.md](references/change-and-verify.md)。

这些资料是本技能的操作参考，不是调研记录或第二份项目权威文档。项目级约定仍以当前仓库
的 `AGENTS.md`、模块 README 和实际源码为准；不要为了使用本技能加载与问题无关的整套文档。

## 不变量

- 保留他人的未完成改动；修改前后检查工作区状态和差异。
- 不删除用户数据、未确认失效的入口或仍承担回归价值的测试。
- 实现证明当前行为，设计说明目标；两者冲突时核对迁移状态，不能用其中一方替代另一方。
- 机械检查、运行时观察和用户验收分别报告；没有证据就保留未知，不把推测写成结论。
- 用户已经授权的局部整理直接推进；只有超出范围、改变公开契约或涉及不可逆动作时才停在
  边界说明。

## 完成条件

当原问题可以回到负责位置、相关引用已经闭合、必要修改和验证完成，并且未决依赖与重开
条件已写清时，结束本次局部整理。发现新的产品需求或更大范围争议时记录关联，不在本轮
偷偷扩张范围。

若清理前尚需决定各单元承担什么、怎样组合或拆分，按需使用
[architecture](https://github.com/lidessen/skills/blob/main/skills/architecture/SKILL.md)，提供当前消费者、有效承诺与冲突。
若既有机制的必要性或核心选择被反例击穿，使用 [design-forge](https://github.com/lidessen/skills/blob/main/skills/design-forge/SKILL.md)；
不要先清理掉它再论证合理性。若争议是重复校验究竟保护不同边界还是误阻工作，使用
[assurance-review](https://github.com/lidessen/skills/blob/main/skills/assurance-review/SKILL.md)。回到整理时沿用已核实的决定与证据，
不从头审查；链接不要求每次清理都加载相邻方法。
