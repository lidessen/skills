# 代码库与软件边界设计

在设计或评审目录、模块、构建、运行与交付关系时读取。本文保留代码库领域的具体方法；
整体目的、跨部分取舍与演进判断见本技能入口，不把软件的包、进程或数据库边界套用于其他组织。

这里解决“内容如何形成清晰结构”，而不只是“目录看起来整齐”。内容可以是代码、文档、配置、schema、生成物、package、module、crate、binary 或 service。

## 核心判断

- 不要先套用 `src/`、`packages/`、`common/`、`shared/`、`utils/` 等目录模板。目录首先是导航；真实边界要由职责、依赖、构建、运行、状态和 ownership 关系共同支持。
- 先区分当前实现、目标设计、派生视图/生成物和历史依据。设计文档不能证明当前代码，目录名也不能证明独立发布或独立进程。
- “放一起”通常意味着有相同的变化原因、不变量、消费者、发布节奏、失败边界或 owner；“拆开”通常意味着其中至少一项可以独立变化，且边界能够被依赖、构建、运行或发布机制约束。
- 优先选择最小且可执行的边界：文件/目录 → private 或 internal unit → package/crate/module → binary/process → service/repository。不要因为理论上可拆就直接增加服务、仓库或中间层。
- 名称应说明所拥有的概念、面向的消费者和必要的角色/环境；`internal`、`public`、`api`、`core`、`common` 等只是信号，除非有语言、构建或项目规则支持，不要把它们当作事实。

## 何时使用

- 决定新代码、文档、配置或生成物应放在哪个位置。
- 评审目录、模块、package、crate、Go module、workspace 或服务是否边界清楚。
- 判断两个已有单元应该合并、保持共置、拆成 package，还是拆成独立进程/仓库。
- 为跨 Node/TypeScript、Go、Rust、Python 或其他语言的项目建立 source、build、runtime 和 delivery 关系。
- 设计或修正模块、文件夹、公共 API、适配器、插件和平台实现的命名。

不要仅因为文件很多就使用本 skill；纯格式化、单纯运行故障排查、视觉布局或已确认的陈旧内容清理应交给更合适的工作流。若主要问题是残留、重复、分散或错位的既有责任，先明确目标结构，再使用适用的清理方法。

## 工作流程

### 1. 定义一个结构问题

把问题收敛成一个可以作出决定的问题，例如：

- `X` 是同一功能的两个实现，还是两个不同消费者的边界？
- 这个目录是 source of truth、生成输出、发布镜像，还是仅用于构建？
- `Y` 应该是当前 package 的内部实现、可复用 library，还是独立 process？
- 混合语言代码的公共契约在哪里，谁拥有它？

记录对象、目标、当前压力、明确约束和不在本次范围内的相邻问题。不要为了“完整”先绘制整个仓库。

### 2. 恢复会改变判断的关系

按需读取入口、消费者和维护说明，然后为候选对象建立最小关系表：

| 对象 | 拥有的职责/不变量 | 直接消费者与入口 | import/API/可见性 | build/version/delivery | runtime/state/owner |
| ---- | ----------------- | ---------------- | ----------------- | ---------------------- | ------------------- |

至少把下面几类关系分开；一个关系成立不能替代另一个关系：

- source：文件、目录、生成输入和派生视图的来源。
- dependency/API：imports、exports、visibility、协议、注册和调用方向。
- build/version：package、crate、module、workspace、构建 target、版本与缓存边界。
- runtime/delivery：library、CLI、binary、process、container、installer 和部署组合。
- state：数据库、队列、事务、租约、缓存、恢复和资源 ownership。
- ownership/release：维护者、review 路径、兼容承诺、发布与回滚责任。

若问题涉及混合语言，读取 [hybrid-repositories.md](hybrid-repositories.md)。若只是某种语言的 package 和构建惯例，读取 [language-idioms.md](language-idioms.md)。

### 3. 判断共置、拆分和边界强度

用变化原因、不变量、消费者、构建/发布、失败隔离和 ownership 逐项判断。若只有目录位置不同，但关系和生命周期相同，不要制造虚假的模块；若关系已经不同但仍共用一个“方便目录”，不要用目录共置掩盖边界。

先选择能够表达并约束当前差异的最小单元：

- 同一概念、同一状态和同一变化原因：优先同 package 或相邻目录。
- 只想隐藏实现：使用 private/internal 可见性或稳定 facade。
- 有稳定外部消费者、独立依赖或独立构建责任：考虑 library/package/crate/module。
- 有独立启动、资源、失败、部署、升级或回滚责任：才考虑 binary/process/service。
- 只有版本治理、权限、ownership 或发布节奏确实独立时，才考虑 repository。

具体判断表和边界反例见 [decision-model.md](decision-model.md)。

### 4. 给概念命名并安排位置

- 先命名“它拥有什么”，再命名“它用什么技术实现”。优先使用领域概念、稳定协议或明确的角色。
- 只有确有两个不同实现或环境时才添加 `client`、`server`、`adapter`、`protocol`、`runtime`、`cli`、`browser`、`node` 等限定词。
- 用 `internal` 表示真实的不可对外依赖边界；不要仅凭下划线、目录名或 README 语气声称私有。
- `common`、`shared`、`misc`、`utils`、`manager`、`core` 如果没有具体 owner、消费者和排除范围，通常是未完成的命名。
- 对每个名称做四个检查：它包含什么、明确排除什么、最近邻概念是什么、一个反例会落在哪里。

### 5. 处理混合架构

- 为 schema/IDL/proto 设定唯一 source of truth，明确 generator、generated output、提交策略和可重现验证。
- 把语言绑定、外部 provider、平台实现和协议转换放在边界 adapter；不要让 adapter 偷走核心状态或业务 ownership。
- 用构建选择和发布矩阵表达平台差异，并追踪每种组合最终生成的 artifact。
- 把 plugin、extension、contrib、router、app 和 package 与 process、service、distribution 分开判断；注册机制不自动提供进程隔离。
- 跨语言不等于必须合并或拆成多个仓库。先检查依赖、提交、版本、发布和 ownership 是否需要同一边界。

### 6. 验证并收束

选择能暴露当前边界问题的真实变更场景检验结构：新增同类功能、替换实现、引入第二个消费者、改变平台、独立发布、失败/重启或迁移。场景数量随未决问题而定，不将次数作为结构成立的依据。验证顺序可按风险调整，但报告必须分开：

- 结构事实：当前源码、manifest、import、构建配置和注册关系。
- 机械结果：格式、静态检查、类型检查、测试、构建、安装或打包。
- 运行时观察：入口、进程、协议、资源、失败和恢复行为。
- 用户验收：维护者能否定位、修改、测试、发布和理解这套结构。

若用户只要求评审，不修改文件；若用户要求重组，执行最小的完整改动，保留已有未提交工作，并在结束前复查状态和差异。详细报告模板见 [review-and-evidence.md](review-and-evidence.md)。

## 交付内容

返回一份能让别人重建决定的记录：

- 结构问题与范围。
- 当前关系证据和仍未知的关系。
- 共置/拆分/不改变的决定及理由。
- 建议的目录、模块、命名或边界图；明确哪些只是组织视图。
- API、构建、运行、状态和 ownership 的实际约束。
- 需要的最小改动、验证结果、未验证项和重新打开条件。

不要把漂亮的目录树、一次格式检查通过或模型的自我解释当成模块化、运行独立性或用户验收的证据。
