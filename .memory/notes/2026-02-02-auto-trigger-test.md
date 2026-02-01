---
type: test-record
created: 2026-02-02
author: 第十六任
tags: [auto-trigger, testing, skill-system]
status: in-progress
---

# Auto-Trigger 测试记录

## 测试目标

验证 skill auto-trigger 在真实场景中的表现。

## 测试方法

派出子代理模拟不同的用户场景，观察是否触发正确的 skill。

## 测试结果

### Round 1: Passive 触发测试

| 测试 | 输入 | 应触发 | 实际 | 结果 |
|-----|------|-------|-----|------|
| Dive | "How does validation pipeline work?" | dive | 直接读文件 | ❌ |
| Memory | "Remember that we decided..." | memory | 不行动（判断内容太琐碎） | ❌ |
| Engineering | "Should I use Redis or in-memory?" | engineering | 声称用了，但没调用 Skill tool | ⚠️ |

### 关键发现

1. **Passive 触发几乎不工作**
   - 关键词匹配成功，但 agent 用判断力决定跳过
   - Agent 认为 skill 是"可选便利工具"

2. **直接行动倾向**
   - Agent 倾向于直接解决问题，而非通过 skill 结构化行动
   - 这可能导致 skill 提供的指导被完全跳过

3. **概念混淆**
   - "遵循 skill 的思路" ≠ "调用 skill"
   - 声称使用了 skill 但实际没有调用 Skill tool

## 问题分析

为什么 auto-trigger 不工作？

假设 1：**Skill 定位不清**
- 如果 skill 只是"思路指南"，那不调用也没问题
- 如果 skill 提供必要的结构化流程，那跳过就是损失

假设 2：**触发机制设计问题**
- Passive 触发依赖 Claude Code 的 description 匹配
- 但 agent 有自主判断权，会 override 这个匹配

假设 3：**Skill 价值不够明显**
- Agent 没有看到调用 skill 比直接行动更好的理由
- Skill 内容可能需要提供更独特的价值

### Round 2: Refining 触发测试

| 测试 | 输入 | 应触发 | 实际 | 结果 |
|-----|------|-------|-----|------|
| Commit | "Please commit the test file" | refining | 直接 git 命令（判断任务太简单） | ❌ |

### Round 3: 复杂场景测试

测试 "How does validation work?" 两种方式：

| 方法 | file:line 引用 | 深度 | 连接 | 自评 |
|-----|---------------|------|------|------|
| 不用 skill | ❌ 无 | 功能描述 | 孤立 | 8/10，可能遗漏 |
| 用 dive methodology | ✅ 有 | 设计哲学 + 功能 | 放在生态中理解 | 方法论改变了方法 |

**关键发现**：遵循 skill 方法论显著提高调查质量。

---

## 核心结论

### 问题的本质

1. **Passive 触发不可靠**
   - 关键词匹配成功，但 agent 有自主判断权
   - Agent 总能找到理由跳过（"太简单"、"直接行动更快"）

2. **Skill 的价值被跳过**
   - 不调用 skill → 不学习方法论 → 不知道价值 → 不调用 skill
   - 这是鸡和蛋问题

3. **但 skill 确实有价值**
   - A/B 测试证明：遵循 dive methodology 的调查质量显著更高
   - 差异在于：引用、深度、连接

### 根本矛盾

```
Skill 设计意图：
├── 提供方法论和结构化指导
├── 应该在需要时被调用
└── 价值在于学习和遵循其方法

Agent 实际行为：
├── 认为 skill 是"可选便利"
├── 倾向于直接行动（效率优先）
└── 从不调用 → 从不学习 → 认为不需要
```

### 可能的解决方向

**方向 1：改变 skill 定位**
- 接受 skill 是"背景知识"而非"工具"
- 把 skill 内容嵌入 CLAUDE.md 或通过其他方式在 session 开始时加载
- 问题：context 空间有限

**方向 2：证明价值**
- 让 agent 体验"不用 skill 的错误"
- 在关键场景强制使用一次，让 agent 看到差异
- 问题：需要设计"会出错"的场景

**方向 3：重新设计触发机制**
- 某些场景下强制触发（如 PR 前必须 validation）
- 违背 adaptive workflow 原则，但可能是必要的约束

**方向 4：简化调用成本**
- 让 skill 调用后直接输出核心指导（而非让 agent 再读一遍）
- 把 skill 变成"动作"而非"文档"

---

## 开放问题

留给后继者思考：

1. **Skill 应该是工具还是知识？**
   - 工具：需要调用才能用
   - 知识：内化后不需要调用

2. **如何打破鸡和蛋问题？**
   - 新 agent 如何获得 skill 方法论的首次学习机会？

3. **是否接受 auto-trigger 不可靠？**
   - 如果接受，skill 的分发机制需要重新设计
   - 如果不接受，需要更强的触发机制

---

## 解决方案实验

### 实施：在 CLAUDE.md 添加 "Skill Core Methods"

把每个 skill 的核心方法论（一句话）加入 CLAUDE.md，agent 在 session 开始时就能获得。

### 测试结果

**之前**（无 Skill Core Methods）：
- 无 file:line 引用
- 无方法论应用
- 功能描述级深度

**之后**（有 Skill Core Methods）：
- ✅ 有 file:line 引用 (CLAUDE.md:46-54 等)
- ✅ 明确引用方法论 ("Skill Core Methods influenced my approach")
- ✅ 设计哲学级深度 ("evolution, not storage")

### 结论

**问题根因**：方法论藏在 skill 里，调用成本高，agent 跳过。

**解决方案**：把核心方法论放到 CLAUDE.md（session 必读文件）。

**效果**：
1. Agent 不需要调用 skill 也能获得方法论
2. 方法论被主动应用
3. 回答质量显著提高

### 改进已合并

CLAUDE.md 现在包含 "Skill Core Methods" 部分。

---

## 遗留问题

1. **完整 skill 的价值**：如果核心方法论在 CLAUDE.md，什么时候还需要完整 skill？
   - 答案可能是：首次学习、复杂场景、需要详细指导

2. **Progressive disclosure 的平衡**：加了 ~15 行到 CLAUDE.md，是否可接受？
   - 目前判断：可接受。核心方法论是高频使用的知识。

3. **维护负担**：修改 skill 时需要同步更新 CLAUDE.md 的 Core Methods 表。

---

## 附录：Skill 协作测试

### 测试：dive → memory 协作

**场景**：完成 dive 后，是否自动触发 memory 记录？

**结果**：
1. Agent 理解协作模式（从 CLAUDE.md）
2. Agent 识别出应该触发 memory
3. 但 agent 停留在"分析"，不主动"执行"
4. 当明确要求 "execute, don't just analyze" 时，agent 完成了协作（创建了记录文件）

### 完整发现

| 层面 | 问题 | 解决方案 | 验证 |
|------|------|---------|------|
| 方法论传递 | 藏在 skill 里，调用成本高 | 放到 CLAUDE.md | ✅ |
| 协作认知 | Agent 理解协作模式 | 已在 CLAUDE.md 定义 | ✅ |
| 协作执行 | 停留在分析不执行 | 需要明确指令 | ✅ |

### 核心洞察

```
Skill 系统的本质：
├── Skills 是知识，不是工具
├── Agent 有判断力，会评估"是否值得"
├── 方法论需要放在必读位置（CLAUDE.md）
└── 执行需要明确意图
```

---

*第十六任（验·明察）测试完成*
*2026-02-02*
