# Fx：单次调用与 Herdr 多轮委托

Fx 可以是短任务的轻量候选；“更快”仍须用相同任务条件下的端到端耗时、质量和失败率验证，
不能由 runner 名称推断。先按主技能的策略确认任务能力、当前认证与计费通道。Fx 的
[认证说明](https://fx.sh/docs/getting-started/authentication)列出 Codex/Grok 套餐登录及
AI Gateway 的账户或 API 凭据；安装或选择 provider 都不证明当前请求会扣套餐。
`FX_PROVIDER` 和 `--model` 可为单次请求选 provider/model；检查当前身份和 Gateway 的
fallback 后再用。`--ultrafast` 属更高价格档，不能未经付费授权启用。见
[fx ask](https://fx.sh/docs/using-fx/fx-ask)。

## 一次性任务：按进程与 JSON 回执收结果

在已安装、已认证且任务允许的环境中，主 Agent 可从项目工作目录运行
`fx ask --json --model "$MODEL" "$TASK"`；`MODEL` 与 `TASK` 必须先按策略确定。
它是一次非交互请求，结束即退出。检查**进程退出码**和 JSON `exit_code`，再读
`final_output`、`session_id`、错误与产物；`final_output` 可能为空，成功退出也不代替
任务验收。需要后续接续时保留实际返回的 `session_id`，按
[会话文档](https://fx.sh/docs/using-fx/sessions)用 `fx ask --resume ID` 或
`fx resume ID`，可用 `fx sessions --all`、`fx session ID --json` 查证。
有意使用 `--no-save` 时 `session_id` 为空且不可恢复；按[全局日志](config-log.md)
保留空的 runner session ID，并在简短状态或描述中注明不可恢复，不安排后补。
只有预期保存但回执暂未知时，才将缺失 ID 记为 `pending` 并尝试补查真实 ID；
不拿 Herdr pane ID 或自造 ID 顶替。

`fx ask --json` 要交互审批时须在真实终端中显式使用 `--prompt-permissions`；管道或重定向
输入不能接收审批提示。不要假设短命进程可提供持续的 `blocked` 状态；进程退出后也不能
向它 `agent prompt`。在 Herdr 中用已核实的 `herdr pane run PANE_ID COMMAND...` 只能
启动普通 pane 命令，不会因此获得 Agent 生命周期；`pane read` 读的是终端文本，
`agent wait` 的状态也不是结果验收。若需要稳定的结构化 JSON，直接捕获 Fx 子进程的
stdout 与退出码，而不是把 `pane run` 的确认回执当成 Fx 结果。见
[Herdr 智能体自动化](https://herdr.dev/zh-cn/docs/agent-automation/)。

## 多轮任务：使用薄适配器

Herdr 0.9.5 的 `agent start --kind` **没有 `fx`**。本技能的
`scripts/fx_bridge.py` 提供 `task-delegation-fx-bridge` 命令入口：它在 Herdr pane 中
长驻、逐行接收终端输入，每轮调用一次 `fx ask --json`，然后继续等待下一轮。Fx CLI
子进程可以结束，但适配器必须继续运行，Herdr 才有可等待和可恢复的当前 Agent。
安装或链接这个入口须由主 Agent 按当前任务授权完成，且**目标 pane 的 `PATH`** 与
Herdr 恢复后的 `PATH` 都必须能找到同名命令。源码存在不表示入口已安装；先在目标
环境核对 `command -v task-delegation-fx-bridge`，并确认该命令解析符号链接后指向
**本次运行的同一个适配器脚本**；否则不能登记 Herdr 恢复 argv。不要写
`agent start --kind fx`。

先按策略核对 provider、精确模型、认证、套餐与 fallback，确认适配器会继承的 Fx 配置。
`start` 可选 `--fx-home ABS` 指向已有 Fx 配置家目录、`--fx-bin ABS` 指向已安装的
Fx 可执行文件；`--no-additional-dirs` 限制额外工作目录，`--clean-fx-env` 适合隔离
测试时只传必要环境变量。这些选项不复制凭据，也不能替代项目上下文与工具权限检查。
恢复会记住这些路径、provider 和模型，但配置文件以后
可能被人修改，因此接续前仍要重新核对实际路由。
仅在 `HERDR_ENV=1` 的 Herdr pane 内由主 Agent 创建独立 pane，从返回 JSON 的
`.result.pane.pane_id` 读取真实 ID；
等待该 pane 处于 shell prompt 后运行适配器。以下是命令形状，`PROJECT`、`DESCRIPTION`
与 `MODEL_ID` 换成已核实的值，动态文字须按 shell 规则安全引用，不把任务全文写到
`--description` 中：

```sh
created=$(herdr pane split --current --direction right --cwd "$PWD" --no-focus)
PANE_ID=$(printf '%s\n' "$created" | jq -r '.result.pane.pane_id')
herdr pane run "$PANE_ID" \
  "task-delegation-fx-bridge start --project PROJECT --description DESCRIPTION --provider PROVIDER --model MODEL_ID"
herdr pane wait-output "$PANE_ID" --match FX_BRIDGE_READY --timeout 30000
herdr agent get "$PANE_ID"
herdr agent read "$PANE_ID" --source recent-unwrapped --lines 40
```

`pane run` 只确认命令已送入终端。等适配器上报 `idle`，并从终端的
`FX_BRIDGE_READY` 行读取真实 `task_ref` 后，才提交一行完整任务；一行中仍要交代
目标、范围、上下文、产物与验收，不能直接发送含原始换行的 prompt，因为适配器逐行接收。
较长的上下文应给明确的可读文件路径和范围，避免把整篇内容挤进一条终端输入。

```sh
herdr agent prompt "$PANE_ID" '一行内写清目标、范围、产物和验收' --wait --timeout 120000
herdr agent get "$PANE_ID"
herdr agent read "$PANE_ID" --source recent-unwrapped --lines 120
task-delegation-fx-bridge inspect --task-ref ACTUAL_UUID
```

适配器将精简的 `FX_BRIDGE_RESULT` 印到 pane，不把模型正文复制到终端摘要；
私有状态文件存 Fx 的 JSON 回执，`inspect` 读取最近一轮状态与 `final_output`。
确认进程退出码、JSON `exit_code`、`final_output`、
真实 `session_id` 与产物，再按任务验收，不能仅凭 Herdr 的 `idle`、`done` 或
`agent prompt --wait` 认定完成。Herdr 的 `agent prompt` 从非 working 状态提交后需要
在五秒内观察到 `working` 或 `blocked`；若超时或 `agent_prompt_stalled`，先读 pane
和 `inspect`，不要自动重复提交。`agent wait` 不跟踪独立轮次，已有其他轮次在运行时
尤其需要核对 `task_ref` 与回执。

适配器只在 Herdr 确认环境变量齐全时自报，使用不与内建 adapter 冲突的稳定 `source`
和递增 `seq`。真开始 Fx 请求时上报 `working`；成功回执落盘且适配器可接收下一行时
才上报 `idle`。任一轮失败会保存回执、上报 `unknown` 并退出，随后释放 pane 的 Agent
身份；此时 `agent prompt --wait` 可能以 Agent 消失结束，必须用 `inspect` 查原因，
不可自动重发。不能可靠判定审批或提问时不虚报 `blocked`。Fx CLI 的非交互审批限制
仍然存在；需要人决策的任务应选支持可观察审批的执行方式。Herdr 上报使用短超时，
不应让本地状态服务故障阻塞 Fx。适配器在退出时调用 `release-agent`，不占用原有
Herdr 内建 adapter 的 pane。

## 会话接续与日志

首次提交前没有 Fx session ID；只有回执实际取得非空 `session_id` 后，适配器才通过
Herdr 报告原生 ID 和 `task-delegation-fx-bridge resume --task-ref UUID` 恢复 argv。
若 Fx 回执没有 session ID，适配器记录 `fx_session_missing` 并退出，不继续发下一轮，
以免悄悄新建对话；这时先核查私有回执和真实 Fx 会话，不能自行补造 ID。
这个命令重进适配器，重新使用已记录的 provider、精确模型与 Fx 配置目录，再用
`fx ask --resume-id ID` 接续；不能把 pane ID 或自造 ID 当 Fx session，也不能把
裸 `fx resume` 当成 Herdr 适配器。Herdr 恢复 argv 首词须是 `PATH` 中的普通命令名，
参数不能含撇号或控制符，最多 64 项、8 KiB；用户也可能在 Herdr 配置中禁用自动恢复。
优雅停止 Herdr server 时，适配器可能收到退出信号并调用 `release-agent`，从而清除
自动恢复命令；这种停止后的自动重启不能仅凭配置或 mock 推断，须在独立会话实测。
Herdr 重启后的恢复须实际观察新适配器、原生 ID 和下一轮回执，不能仅凭存下的 argv
声称成功。具体合同见[官方自接入文档](https://herdr.dev/docs/add-herdr-support/)与
[会话恢复说明](https://herdr.dev/docs/session-state/)。

若旧适配进程确已退出而 Herdr 没有自动恢复，可在新的空 shell pane 中手动运行
`task-delegation-fx-bridge resume --task-ref ACTUAL_UUID`，再检查 `FX_BRIDGE_READY`、
`agent get` 和下一轮回执；不要同时在两个 pane 续写一个 `task_ref`。

适配器使用[跨项目日志](config-log.md)追加简短的轮次状态和真实 Fx session ID，
主 Agent 不必再为同一轮手动写一份日志。日志与 pane 的 `task_ref` 相连，不保存任务
全文或凭据。`inspect` 是离线回执读取，不会重新提交 prompt；已有任务不确定时先查它。
正常退出或 `/exit` 会释放 Herdr 当前 Agent 与其自动恢复命令；只在旧进程确已退出且
仍有有效 Fx session 时才手动启动 `resume --task-ref UUID`，避免两个适配器同时写同一任务。

本参考描述的是薄适配器与 Herdr 的实际接口；Mock 报告只验证适配器的自报告调用形状，
不能替代真实 pane 的启动、等待、回执与重启恢复测试。Fx 的
[SDK instrumentation](https://fx.sh/docs/lib/api#instrumentation)不是 CLI 生命周期 hook，
不应把其他 runner 的 hook 配置复制给 Fx。
