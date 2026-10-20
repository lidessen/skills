# 2026-10-20 迁移与公开清单

内容主要来自 Lidessen 自有 Rossovia 工程的通用技能、Blog 和方法资料。源版本为 `0ce3ef5c8c99893d64c3cd94df5fc4eac822c9de`；逐文件原路径与原始、公开版 SHA-256 见 [migration-manifest.json](migration-manifest.json)。源路径均为仓库相对路径。

## 公开内容

- 14 个通用技能及必要资源。
- 2 篇理论公开摘编：技能发展与评估；整体结构、分治与归位。
- 6 篇个人短想法。
- 4 篇保留 `_` 前缀的文章草稿，3 张关联猫插画。

`meow-design` 更名为 `interface-design`。它实际处理产品界面的视觉层级、比例、排版和交互打磨，明确不承担软件架构评审，因此采用界面设计这一通用名称。目录、Frontmatter、标题和活动引用同步更名，不保留旧名兼容入口。原 Meowland 专属上下文拆回项目。

## 公开版处理

六篇完整的技能形成资料混有私人工作反馈、内部模型试验、项目审计或实现背景，留在私有源仓库。此处仅收录两篇通用理论摘编，保留来源区段和效果尚未验证的边界，不把内部试验结果改称公开验证。

短想法删除私人捕获与审校 HTML 注释，保留 Frontmatter 和面向读者的正文。文章只去掉私有配套设计引用和一处既有项目实现陈述；观点、草稿身份和其余内容保留。公开技能去除私有工程的本机路径、账号状态和未提交实现案例，保留通用方法与公开文献来源。

跨技能的可选引用改为公共仓库链接，技能自身的资源继续使用相对路径，以便按需单独安装。图片保留字节内容；文章没有 MDX imports 或直接嵌入图片依赖。原始出处和第三方引用保留，没有添加新许可证。

## 项目接续

Rossovia、Meowland 和 Workcells 通过官方 Skills CLI 项目级安装所需技能，并跟踪 `skills-lock.json`。项目特有技能与 AGENTS 引导留在各自项目；不进行全局安装，不安装其他来源的技能。

Rossovia 原通用目录在目标校验、CLI 安装和消费者切换后清理，运行技能继续通过项目内已有目录引用物化。内部研究原件保留；旧路径引用若属于历史现场记录，保留其历史地位。

Blog 引擎和部署仍归 Rossovia。构建时从本仓库 checkout 读取 `blog/`、`notes/` 和图片，临时映射为引擎需要的内容布局；不发布网站。文章草稿只在站点构建中排除，GitHub 仓库源码仍可见。

新仓库最初以私有方式准备，公开前建立仅含审查后内容的干净历史。此前完整迁入快照只在本机私有备份分支保留，不推送该分支。此次只公开 `lidessen/skills`，其他仓库可见性不变。

首次迁移时尚未定位三份早期 theory 文件，后续只读追查已在旧仓库的未合并分支找到原文，见下节。外部文献网页的持续在线可用性不作保证。

## 补迁：三份历史理论原文

2026-10-20，将旧仓库 `lidessen/rossovia-old` 的 `cursor/incubate-theory-068c` 分支中三份文稿原样迁入本仓库。固定来源提交为 `e205d09f036a134864d336978ced0a7ec9c10f91`；旧仓来源保留。

| 目标文件 | 固定来源 |
| --- | --- |
| `theory/theory.md` | [旧仓原文](https://github.com/lidessen/rossovia-old/blob/e205d09f036a134864d336978ced0a7ec9c10f91/theory/theory.md) |
| `theory/thoughts/information.md` | [旧仓原文](https://github.com/lidessen/rossovia-old/blob/e205d09f036a134864d336978ced0a7ec9c10f91/theory/thoughts/information.md) |
| `theory/skills.md` | [旧仓原文](https://github.com/lidessen/rossovia-old/blob/e205d09f036a134864d336978ced0a7ec9c10f91/theory/skills.md) |

三文件均在该提交新建，至分支顶端 `c7ba0f90d80850a9b92e2d53ac12af5d5fba34e0` 内容未变。旧 `main` 未合入这段历史，最初只查主分支导致漏检；本次不是重建或猜测正文。

三份原文保留全部字节及当时的候选、原话和方法边界。公开内容核查未发现密钥、私密个人或业务事实、账号配置或运行数据。另增[理论阅读入口](theory/README.md)，说明全文与现有两篇后续摘编的部分重叠，以及未随迁的归档和 `harness.md` 的历史引用；未把它们改写成当前技能的安装依赖。

正式 README 仅调整理论导航，保留已完成的文案改写。两篇现有摘编仅补阅读入口，正文未重写。逐文件来源、Git blob 和 SHA-256 已补入 `migration-manifest.json`。
