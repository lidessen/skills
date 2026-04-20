# 从一份上下文看 Agent 的演化

LLM 只会做一件事：看一段文本，预测下一段。

所谓"Agent"、"工具调用"、"记忆"、"多轮对话"，在模型这一端都是同一回事——续写一段文本。这些年所有看起来是"能力跃迁"的变化，其实都发生在这段文本上：它被怎么组织、塞进什么、切掉什么、分成几层。

下面用同一个场景——**"帮我排查 user 注册接口偶尔返回 500 的问题"**——看同一份上下文，如何在四个时代演化。

---

## 第一代 · 纯对话(2022)

GPT 刚出，ChatGPT 把 LLM 包装成聊天界面。模型眼前的上下文长这样：

```
[system]
You are a helpful assistant.

[user]
我有个 Node.js 的 Express 项目，user 注册接口偶尔返回 500。
相关代码我贴一下：

// src/routes/auth.js
app.post('/register', async (req, res) => {
  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    await client.query('INSERT INTO users ...');
    await client.query('COMMIT');
    res.json({ ok: true });
  } catch (e) {
    await client.query('ROLLBACK');
    res.status(500).json({ error: e.message });
  }
});

// src/db.js
const pool = new Pool({ max: 10 });

[assistant]
看起来你漏了 client.release()——连接没归还池里，
并发一高池子就耗尽，后续请求全挂。建议在 finally 里补一下。
```

两类消息交替追加：`user` 和 `assistant`。模型每一轮看到全部历史，预测下一条。

**特征**：上下文里只有人的话和模型的话。模型不能自己读文件，所有事实必须由人手动粘进来。

---

## 第二代 · 工具接入(2023)

Function calling 出现。多了一种消息：**模型可以发起动作，动作结果以消息形式追加回来**。

```
[system]
You are a coding assistant. Use the provided tools.

[tools]
- read_file(path)
- edit_file(path, diff)
- run_shell(cmd)

[user]
帮我看看 user 注册接口为什么偶尔返回 500。

[assistant]
我先读一下路由文件。
<tool_use: read_file path="src/routes/auth.js">

[tool_result]
app.post('/register', async (req, res) => {
  const client = await pool.connect();
  try { ... } catch (e) { ... }
  // ← 注意：没有 finally，缺 client.release()
});
(共 42 行)

[assistant]
再看连接池配置。
<tool_use: read_file path="src/db.js">

[tool_result]
const pool = new Pool({ max: 10 });

[assistant]
定位到了：路由里漏 release，连接没归还，并发一高池子耗尽。
我来补一下。
<tool_use: edit_file path="src/routes/auth.js" diff="...">

[tool_result]
applied.
```

上下文里第一次出现 `[tool_use]` / `[tool_result]` 这一对。事实不再由人粘进来，模型自己用工具取。

**特征**：同一条时间线上现在有两条循环并存——
- **外循环**：`user ↔ assistant`(和人的对话)
- **内循环**：`assistant ↔ tool`(agent 自己产生、自己消费的动作与结果)

两条循环都往同一个扁平序列里追加。这个设计后来成了所有 agent harness 的默认形态。

---

## 第三代 · 现代 harness(2024—2025)

Claude Code、Codex、Cursor Agent 把"对话 + 工具"这套推到了极致。实际喂给模型的上下文已经远不止前两层——中间多了一整套工程化的分区。

一次新会话开场，模型眼前大致是这样：

