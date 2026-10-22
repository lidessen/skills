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
`printf '%s' "$TASK" | fx ask --json --model "$MODEL"`；`MODEL` 与 `TASK` 必须先按策略
确定。本机 Fx 0.0.14 的 `ask --help` 确认无 prompt 参数时可从 stdin 读取任务文字；
这样任务正文不进入 Fx 进程 argv。管道输入无法回答交互审批，需审批的任务改用合适的
交互执行方式。
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
此脚本使用 POSIX 文件锁和进程组；在其他操作系统部署前须核对或适配这些接口。
安装或链接这个入口须由主 Agent 按当前任务授权完成，且**目标 pane 的 `PATH`** 与
Herdr 恢复后的 `PATH` 都必须能找到同名命令。源码存在不表示入口已安装；先在目标
环境核对 `command -v task-delegation-fx-bridge`，并确认该命令解析符号链接后指向
**本次运行的同一个适配器脚本**；否则不能登记 Herdr 恢复 argv。不要写
`agent start --kind fx`。

先按策略核对 provider、精确模型、认证、套餐与 fallback，确认适配器会继承的 Fx 配置。
`start` 可选 `--fx-home ABS` 指向已有 Fx 配置家目录、`--fx-bin ABS` 指向已安装的
Fx 可执行文件；`--no-additional-dirs` 限制额外工作目录。新任务默认给 Fx 子进程最小
环境；只有核实目标通道确需并允许继承环境中的认证或其他变量时，才显式使用
`--inherit-fx-env`。已有任务恢复沿用启动时保存的环境模式。最小环境不保证每种通道
都能认证成功，继承环境也不能替代项目上下文与工具权限检查。
恢复会记住这些路径、provider 和模型，但配置文件以后
可能被人修改，因此接续前仍要重新核对实际路由。
以下使用 `--current` 的创建示例仅适用于主 Agent 已在真实 Herdr pane 内；从外部终端
控制时须获得授权，在每条命令显式指定已核对的 `--session` 与目标 pane，不能隐式选默认
会话。无论控制命令从哪里发，适配器 `start/resume` 都必须实际运行在 Herdr pane 内。
从创建结果 `.result.pane.pane_id` 取得真实 ID，等待该 pane 到 shell prompt 后再启动。
以下是命令形状，`PROJECT`、`DESCRIPTION`
与 `MODEL_ID` 换成已核实的值，动态文字须按 shell 规则安全引用，不把任务全文写到
`--description` 中：

```sh
herdr pane split --current --direction right --cwd "$PWD" --no-focus
# 仅在创建成功后，从返回 JSON 的 .result.pane.pane_id 取 PANE_ID 并核对目标 pane。
herdr pane run "$PANE_ID" \
  "task-delegation-fx-bridge start --project PROJECT --description DESCRIPTION --provider PROVIDER --model MODEL_ID"
herdr pane wait-output "$PANE_ID" --match FX_BRIDGE_READY --timeout 30000
herdr agent get "$PANE_ID"
herdr agent read "$PANE_ID" --source recent-unwrapped --lines 40
```

`pane run` 只确认命令已送入终端；`wait-output` 也可能匹配旧 scrollback，因此需检查
刚启动的前台进程和最新输出。等适配器上报 `idle`，并从终端的
`FX_BRIDGE_READY` 行读取真实 `task_ref` 后，才准备完整任务；任务中仍要交代
目标、范围、上下文、产物与验收。`encode` 从标准输入接收一行 UTF-8 任务文字，拒绝
原始换行、回车与控制符，再输出 `: FXB1_...` 封套。为避开 macOS PTY 的单行限制，
封套最多 900 个 ASCII 字节；超限时缩短任务文字，改给经过授权、目标 runner 可读的
文件路径与具体范围。Herdr 0.9.5 只把此适配器的自报告用于状态展示，
`agent prompt` 仍要求原生识别的前台 Agent，不能给自报告的 Fx 提交任务；改名也不会改变
这一检查。用 `pane run` 将编码后的单行封套和 Enter 一次送到当前适配器，再按本轮标识
等回执：

```sh
TASK_REF=ACTUAL_UUID       # 从 FX_BRIDGE_READY 读取，不自行生成
NEXT_TURN=1                # inspect 的当前 turn + 1
TASK_TEXT='一行内写清目标、范围、产物和验收'
if WIRE=$(printf '%s' "$TASK_TEXT" | task-delegation-fx-bridge encode \
  --task-ref "$TASK_REF" --turn "$NEXT_TURN"); then
  herdr pane run "$PANE_ID" "$WIRE"
else
  printf '%s\n' '编码失败：没有提交任务' >&2
fi
```

编码成功且 `pane run` 已提交后，等待本轮回执；提交结果不确定时先查 pane 与 `inspect`，
不要重发：

```sh
herdr pane wait-output "$PANE_ID" --source recent-unwrapped \
  --match "FX_BRIDGE_RESULT {\"task_ref\":\"$TASK_REF\",\"turn\":$NEXT_TURN," --timeout 120000
task-delegation-fx-bridge inspect --task-ref "$TASK_REF"
herdr agent get "$PANE_ID"
```

