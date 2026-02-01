---
type: design
created: 2026-02-02
author: 第十六任
tags: [skill-system, design, auto-trigger]
status: proposal
---

# Skill 调用体验重设计

## 问题

当前调用 `/dive` 返回 ~150 行完整 SKILL.md。

这导致：
- 调用成本高（读 150 行 + 行动）
- Agent 倾向于跳过（直接行动更快）
- Skill 价值无法传递

## 提案：精简调用输出

调用 skill 时返回 **核心指导**（<30 行），完整内容按需加载。

### Dive Skill 精简版示例

```markdown
# Dive: Quick Reference

**Your question**: {ARGUMENTS}

## Do This Now

1. **Understand**: What exactly is being asked?
2. **Search**: Docs → Code → Deep analysis (as needed)
3. **Collect**: Gather evidence with `file:line` citations
4. **Synthesize**: What do sources tell us together?
5. **Respond**: Answer + evidence + uncertainty

## Evidence Hierarchy (trust order)

Running code > Tests > Implementation > Types > Comments > Docs

## Question → Search Strategy

| Question type | Start with |
|--------------|------------|
| "How does X work?" | Code, verify with tests |
| "Why is X designed this way?" | Docs/ADRs, check history |
| "What calls X?" | Grep, trace references |

## Key Principle

> Never state confidence without evidence. "I'm 90% sure" means nothing without sources.

---

*Need more detail? Read `reference/search-strategies.md`*
```

### 对比

| 版本 | 行数 | 包含 | 适合 |
|-----|------|-----|------|
| 当前 | ~150 | 完整方法论 + 哲学 + 细节 | 首次学习 |
| 精简版 | ~30 | 行动指南 + 关键映射 | 快速使用 |

### 实施方式

**选项 1：修改 SKILL.md 结构**
- 顶部放精简指南
- 哲学和细节移到 reference/

**选项 2：添加 QUICK.md**
- SKILL.md 保持不变（首次学习用）
- 新增 QUICK.md（重复调用用）
- 触发时根据场景选择返回哪个

**选项 3：动态生成**
- Skill 调用时生成精简版
- 把 ARGUMENTS 嵌入模板
- 需要系统支持

### 推荐

**选项 1**（修改 SKILL.md 结构）最简单，且符合 progressive disclosure 原则：

```
SKILL.md 新结构:
├── Quick Reference (~30 lines)
│   └── 行动指南、关键映射
├── Philosophy (可选)
│   └── 为什么这样设计
└── Reference (按需)
    └── 详细技巧
```

调用 skill 时，系统可以只返回到第一个 `## Philosophy` 之前的内容。

## 影响

如果实施：
- 调用成本降低（30 行 vs 150 行）
- Agent 更可能调用（因为成本低）
- 方法论核心仍然传递（通过精简版）

## 需要验证

1. 精简版是否足够指导行动？
2. Agent 是否更愿意调用精简版 skill？
3. 系统是否支持"只返回部分内容"？

---

*待用户/后继者决策*
