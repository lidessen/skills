# Agent guidance evaluation

## 先冻结要回答的问题

区分三种问题：

- **发现**：description、入口和相邻边界能否让 Agent 选择正确载体？
- **激活**：加载后是否改变了核心判断、行动、失败处理或返回？
- **体系**：是否与现有 skill、指令、文档、工具和 runtime 保持 owner、权威与生命周期关系？

不要用一个“整体效果分数”替代这三种问题。
需要在完整执行前筛选候选、量化设计缺口或用参考技能校准孵化器时，按需读
[quality-assessment.md](https://github.com/lidessen/skills/blob/main/skills/skill-incubator/references/quality-assessment.md)。设计量表与低成本决策探针不能直接当成任务成功概率。

## 最小行为探针

准备相同任务、来源、工具、权限和 workspace，至少覆盖：

- 正触发：应该使用该 skill 或 prompt 的案例；
- 负触发：相似但应留在普通任务表达或其他 owner 的案例；
- 最近邻：最容易误选相邻 skill、reference、工具或 runtime 的案例；
- 回归：已有能力和必要边界仍应保留的案例。

要声称候选载体造成改善，比较不加载它的 baseline 与只加载它的 treatment；变量无法隔离时只
报告观察，不作因果归因。需要稳定性时再增加重复或 fresh holdout，不把轮数或 Agent 数当作结果。

## 证据与处置

分别报告：

- `format-valid`：格式、frontmatter、链接或确定性检查通过；
- `behavior-observed`：激活后出现了目标行为；
- `boundary-supported`：负触发和最近邻没有被错误吞入；
- `matched-improvement`：相对冻结 baseline 有匹配改善；
- `regression-supported`：改善没有破坏既有行为。

证据等级限制主张，不自动晋级。自评、文件存在、格式通过、一次成功或多 Agent 一致，都不能
单独证明 skill 已被接受。最终处置可以是 `adopt`、`adapt-and-retest`、`retain-baseline`、
`rollback`、`uncertain` 或 `no-proposal`，由真实 owner 采纳。