封套只使用 shell 安全字符，前面的 `:` 是 shell 空操作；即使适配器在检查与提交之间
退出，落到 shell 的这一行也不会执行任务正文。适配器只接受匹配当前 `task_ref` 与下一
轮次的封套，拒绝原始任务文字和旧封套。编码并不加密，仍不可借此传递凭据或越权内容。
`encode` 须与目标适配器使用同一用户状态目录，且仅在其状态为 `idle` 时生成封套。
`pane run` 的成功回执只表示文本已送达终端；`pane wait-output` 会先搜索已有 scrollback，
所以每次都用实际 `task_ref` 和预期 `turn` 匹配，不能只等泛用的 `FX_BRIDGE_RESULT`。
等待超时先查 `inspect` 与 pane 输出，确认当前轮是否已提交或完成，不自动重发。
适配器将精简的 `FX_BRIDGE_RESULT` 印到 pane，不把模型正文复制到终端摘要；
私有状态文件存 Fx 的 JSON 回执，`inspect` 读取最近一轮状态与 `final_output`。
确认进程退出码、JSON `exit_code`、`final_output`、
真实 `session_id` 与产物，再按任务验收，不能仅凭 Herdr 的 `idle`、`done` 或
`pane wait-output` 认定完成。`agent wait` 不跟踪独立轮次，已有其他轮次在运行时尤其
需要核对 `task_ref` 与回执。

适配器只在 Herdr 确认环境变量齐全时自报，使用不与内建 adapter 冲突的稳定 `source`
和递增 `seq`。真开始 Fx 请求时上报 `working`；成功回执落盘且适配器可接收下一行时
才上报 `idle`。任一轮失败会保存回执、上报 `unknown` 并退出；此时必须用 `inspect`
查原因，不可自动重发。`resume` 遇到已记录的失败轮次会拒绝恢复；检查回执和可能的
实际副作用后，确需继续时显式加 `--ack-failed-turn`，它不会自动重发上一轮。
不能可靠判定审批或提问时不虚报 `blocked`。Fx CLI 的非交互审批限制
仍然存在；需要人决策的任务应选支持可观察审批的执行方式。Herdr 上报使用短超时，
不应让本地状态服务故障阻塞 Fx。仅显式 `/exit` 会调用 `release-agent`；异常退出与
Herdr 服务停止时不会由适配器主动清除恢复信息，但不能因此推断 Herdr 已保存或自动恢复成功。
轮次超时会尽力终止 Fx 的进程组并保存 `turn_timeout` 回执；自行脱离该进程组的后代
可能继续运行。状态不确定时先核实实际产物和费用，不自动重发。

## 会话接续与日志

首次提交前没有 Fx session ID；只有回执实际取得非空 `session_id` 后，适配器才通过
Herdr 报告原生 ID 和 `task-delegation-fx-bridge resume --task-ref UUID` 恢复 argv。
若 Fx 回执没有 session ID，适配器记录 `fx_session_missing` 并退出，不继续发下一轮，
以免悄悄新建对话；这时先核查私有回执和真实 Fx 会话，不能自行补造 ID。
这个命令重进适配器，重新使用已记录的 provider、精确模型与 Fx 配置目录，再用
`fx ask --resume-id ID` 接续；不能把 pane ID 或自造 ID 当 Fx session，也不能把
裸 `fx resume` 当成 Herdr 适配器。Herdr 恢复 argv 首词须是 `PATH` 中的普通命令名，
参数不能含撇号或控制符，最多 64 项、8 KiB；用户也可能在 Herdr 配置中禁用自动恢复。
Herdr 停止与重启后的自动恢复须在独立会话实际观察新适配器、原生 ID 和下一轮回执；
保存的 argv 或 mock 不能证明成功。具体合同见[官方自接入文档](https://herdr.dev/docs/add-herdr-support/)与
[会话恢复说明](https://herdr.dev/docs/session-state/)。

若旧适配进程确已退出而 Herdr 没有自动恢复，可在新的空 shell pane 中手动运行
`task-delegation-fx-bridge resume --task-ref ACTUAL_UUID`，再检查 `FX_BRIDGE_READY`、
`agent get` 和下一轮回执；不要同时在两个 pane 续写一个 `task_ref`。

适配器使用[跨项目日志](config-log.md)追加简短的轮次状态和真实 Fx session ID，
主 Agent 不必再为同一轮手动写一份日志。日志与 pane 的 `task_ref` 相连，不保存任务
全文或凭据。`inspect` 是离线回执读取，不会重新提交 prompt；已有任务不确定时先查它。
显式 `/exit` 会释放 Herdr 当前 Agent 与其自动恢复命令；只在旧进程确已退出且
仍有有效 Fx session 时才手动启动 `resume --task-ref UUID`，避免两个适配器同时写同一任务。

本参考描述的是薄适配器与 Herdr 的实际接口；Mock 报告只验证适配器的自报告调用形状，
不能替代真实 pane 的启动、等待、回执与重启恢复测试。Fx 的
[SDK instrumentation](https://fx.sh/docs/lib/api#instrumentation)不是 CLI 生命周期 hook，
不应把其他 runner 的 hook 配置复制给 Fx。
