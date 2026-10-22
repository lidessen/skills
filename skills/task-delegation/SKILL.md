---
name: task-delegation
description: 用 Herdr 交付和追踪独立 Agent 任务，结合 Magpie 可见的模型、provider 与套餐通道选择合适 runner，并按质量、延迟和实际费用权衡。用于明确要求 Herdr + Magpie 委托或需要在其已配置通道间选路；普通分治组织、不需要委托的任务和未授权的付费 API 接入不由本技能处理。
metadata:
  short-description: Herdr + Magpie 任务委托与选路
---

# Task Delegation · 基于 Herdr 与 Magpie 的任务委托

为一项已获授权、能独立交接的任务选择**能完成任务**且成本与延迟合理的执行通道。
Herdr 负责启动、提交、追踪和读取 Agent 结果；Magpie 提供当前可见的模型、provider、
账户与额度线索。具体模型是否能在所选 runner 上调用，仍要核对当前认证、产品条款、runner
参数和实际配置。这里不创建另一套 Agent 框架，也不把配置文字当作权限保证。

多任务的分工、覆盖和总体验收由
[divide-and-conquer](https://github.com/lidessen/skills/blob/main/skills/divide-and-conquer/SKILL.md)
负责；本技能只处理每项任务的选路和交接。无需委托的简单任务、没有受支持 Herdr 环境的任务、
或用户只要套餐价格比较时，分别用宿主原有执行方式或
[plan-value-analysis](https://github.com/lidessen/skills/blob/main/skills/plan-value-analysis/SKILL.md)。

## 先建立可编辑策略

首次使用，按用户或项目的适用范围选择明确的策略文件位置，生成草稿后编辑。以下两行
分别适用于技能源码仓库根目录和项目安装副本目录，按实际位置只运行其中一行：

```sh
python3 skills/task-delegation/scripts/init.py --output ./task-delegation-policy.md
python3 .agents/skills/task-delegation/scripts/init.py --output ./task-delegation-policy.md
```

`--dry-run` 只预览目标；重复初始化不覆盖已有文件。策略用 Markdown 表达优先、避开、禁止、
允许的 runner/provider/route、套餐通道、质量与延迟偏好、付费 API fallback 和预算。
它不保存密钥，也不因写着“有订阅”就认为当前已认证可调用。脚本只生成文件，不解析或强制
执行自然语言策略。若用户与项目策略同时适用，逐项合并；冲突的硬边界在澄清前不得放宽。
没有策略文件时，先确认本次任务的硬边界，尤其是否允许付费通道，再选路。

## 为任务选可兑现的路

1. 明确任务目标、范围、输入与可读上下文、允许的写入或外部效果、产物和验收依据。
   先判定所需工具、上下文长度、推理与可靠性、可接受延迟；不让低价覆盖关键能力缺口。
2. 读取适用策略，先排除**禁止**的 runner、provider、route 和计费路径；“避开”是可解释的
   软偏好，不等于禁止。确认套餐的**官方受支持入口**和当前认证/计费身份，区分原生 runner
   订阅、官方授权的套餐集成与单独计费的 API。订阅不自动产生 API key，登记账户不等于可调用。
3. 用 Magpie 当前目录、配额及 runner 的真实模型参数检查候选；目录说明候选 ID，不证明
   质量、剩余额度或可用认证。同一共享池的两个 route 不算两份余额。对合格候选，优先利用
   已付套餐的可用额度，再考虑耗时、成功率和边际费用；不盲目用完额度，也不默认选最弱模型。
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
不修改 Magpie 的全局模型、group 或 fallback 配置来完成一次委托。交给执行者的任务应包含：

> 目标与验收；范围和禁止事项；必要上下文及权威来源；可读写位置、工具与权限；
> 期望产物与路径；应运行的检查；失败、阻塞和未知时返回什么。

Herdr 的状态只说明观察到的生命周期，不证明产物正确。`blocked` 先检查问题或审批界面；
`stalled`、超时及 `unknown` 先核对状态与输出，不盲目重发。拿到结果后按原验收依据审查
产物、验证和权限边界，再向调用者交还采用的 route、理由、实际观察和剩余未知。
遇到 429 先区分短期限流、共享池和真正耗尽，尊重可用的重试时间；余额未知既不是零也
不是无限。付费 API fallback 未获允许时停下或等待合规通道恢复，绝不静默切到付费。

## 证据边界

本技能的命令依据 Herdr 0.9.5、Magpie 0.1.1296 与当时 runner `--help`；版本变化以现场
CLI 为准。策略与静态检查不证明套餐认证、条款允许、模型效果或实际执行成功；这些须由当前
通道和任务结果分别验证。本技能不自动安装工具、登录服务、生成凭据或更改全局配置。
