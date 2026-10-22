# 策略配置与跨项目接续日志

## 策略

全局策略为 `XDG_CONFIG_HOME/task-delegation/policy.md`。只有 `XDG_CONFIG_HOME` 是绝对
路径时才用它；未设置或相对路径时退回 `~/.config/task-delegation/policy.md`。主 Agent
在首次启用时先与用户协商[策略示例](policy-example.md)中的实际选择，再直接写 Markdown。
已存在的文件不覆盖；用户要求修订时针对既有内容修改。Markdown 是给 Agent 阅读的偏好与
边界，不是运行时强制器；项目规则、本次授权及工具权限继续约束执行。

## 接续日志

所有项目共用 `XDG_STATE_HOME/task-delegation/delegations.jsonl`；只有 `XDG_STATE_HOME`
是绝对路径时使用它，否则退回 `~/.local/state/task-delegation/delegations.jsonl`。
主 Agent 在实际委托时写短事件，便于跨项目找到原任务和接续位置。事件至少包含带时区
时间、短描述、项目、runner、状态与稳定 `task_ref`；Herdr Agent 名、pane ID 和 runner
自身 session ID 各自独立。日志不存任务全文、凭据、完整地址或账户资料。

可用本技能的最小 helper 追加事件。先把 `SKILL_DIR` 设为实际安装的本技能目录；以下
只展示调用形状。`task_ref` 省略时 helper 生成本地 UUID 并只打印该 UUID，主 Agent
应保存它供后续事件复用：

```sh
python3 "$SKILL_DIR/scripts/log.py" --project PROJECT --description '简短任务描述' --runner RUNNER --status started --herdr-agent NAME --herdr-pane PANE_ID
```

可选 `--runner-session-id ID` 只有在 runner 确认后传；未知时日志写 `null` 与
`session_state: pending`，确认后用 `--task-ref UUID` 追加同一任务的事件，不回填或改写旧行。
这里的 `pending` 仅表示 helper 未收到非空 ID；有意使用 `--no-save` 等不保存会话时，
主 Agent 在简短状态或描述中注明不可恢复，读日志时据此不安排补查或恢复。
`--log ABS_PATH` 只供隔离测试或明确覆盖日志目标。Herdr 的 pane 是终端位置，不能作为
runner 可恢复会话；`agent get` 的 `agent_session` 只有在集成真实报告后才可用。
helper 使用 POSIX `fcntl` 锁，适用于 macOS/Linux；未验证 Windows 支持。
使用 [Fx 薄适配器](fx.md)时，适配器用同一 `task_ref` 为每轮追加简短状态及确认的
Fx session ID；主 Agent 不要再为同一轮重复写一条等价事件。Fx 的详细回执保存在
私有状态目录，用 `task-delegation-fx-bridge inspect --task-ref UUID` 查看摘要，
全局日志仍只记录定位和状态。

状态事件描述已观察的进度，不能代替验收。失败、超时或 `blocked` 时保留原任务标识，
先查现场与产物，不盲目重派；交付后日志只追加简短结果状态，验证依据留在原任务回执
或产物中。没有真实委托时
不制造日志事件。
