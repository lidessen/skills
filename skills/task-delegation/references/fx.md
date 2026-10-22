# Fx：轻量委托与按需 Herdr 接入

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

## 持久交互：确有需要才自行接入 Herdr

本机 Herdr 0.9.5 的 `agent start --kind` **没有 `fx`**，本机也没有 Fx 可执行文件。
这不妨碍以后由主 Agent 在已授权环境中通过 `pane run` 启动一个**现有、可用的桥接入口**，
但桥接必须真的处理持续输入、Fx 状态与会话恢复；本文不提供或安装 wrapper。
不要写 `agent start --kind fx`，也不要在已有内建 adapter 占用的 pane 抢报所有权。

按 [Herdr 自接入合同](https://herdr.dev/zh-cn/docs/add-herdr-support/)设计桥接：

1. 仅在 `HERDR_ENV=1` 且 `HERDR_PANE_ID`、`HERDR_BIN_PATH`、`HERDR_SOCKET_PATH`
   均存在时上报。桥接运行在目标 pane 并继承这些变量；外部调用方不能把自己的 pane ID
   当目标 pane。选稳定、唯一且不以 `herdr:` 开头的 `source`，使用不与内建 Agent
   冲突的标签。`--seq` 对同一 source 在跨会话、重启后严格递增，旧上报不得覆盖新状态。
2. 真实工作开始才上报 `working`，可接受下一次输入才上报 `idle`，确有用户决策等待
   才上报 `blocked`（可带 `--message`）；没有可靠依据时上报 `unknown`。桥接应后台
   或短超时发送最新状态、忽略上报失败，不阻塞 Fx；Herdr CLI 没有为该上报提供
   `--timeout` 选项。命令形状如下，`fx-bridge` 须换成不会冲突的 source：

   ```sh
   "$HERDR_BIN_PATH" pane report-agent "$HERDR_PANE_ID" \
     --source fx-bridge --agent fx --state working --seq "$SEQ"
   ```
3. Fx 实际返回 session ID 后，同一 source 可在状态上报中加 `--agent-session-id ID`，
   或用 `pane report-agent-session` 单独上报；必须先由 `report-agent` 持有该 pane。
   只有持久桥接能够重建相同模型、provider、套餐通道和输入处理时，才在 `--` 后附
   **桥接命令**作为恢复 argv，不要直接写裸 `fx resume ID` 而失去桥接。首词必须是
   `PATH` 上的普通命令名（非路径），参数不得含撇号或控制符，至多 64 项、合计
   8 KiB；不满足时不声明可自动恢复。Herdr 恢复命令需 0.9.2 以上且可被用户配置关闭。
4. 桥接真正退出才以同一 source/agent 和递增 seq 调用 `pane release-agent`。
   `agent prompt` 只是在已识别 Agent 的终端提交文本与 Enter；桥接未实现接收时，
   不能把它当 Fx 的通用任务 API。`agent read` 是终端输出，`agent wait` 只观察状态，
   最终仍要核对 Fx 产物与原验收条件。

若选择 libfx 做持续桥接，[Fx instrumentation](https://fx.sh/docs/lib/api#instrumentation)
中的 `hooks.onEvent` 是 SDK 观察接口，不是 Fx CLI 的生命周期 hook；回调 Promise 不被
等待，失败不阻断或重试，不能单独充当持久日志。`session.id` 在首个 prompt 接受前可能
为空；`turn.end` 也不必然表示已空闲，实际审批/提问要看配对的 `wait.start`/`wait.end`
及桥接自身的输入状态。不要复制 Claude hooks JSON 当 Fx 配置。

上述接口来自官方文档与本机 Herdr CLI 帮助；**本机 Fx 未安装**，未做运行、速度、
认证或恢复实测。只有实际桥接运行后才能声称 Herdr 能追踪该 Fx 会话。
