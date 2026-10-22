---
name: task-delegation
description: 主 Agent 用 Herdr 交付与追踪独立任务，结合 Magpie 的模型和套餐线索选择 runner、provider 与模型，并用跨项目日志保存接续标识。用于 Herdr + Magpie 委托及其质量、延迟、成本选路；普通分治组织、不需要委托的任务和未授权付费接入不由本技能处理。
metadata:
  short-description: Herdr + Magpie 任务委托与选路
---

# Task Delegation · 基于 Herdr 与 Magpie 的任务委托

主 Agent 为独立任务选择**能完成任务**且成本与延迟合理的执行通道，交接后追踪真实结果。
Herdr 负责启动、提交和观察 Agent；Magpie 提供模型、provider、账户与额度线索；
runner 自己拥有会话和恢复方式。具体 route 是否能调用，仍要核对认证、产品条款、runner
参数与实际配置。技能不创建另一套 Agent 框架，也不把配置文字当作权限保证。

多任务的分工、覆盖和总体验收由
[divide-and-conquer](https://github.com/lidessen/skills/blob/main/skills/divide-and-conquer/SKILL.md)
负责；本技能只处理每项任务的选路、交接和接续记录。无需委托的简单任务，或用户只要
套餐价格比较时，分别用宿主原有执行方式或
[plan-value-analysis](https://github.com/lidessen/skills/blob/main/skills/plan-value-analysis/SKILL.md)。

## 首次启用：与用户协商策略

全局策略位置为 `XDG_CONFIG_HOME/task-delegation/policy.md`；`XDG_CONFIG_HOME` 未设置
或不是绝对路径时使用 `~/.config/task-delegation/policy.md`。先检查是否已有策略，
有则保留并读取，不能以模板覆盖。没有时，先与用户对话协商：已拥有且允许使用的套餐与
官方访问方式、当前可安装/使用的 runner、偏好的 provider/model、优先/避开/禁止、
付费 API fallback 及预算、任务的质量与延迟取舍。只需问会影响选路的未知，不索取凭据。
据工具、上下文、恢复、隔离、质量/延迟和用户偏好，与用户选定默认及备选 runner，
记录取舍理由；这是可修订的起点，不强制每项任务用同一 runner。取得这些决定后由
主 Agent 直接写可编辑 Markdown；以
[策略示例](references/policy-example.md)作结构参考，不照抄其中占位符当用户事实。

策略是给主 Agent 和获准决策器阅读的指引：**禁止**是硬边界，**避开**是可解释的软偏好。
写着“有订阅”不等于当前已认证可调用，Markdown 也不会机械强制权限。项目自身的
`AGENTS.md` 和本次任务授权继续适用；与全局策略冲突的硬边界在澄清前不得放宽。
策略更改需保留用户已有选择，不因工具目录变化自动改写个人偏好。配置和日志位置、
保留内容及示例见[配置与接续日志](references/config-log.md)。

## 为任务选可兑现的路

1. 明确任务目标、范围、输入与可读上下文、允许的写入或外部效果、产物和验收依据。
   先判定工具、上下文、会话恢复、隔离、推理可靠性和可接受延迟；不让低价覆盖能力缺口。
2. 读取适用策略，先排除**禁止**的 runner、provider、route 和计费路径；“避开”是可解释的
   软偏好，不等于禁止。确认套餐的**官方受支持入口**和当前认证/计费身份，区分原生 runner
   订阅、官方授权的套餐集成与单独计费的 API。订阅不自动产生 API key，登记账户不等于可调用。
3. 用 Magpie 当前目录、配额及 runner 的真实模型参数检查候选；目录说明候选 ID，不证明
   质量、剩余额度或可用认证。同一共享池的两个 route 不算两份余额。默认从能满足上述
   门槛的较轻量 runner 起选，再比较成功率、端到端延迟和边际费用；尊重用户偏好，优先
   利用合规、已付且可用的套餐额度。不固定 Claude、Pi、Fx 或最轻模型，也不以用完额度为目标。
4. 依据当期官方模型能力目录、可比的原始评测和本地任务反馈，按任务类别、工具可靠性、
   上下文、端到端延迟与成本选择。记录准确模型版本、runner/推理档、来源日期及未知。
   初始化、目录或套餐变化、证据过时、任务类型变化、反复失败或 429 时刷新相关证据，
   不为每个小任务重抓全网，也不编造实时排名。详见[选路判断](references/routing.md)。
5. 若有当前已验证、获授权且符合相同禁止/预算边界的 decision API 或 Jev，可让它辅助筛选；
   先计入选路调用自身的费用。若只能走未授权付费通道、能力不符或接口未证实，主 Agent
   直接按上述策略选择。Magpie 的 Jev effort classifier 与任务级路由不同，不能替代此步。

## 委托、观察与回收

在 Herdr 管理的 pane 中才用其控制命令。读取
[已核实的 CLI 接口与示例](references/interfaces.md)，核对现场 `--help`、runner 认证和执行参数；
不修改 Magpie 的全局模型、group 或 fallback 配置来完成一次委托。Herdr 不支持的 runner
不能假装为 Herdr kind；若另走其原生 CLI，使用它真实的执行与恢复接口。选 Fx 时按
[Fx 接入参考](references/fx.md)区分一次性调用和本技能的可选长驻薄适配器。适配器由
主 Agent 在获准环境中部署并启动；Markdown 策略不是路由白名单。交给执行者的任务应包含：

> 目标与验收；范围和禁止事项；必要上下文及权威来源；可读写位置、工具与权限；
> 期望产物与路径；应运行的检查；失败、阻塞和未知时返回什么。

Herdr 的状态只说明观察到的生命周期，不证明产物正确。`blocked` 先检查问题或审批界面；
`stalled`、超时及 `unknown` 先核对状态与输出，不盲目重发。拿到结果后按原验收依据审查
产物、验证和权限边界，再向调用者交还采用的 route、理由、实际观察和剩余未知。
在跨项目日志中记短描述、带时区时间、runner、状态和稳定 `task_ref`；Herdr agent/pane 与
真实 runner session 分列。未知 session 先标 `pending`，确认后以同一 `task_ref` 追加事件，
不把 pane ID 当作可恢复会话，也不记任务全文、凭据或完整地址。详见
[配置与接续日志](references/config-log.md)。
遇到 429 先区分短期限流、共享池和真正耗尽，尊重可用的重试时间；余额未知既不是零也
不是无限。付费 API fallback 未获允许时停下或等待合规通道恢复，绝不静默切到付费。

## 证据边界

本技能的命令依据 Herdr 0.9.5、Magpie 0.1.1321、Fx 0.0.14 与已核对的 runner
帮助/官方文档；版本变化以现场 CLI 为准。策略与静态检查不证明套餐认证、条款允许、
模型效果或实际执行成功；这些须分别由当前通道和任务结果验证。会话 hook 只在目标
runner 支持且获授权时使用，不默认安装或修改
个人配置。本技能不自动安装工具、登录服务、生成凭据或更改全局模型配置。