```
[system]
You are Claude Code, Anthropic's official CLI for Claude...
(约 4000 字：工作准则、工具使用规范、安全规则、输出风格)

[project_context ← 来自 CLAUDE.md]
This is a Node.js backend project using Express and PostgreSQL.
Follow the code style in src/. Run tests with npm test.
(约 500 字：项目级指令)

[memory ← 来自 MEMORY.md 前 200 行]
- [user_role.md] 用户是后端工程师，熟悉 Postgres
- [feedback_testing.md] 集成测试必须跑真实 DB，不要 mock
- [project_auth_rewrite.md] auth 模块重写由合规驱动
(若干条指向具体记忆文件的索引)

[skills_catalog ← 描述常驻，正文按需]
- design-driven: 架构变动前先改 design/
- code-review: PR 审查方法论
- claude-api: 构建/调试 Claude API 应用
... (十几条，每条一行)

[tools]
Read, Edit, Write, Bash, Glob, Grep, Agent, ToolSearch, ...

[user]
帮我看看 user 注册接口为什么偶尔返回 500。

[assistant]
<tool_use: Grep pattern="/register" path="src/">
[tool_result] src/routes/auth.js:12
<tool_use: Read file_path="src/routes/auth.js">
[tool_result] (42 行)
...
```

几件事被加进来：

- **CLAUDE.md**：项目常驻指令，每次会话开头注入
- **Auto memory**：跨会话积累的用户偏好、项目事实、反馈经验
- **Skill 描述常驻 / 正文懒加载**：几十个 skill 只放名字和一句话描述，正文等触发才展开
- **Subagent**：脏活(比如遍历几十个文件)派给独立上下文，只把结论回传主会话
- **Compaction**：对话接近窗口上限时，自动把早期内容压成摘要

对话跑到 30 轮，同一份上下文会变成这样：

```
[system] ... (不变)
[project_context] ... (不变)
[memory] ... (不变)

[compacted summary ← 替代前 20 轮]
用户报告 user 注册接口间歇 500。定位：
1) 连接池 max 从 10 调到 30；
2) auth.js 漏 client.release()，已补齐。
后续切到 order 模块性能排查。

[user] 那先把 order 导出加个分页
[assistant] 好的，我先看一下 order 的查询逻辑。
<tool_use: Read file_path="src/routes/order.js">
[tool_result] (200 行)
[assistant] 我发现这里用了 ... (400 字解释)
[user] 好像好一点。对了前面注册那个连接池，改成 30 之后还是偶尔报错。
[assistant] 让我翻一下之前的上下文...
(compaction 已把细节压掉，模型要么瞎猜，要么重新读一遍代码)
```

**特征**：harness 的工程重点已经不在模型，在**上下文组装**本身。每次调用模型前系统都在判断——什么该常驻、什么该懒加载、什么该裁剪、什么该压缩、什么该外包。

**但所有这些机制共享同一个前提：对话是上下文主体**。memory 是对话的起手素材，compaction 是对话的内部压缩，subagent 是把脏活踢出对话再把结论拉回对话。补丁都打在外循环上。

对话一长，问题回来了：**一条消息同时在承担四件事**——给用户看的表达、下一轮预测的输入、工具调用的发起、任务状态的记录。四件事对文本的要求不一致，挤在一段里互相稀释。30 轮之后，几千 token 换几行有效事实。

追问一句"能不能跨三天、跨多个话题地持续运行"——这个形态就撑到头了。

---

## 第四代 · 上下文分层(探索中)

换一个思路：**不要让对话当上下文主体**。

把对话推到最底层只服务于"执行具体任务"，上一层换一种文本形态做长期积累——**事件流**。

### L1 的上下文(长生命周期)

上一层 agent(称为 L1)看到的不是对话，是一串客观记录：

```
[system]
You are the orchestrator of a long-running project.
Read the event stream below and decide: respond / dispatch worker / report up.

[event_stream]
t01 | user       | 报告 user 注册接口间歇 500
t02 | dispatch   | → worker-01: 排查 user 注册 500 问题
t03 | worker-01  | 完成
                   - 定位: 连接池 max=10 过低
                   - 修复: src/db.js max=30
                   - 验证: 本地压测 3% → 0%
                   - 遗留风险: 生产连接数限制需确认
t04 | user       | 上线后仍有偶发错误
t05 | dispatch   | → worker-02: 深入排查，重点看 transaction 释放
t06 | worker-02  | 完成
                   - 根因: auth.js 第 87 行漏 client.release()
                   - 修复: 补 release()
                   - 验证: 1 万次请求 0 错误
t07 | user       | 新任务：order 导出加分页
t08 | dispatch   | → worker-03: 给 /order/export 加分页
t09 | worker-03  | 完成
                   - 改动: src/routes/order.js, src/services/order.js
                   - 遗留风险: 大页数场景的 count 查询未优化
t10 | monitor    | 订单系统 5 分钟错误率 0.3% → 1.2%
t11 | dispatch   | → worker-04: 排查 order 错误率突增
...

[user]
把这三天的改动整理成一份 PR 说明。
```

