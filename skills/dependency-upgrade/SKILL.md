---
name: dependency-upgrade
description: Inventory npm/Bun workspaces and Go modules, distinguish declared and resolved versions, assess upgrade candidates, and implement authorized updates. Use for dependency upgrade decisions and execution, not as a complete security audit.
---

# Dependency Upgrade

把版本查询变成有依据的升级决定。先读取目标项目的依赖策略、模块边界、包管理器和验证
要求；是否升级 major、追随什么发布通道、如何使用 overrides 均由该项目与本次任务决定。
只要求检查时不修改 manifest、锁文件或工具配置；已要求升级时继续完成相应迁移和验证。

## 找到真实检查范围

先核对 Git 的工作树与暂存差异，保留已有工作。发现 manifest、workspace、Go module、
工具模块、示例和锁文件，再区分源码目录与构建产物，不按固定项目布局猜入口：

```bash
rg --files -g package.json -g go.mod -g go.work -g go.sum -g '*lock*'
```

读取 workspace 声明及相关模块说明。`workspace:*`、本地路径依赖与 Go `replace` 是源码
关系，不直接换成 registry 版本。每个独立 module 的版本和消费者分别核对；若使用 go.work，
先决定是在检查 workspace 的有效关系，还是逐个检查可独立发布的模块。

## npm / Bun：声明范围与锁定结果分开

复用 [npm-check-updates](https://github.com/raineorshine/npm-check-updates) 等项目认可的工具，
不自写 registry 查询和 semver 求解。先确认所用工具的版本、运行时要求、配置和 flag 语义，
不要把旧项目的一次兼容性测试作为当前版本保证。已有可信 `ncu` 时，检查示例为：

```bash
ncu --workspaces --target latest --jsonUpgraded --no-upgrade --no-interactive --no-doctor --install never
```

只在实际使用 workspace 时加 `--workspaces`；独立 manifest 用明确的 `--packageFile`。
根据项目 policy 选择 target，`latest` 是一个查询目标，不是自动批准所有升级；需要比较时
再查 minor、patch 或指定通道。不要用 `newest` 把最新发布时间误作稳定性。

检查 NCU 配置：CLI 显式关闭写 manifest、交互、doctor 与安装，仍可能加载可执行配置、
联网或写缓存。只读任务优先在可信项目的只读副本或只读挂载中查询，工具缓存另置临时位置；
先核对配置和执行环境，不把“查询”当作天然无副作用。工具缺失时按任务授权选择已有执行器、
隔离运行或安装，不为一次查询悄悄新增项目依赖。
私有源沿用授权配置，不切源或输出凭据。

NCU 候选表示**声明范围**可怎样改，不等于 lockfile 的实际版本，也不覆盖全部传递依赖。
核对项目锁文件与已安装/解析结果；同一依赖跨 workspace 出现时合并升级决定，保留各路径。
空候选只说明本次范围查询未建议改声明，不能证明 lockfile 最新、查询成功或不存在漏洞。
必要时用项目包管理器的 outdated 功能补充解析结果；网络、认证和工具失败明确列为未完成。

## Go：build list、替换关系和 major 路径

使用 [Go 模块工具](https://go.dev/ref/mod#go-list-m) 查询各 module 的完整 build list。
只读仓库查询可在原 module 目录使用临时 mod/sum 副本；下面的 `MODULE_DIR` 必须设为
真实模块目录，保留 cwd 使本地相对 replace 的解析环境不变：

```bash
(
  set -euo pipefail
  cd -- "$MODULE_DIR"
  scratch=$(mktemp -d)
  trap 'rm -rf -- "$scratch"' EXIT
  cp go.mod "$scratch/check.mod"
  if [[ -f go.sum ]]; then cp go.sum "$scratch/check.sum"; fi
  GOWORK=off go list -mod=readonly -modfile="$scratch/check.mod" -m -u -json all
)
```

此示例检查独立 module，显式 `GOWORK=off`；若目标是 workspace 的有效构建关系，应另行
保留并检查 go.work/replace 影响，不用独立模块结果代表整个 workspace。`-mod=readonly`
不保护所有 sum/cache 写入，临时 mod/sum 才把这些依赖文件写入留在副本；查询仍可能联网、
写 Go cache 或受 toolchain 选择影响。需要更严格隔离时使用项目认可的只读运行环境。

`-json all` 输出连续 JSON 对象，应按 stream 解析（例如 `jq -s`），不能当成单个 JSON 数组。
读取 `Path`、`Version`、`Update`、`Indirect`、`Replace`、`Retracted`、`Deprecated` 和 `Error`，
跟踪实际被替代的模块及错误。本地 replace 不作为远端版本升级；传递依赖优先通过其直接
owner 调整，不盲目对所有 indirect 执行 latest。

`-u` 不会枚举 `/v2`、`/v3` 等不同 module path。对主要直接依赖、弃用库和已知换 major 的
上游核对官方 release 与 migration 文档；`Update` 为空不足以说明最新版。被撤回和弃用的
版本说明原因及替代路线，不能只按版本号排序。

## 从候选到实施

给出升级、暂缓或待核实的明确建议，列出依赖及文件范围、声明/解析版本、目标、理由、
必要迁移和验证。记录查询日期、工具版本、覆盖模块及失败范围；把未知写成缺少的证据和
下一步，不用泛泛风险代替决定，也不把一次成功退出当作“全部已检查”。

读候选的官方 changelog/迁移说明，定位真实消费者，核对运行时、OS/arch、peer、生成代码
及成组发布依赖。安全扫描另用项目认可的 audit/govulncheck 工具，解释实际 findings 和
覆盖范围；不为了另一工具生成第二套锁文件，不把版本查询当完整漏洞结论。

用户已要求实施时，按耦合关系分批更新选定 manifest、唯一权威锁文件和消费者：NCU 只改
manifest，安装由项目包管理器完成；Go 使用目标 module 的 go get/tidy，跨 major 同步
import 与 API。保留本地 workspace/replace，overrides 需有具体 owner 与问题依据。
执行能发现迁移错误的针对性测试及项目必需检查，类型通过不代替实际运行或打包验证。
最后核对 diff 与已有工作，分别交付已升级项、暂缓项和验证边界；提交、发布另按用户授权。
