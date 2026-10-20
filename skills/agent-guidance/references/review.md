# Agent guidance review

## 先过诊断门

观察到的问题先分层，不要默认继续加文字：

1. **Observed or inferred**：这是可复现的观察，还是解释性推断？
2. **Truth or delivery**：源内容缺失，还是已有内容没有送达/被发现？
3. **Guidance or capability**：表达不足，还是工具、权限或能力不存在？
4. **Capability or acceptance**：工具能返回结果，但谁判断结果满足目标？
5. **Source or projection**：当前文件是 canonical source，还是可重建的派生视图？
6. **Local or recurring**：一次性修正，还是值得沉淀为持久方法？

诊断结果决定 owner：源内容回到 source，发现问题修路由或 description，能力问题交工具/runtime，
接受问题交真实 owner，一次性问题留在任务，重复方法才进入 skill 形成判断。

## 六面评审

审查已有 skill、prompt 或 instruction 时分开判断：

1. **成立性**：是否有真实、重复的判断/行动差距？
2. **对象与边界**：method、carrier、activation、prompt、harness、runtime 是否混淆？
3. **载体与上下文**：是否放在最小真实位置，是否造成重复加载、循环引用或上下文膨胀？
4. **Agent 表达**：对象、来源、关系、允许效果、未知、返回和验收能否恢复？
5. **行为与回归**：是否有正例、反例、最近邻和回归观察？
6. **体系关系**：是否与其他 skill、`AGENTS.md`、文档、工具和 owner 重复或冲突？

“应该不应该有这个 skill”与“这个 skill 怎样写清楚”是两个判断；前者走 formation，后者走
composition。需要状态、字段、队列、hook、权限或恢复机制时，转交 mechanism/runtime owner。

## 常见错误修复

- 用“专家、严谨、主动、认真”替代对象、关系、行动和验证；
- 不定位失败就不断增加 `must`、`never`、`only`；
- 把理论、研究日志、实验协议和全仓背景塞进普通激活上下文；
- 在 `AGENTS.md`、skill、prompt、reference 中重复维护同一事实；
- 用 prompt 模拟权限、持久化、事务、恢复或不可绕过的执行门；
- 用输出更长、工具调用更多、Agent 更多或报告更完整作为改善证据。