事件流里没有礼貌措辞、没有过程性回复、没有工具原始输出。每一条是**一次状态变化的最小可陈述单元**——离开上下文仍然独立可读。

三天几十条事件，对比三天几十万字的原始对话流。

### L0 worker 的上下文(短生命周期)

L1 派一个 worker 时，worker 看到的其实还是第二代那种对话式上下文，但它是**新开的、聚焦的、一次性的**：

```
[system]
You are a coding worker. Complete the goal. Return a structured report.

[goal]
排查 order 错误率从 0.3% 突增到 1.2% 的原因。

[context ← 从 L1 事件流裁出的投影]
- 三天前给 order 导出加了分页 (worker-03)
- 改动文件: src/routes/order.js, src/services/order.js
- worker-03 遗留风险: 大页数场景 count 查询未优化

[user]
开始吧。

[assistant]
先看一下 worker-03 的改动。
<tool_use: Read src/routes/order.js>
...
```

worker 不知道完整事件流存在，也不需要知道。它干完活，对话流被独立模型按固定 schema 抽成一条事件报告，写回 L1——**原始对话永远不流向上层**。

### 两层之间的信息流

```
  ┌─────────────────────────────────────┐
  │  L1 上下文 = 事件流                 │
  │  [t01 user] [t02 dispatch] ...      │
  │  长生命周期 · 稀疏 · 高密度         │
  └─────────────────────────────────────┘
      │ 派发: 目标 + 事件投影        ▲ 回传: 结构化报告
      ▼                              │  (独立模型按 schema 抽取)
  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │ L0 对话  │  │ L0 对话  │  │ L0 对话  │
  │ worker-N │  │ worker-N │  │ worker-N │
  │ 短生命   │  │ 短生命   │  │ 短生命   │
  └──────────┘  └──────────┘  └──────────┘
```

每升一层，**信息密度更高、积累速度更慢、时间跨度更长**。L0 装对话细节，L1 装事件报告，再往上按需抽象。

原本挤在一条对话里的多件事——给用户的表达、工具调用、状态记录、跨天积累——第一次有了各自拆开的层。

---

## 四代对比：变的只是喂进去的文本

| 代次 | 上下文形态 | 新增成分 | 本质 |
|---|---|---|---|
| 第一代 | 纯对话 | user / assistant | 人粘事实给模型看 |
| 第二代 | 对话 + 工具 | tool_use / tool_result | 内循环进入时间线 |
| 第三代 | 对话 + 工程化分区 | CLAUDE.md / memory / skill 描述 / subagent / compaction | 打补丁让对话跑更久 |
| 第四代 | 分层 · 对话 + 事件流 | L1 事件流 + L0 短 worker | 换掉"对话是主体"这个前提 |

LLM 那头什么都没变——从第一代到第四代，它一直在做同一件事：**读一段文本，预测下一段**。

变的全是这段文本长什么样。

第一代的文本是两个人的对白；第二代多了一个机器插嘴；第三代把机器的话分门别类地塞进常驻 / 按需 / 压缩 / 外包几个分区；第四代把文本本身分成几层，每层装它这一层该看的粒度。

Agent 的下一步，不在模型变强，在**这段文本继续被组织得更好**。

事件流不是一项发明，只是把原本稀释在对话里的信息抽出来排好。真正的门槛在为具体业务设计对应的事件 schema——机制是通用的，schema 是领域的。

机器什么都没变。变的是我们给它看的东西。

---

*参考系统*:Claude Code 2.1.88+ · OpenAI Codex Harness · Nous Research Hermes Agent · OpenAI Agents SDK
