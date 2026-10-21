# 内容来源与适配

通用技能、短想法和文章主要来自 Lidessen 自有 Rossovia 工程，原始来源版本为
`0ce3ef5c8c99893d64c3cd94df5fc4eac822c9de`。以下源路径均相对于其所属仓库。

## 通用方法

`meow-design` 更名为 `interface-design`，职责是界面的视觉层级、比例、排版和交互打磨，
不承担软件架构评审。名称、Frontmatter 和活动引用随之调整，Meowland 专属上下文留在项目。

测试、依赖维护和现场评估材料来自 Rossovia 固定提交
`5150fe39aa8968fbc2c7efdbeb7a8fda0d629a9a`：

| 材料 | 原始位置与适配 |
| --- | --- |
| `risk-driven-testing` | 来自 `skills/risk-driven-testing/`；`.agents/skills/test-cycle/SKILL.md` 的复测与中断续接方法归入按需参考，去掉固定记录目录和产品方法依赖。 |
| `dependency-upgrade` | 来自 `.agents/skills/dependency-upgrade/SKILL.md`；保留版本、模块关系和升级验证方法，目标项目的版本策略优先，不沿用固定路径或历史工具版本保证。 |
| `agent-guidance` 现场评估参考 | 来自 `.agents/skills/agent-eval/references/field-trial.md`；保留答案隔离、真实入口及程序状态与业务评价分离，产品链路、运行标识和认知研究历史留在 Rossovia。 |

技能自身资源使用相对路径，可选的跨技能引用使用公共仓库链接，便于按需单独使用。
来源文献与第三方引用保留在各文件中。

## 理论

下列历史原文来自 `lidessen/rossovia-old` 的 `cursor/incubate-theory-068c` 分支，
固定提交为 `e205d09f036a134864d336978ced0a7ec9c10f91`，正文保留原始字节及当时的候选与未知：

| 文件 | 固定来源 |
| --- | --- |
| `theory/theory.md` | [旧仓原文](https://github.com/lidessen/rossovia-old/blob/e205d09f036a134864d336978ced0a7ec9c10f91/theory/theory.md) |
| `theory/thoughts/information.md` | [旧仓原文](https://github.com/lidessen/rossovia-old/blob/e205d09f036a134864d336978ced0a7ec9c10f91/theory/thoughts/information.md) |
| `theory/skills.md` | [旧仓原文](https://github.com/lidessen/rossovia-old/blob/e205d09f036a134864d336978ced0a7ec9c10f91/theory/skills.md) |

两篇方法摘编取自上述 Rossovia 原始来源版本的技能形成资料：

| 摘编 | 来源材料 |
| --- | --- |
| `theory/skill-development.md` | `docs/tooling/skill-quality-evaluation-design.md` |
| `theory/architecture-and-defrag.md` | `docs/tooling/structuring-skill-design.md`、`docs/tooling/divide-and-conquer-skill-design.md`、`docs/tooling/defrag-skill-design.md`、`docs/tooling/design-steward-skill-design.md` |

摘编保留通用方法、来源与证据限制，完整内部形成记录仍归源仓库；内部试验不改称公开验证。
历史原文、摘编与未随迁归档的关系见[理论入口](theory/README.md)。

## 写作与项目边界

短想法和文章保留 Frontmatter、作者语气、草稿身份和原有引用，去除私人捕获、审校注释与
私有配套设计引用；关联插画保留原始内容。文章的 `_` 前缀保持草稿含义。

项目特有的 AGENTS 引导、角色制度、JSX、运行、发布和内部工作流规则仍归各项目，
公开方法不携带本机路径、账号状态或私有实现案例。Blog 引擎与部署留在 Rossovia；
本仓库保存文章、短想法与素材，不把内容迁移当作文章或网站发布。
