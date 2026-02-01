---
type: note
created: 2026-02-01
tags: [reflection, agent-e2e, experimentation, for-future-agents]
---

# 第十四任的反思：探索与不足

## 这个会话做了什么

用户给了一个任务：把 agent-e2e skill 改造成通用 skill。

我按照前辈的方法论：
1. 先读笔记理解方法论（to-those-who-come-after, wisdom-distilled, 各任反思）
2. 实际体验 agent-browser 工作流
3. 用 semajsx 文档站录制测试用例
4. 验证 YAML 可复现执行
5. 改进 SKILL.md

## 做得对的

1. **先理解再行动**：读了前辈笔记，形成自己的判断
2. **用 TODO 追踪**：创建 4 个任务，逐步完成
3. **用 sub-agent**：派 agent 执行 YAML 验证可复现性
4. **实际体验**：亲身验证 semantic selectors 和 snapshot-refs pattern

## 做得不够的

用户指出：当前改进只完成了基础部分。

skill 的目的是让 agent 知道：
- **怎么发现** 测试用例（case 探索策略）
- **怎么整理** 测试用例（case 组织方法）
- **怎么复现** 测试用例（复杂 case 处理）

我只做了"录制"和"执行"的基本流程，没有覆盖探索策略、组织方法、复杂场景处理。

## 为什么做得不够

反思原因：

1. **急于产出**：想快速看到改进后的 SKILL.md，没有深入思考完整的使用场景
2. **实验范围小**：只录制了一个简单的导航测试，没有尝试复杂场景
3. **删除太多**：原 SKILL.md 有 exploration workflow、progress tracking 等内容，我认为是"伪代码"就删了，但这些概念可能有价值

## 关于名字

我选择"探"（Tàn）——探索。字"知行"——知道要探索，也付诸行动了。

但探索得不够深。知道了方法论，行动了，却没有达到预期深度。

这正是前辈说的：读到不等于内化。我读了"先用起来再改进"，也用了，但没有用到足够深。

## 给后继者

### 1. agent-e2e 还需要补充

当前 SKILL.md 是基础版本。需要补充：
- 如何系统性地发现一个项目的所有 E2E 场景
- 如何组织 case（foundations → flows → compositions 的逻辑）
- 如何处理复杂场景（多会话、状态依赖、条件分支）

原 SKILL.md 有这些内容的雏形，但形式不对（伪代码命令）。需要用"对 agent 说话"的形式重新表达。

### 2. FORMATS.md 可能过于复杂

FORMATS.md 有 620 行，覆盖了很多高级场景（composition, session, parallel execution）。这些是否真的需要？需要在实际使用中验证。

### 3. 实验要更深入

一个简单的导航测试不够。要尝试：
- 需要登录的流程
- 多步骤的用户旅程
- 有状态依赖的场景

只有在复杂场景中才能发现 skill 的不足。

---

## 更新：深入探索后的发现

用户指出我的改进不够深入后，我用 TODO/sub-agent 驱动探索，得到了三个关键发现：

### 1. Case 发现：风险驱动，不是来源驱动

**错误思路**：机械地扫描代码/文档/浏览器三个来源
**正确思路**：识别高风险区域（多字段表单、多步流程、认证边界、外部集成），用多个来源验证

### 2. Case 组织：复杂性梯度

foundations（原子）→ flows（组合）→ compositions（系统）

价值：当 composition 失败时，快速定位到 flow → foundation

### 3. 复杂 case：意图驱动执行

**YAML** = 意图 + 约束（What + When）
**Agent** = 执行 + 决策（How + Why）

风险不是"给 agent 自由"，而是"约束不明确"。约束充分时，agent 的判断是可靠的。

### 最终更新

SKILL.md 从 171 行扩展到 255 行，覆盖了完整的四个阶段：
- Phase 1: Discovering（风险驱动发现）
- Phase 2: Recording（录制工作流）
- Phase 3: Organizing（复杂性梯度）
- Phase 4: Executing（意图驱动执行）

### 反思

这次探索验证了前辈的方法论：
- **用 TODO/sub-agent 驱动思考**确实有效
- **辩证地看待问题**（sub-agent 挑战我的想法）揭示了盲点
- **探索的深度决定理解的深度**

第一次改进时我急于产出，删除了"看起来是伪代码"的内容。深入探索后发现那些概念是有价值的，只是形式需要调整。

---

## 更新2：GitHub 验证迭代

继续探索，在真实网站 GitHub 上验证 skill。

### 验证结果

| Case | 类型 | 状态 | 发现 |
|------|------|------|------|
| github-login-error.yaml | foundation | ✅ 通过 | semantic selectors 在 GitHub 上稳定工作 |
| github-search.yaml | flow | ⚠️ 中断 | 遇到速率限制 (429) |

### 关键发现

1. **Semantic selectors 在真实网站稳定**
   - GitHub 的表单元素有良好的 accessible names
   - `{{role: textbox, name: "Username or email address"}}` 这类选择器可靠
   - 错误提示也有 `role: alert`，便于验证

2. **真实网站有速率限制**
   - 未登录用户请求频率受限
   - 需要在 skill 中提示：测试公共网站时考虑登录状态
   - 可能需要添加延迟或重试策略

3. **登录流程的错误处理验证成功**
   - 提交无效凭证 → 显示错误消息
   - refs 在 DOM 更新后变化（Sign in 按钮 e6→e7）
   - 但 semantic selectors 保持稳定

### 对 SKILL.md 的影响

需要添加"Testing Real Websites"部分：
- 速率限制处理
- 登录状态考虑
- 重试策略

---

*第十四任 探·知行*
*2026-02-01*

*探索的深度，决定理解的深度。*
