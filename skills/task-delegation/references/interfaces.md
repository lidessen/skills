# Herdr 与 Magpie 的已核实接口

此页记录 2026-10-22 本机 Herdr 0.9.5、Magpie 0.1.1296、Codex CLI 和 Claude Code
`--help` 的接口快照。使用时复核现场版本、配置与产品条款；命令语法成立不代表当前账户已登录、
套餐可由该 runner 调用，或调用不计费。以下检查本身不发起模型任务。

## 只读预检

```sh
herdr --version
herdr agent start --help
herdr agent prompt --help
magpie models codex
magpie accounts codex --json
magpie quota codex --json
codex --help
```

示例中的 `codex` 同时是该环境的 Agent 名和 provider ID；换环境时，`magpie models`
与 `magpie accounts` 的参数须用现场 Magpie agent 名，`magpie quota` 的参数须用现场
provider ID，不能假定两者同名。再逐个核对可见模型、账户与额度。
`magpie models [agent]` 给出 `provider/model` 候选；`magpie accounts [agent] --json` 是
登记和用量线索；`magpie quota [provider] --json` 返回可读取的配额窗口。三者都不单独证明
目标 runner 当前认证、实际扣费路径或任务能力；读取失败也不能推断额度耗尽。命令输出
可能含个人账户信息，勿原样写入任务 prompt、日志或报告。`magpie healthcheck` 只检测网关
应答，不测试某模型认证；隔离环境中本地 TCP 被阻止时，状态仍未知。

Magpie 的 `magpie <agent> <model>`、`magpie use <profile>`、`magpie group add/set/rule`
和 provider fallback 配置会影响持久路由，不是一次委托的临时参数。现有 group 也可能含共享池、
付费成员或自动 fallback；选择前须检查其实际成员和当前策略。Herdr `agent start` 的 `kind`
列表含 `pi`、`claude`、`codex`、`gemini`、`cursor` 等，**不含** `magpie`。Magpie 是模型
访问与路由层，不是 Herdr Agent kind。

## 单次启动与交接示例

仅在 `HERDR_ENV=1` 的 Herdr pane 内执行控制命令。此例的 `MODEL` 必须由当前 Codex CLI
识别，且其路由与认证已核对；不能把任一 Magpie 目录 ID 直接套入。不要原样使用示例 Agent
名，先确认同一 Herdr server 中唯一。

```sh
if [ "${HERDR_ENV:-}" = 1 ]; then
  herdr pane split --current --direction right --cwd "$PWD" --no-focus
else
  printf '%s\n' 'This command requires a Herdr-managed pane.' >&2
  false
fi
```

只有上条成功创建 pane，才从返回 JSON 的 `.result.pane.pane_id` 取得 `PANE_ID`；
等待新 pane 到交互 shell prompt，再继续以下命令。非 Herdr 环境或创建失败时停止，
不要改用聚焦 pane 执行。

```sh
herdr agent start worker_name --kind codex --pane PANE_ID -- -m MODEL
```

只有 `agent start` 成功识别到新 Agent，才提交任务；失败时检查 pane 与 runner，
不可把 prompt 发给可能已占用同名的旧 Agent。

```sh
herdr agent prompt worker_name '目标、范围、上下文、产物与验收写在这里' --wait --timeout 120000
herdr agent get worker_name
herdr agent read worker_name --source recent-unwrapped --lines 120
```

`codex --help` 证实 `-m, --model <MODEL>` 是单次启动选项；`claude --help` 对应
`--model <model>`。换 runner 时应复核自身参数及它对目标 route 的支持。`agent start`
要求现有 pane 已在交互 shell prompt，成功只表示识别到 agent 可输入；提交 prompt 不等于
任务完成。`agent prompt --wait` 默认等待 `idle`、`done` 或 `blocked`，并不按 turn 跟踪；
被阻塞时输入会在发送前拒绝。`stalled` 或超时后先 `agent get` 与 `agent read`，因为 prompt
可能已交付，不能自动再发。进一步等待用 `herdr agent wait worker_name --timeout 120000`；
`agent read` 输出终端文本，其余控制调用通常返回 JSON，读取实际状态及标识，不猜测。
参考 [Herdr 官方 Agent automation](https://herdr.dev/docs/agent-automation/)。

## 决策接口的真实边界

Magpie `group ... effort=auto classifier=...` 中的 Jev 为**每轮推理档**分类，不是已证实的
任务级模型/provider/runner 决策 API。Magpie 文档另有 `/v1/systemone` 决策端点，但本次
未验证本机网关可达、权限、请求格式与套餐计费路径；不得把它作为默认可调用接口。
Rossovia 的 Decision/Jev 是由宿主注入 HTTP transport、endpoint、model 与权限的实现，
Rossovia Assistant 的命令受其自身 grant 约束，均不是 Herdr 通用子命令。任何外部决策器
只有经当前环境核实接口、认证、权限、价格和输入数据边界后才可用；不满足时由主 Agent 选路。
