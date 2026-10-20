# Skills、理论与感悟

Lidessen 的通用 Agent 技能、方法论、个人感悟和 Blog 草稿。项目专属规则与内部研究记录留在各自项目，本仓库维护可复用、可公开的内容。

| 目录 | 内容 |
| --- | --- |
| [skills/](skills/) | 14 个技能，每个目录含 `SKILL.md` 和必要资源 |
| [theory/](theory/) | 技能发展、评估、整体结构与归位方法的公开摘编 |
| [notes/](notes/) | 6 篇个人短想法 |
| [blog/](blog/) | 4 篇文章草稿及关联图片 |

## 安装与更新

在需要使用技能的项目根目录执行官方 [Skills CLI](https://github.com/vercel-labs/skills/blob/main/docs/commands.md)，先列出技能，再选需要的名字：

```sh
npx --yes skills@1.7.4 add lidessen/skills --list
npx --yes skills@1.7.4 add lidessen/skills --skill interface-design -a codex --copy -y
```

这里明确选择 Codex，项目级安装到 `.agents/skills/`；不使用 `-g`。`--copy` 保留技能完整目录，不添加其他 Agent 的链接。CLI 同时维护项目根的 `skills-lock.json`，将它和安装目录一起纳入项目版本控制。

按需增加技能时复用同一条 `add` 命令，列出所需名字。升级前先比较本地改动；当前核对的 CLI 版本会替换同名目录，不保护项目定制。确认没有独有改动后，以同样明确的名字、`-a codex --copy` 重新安装。项目专属技能使用独立名字，保留自己的来源与维护入口。

技能内部资源使用相对路径；相邻技能的方法引用指向本仓库，按任务需要再安装，不会自动递归加载。`interface-design` 负责产品界面视觉与交互打磨；软件、组织和职责架构使用 `architecture`。

## 脚本与内容

`interface-design` 的图像处理脚本需要 Python 3 和 Pillow，采集器测试使用 `@playwright/test`。`ui-improvement` 的浏览器脚本使用被测项目的 Playwright；参数与边界见各技能自带说明。本仓库不安装统一网站引擎或前端工具链。

`blog/_*.md` 保留草稿前缀和 Frontmatter。草稿源码在公开 GitHub 仓库可见；站点构建继续按 `_` 前缀排除页面。`notes/` 保存面向读者的正文，私人捕获与审校过程留源。

迁移来源、重命名和公开处理见 [MIGRATION.md](MIGRATION.md)，逐文件来源与哈希见 [migration-manifest.json](migration-manifest.json)。本仓库没有新增许可证；已有引用和第三方出处随文件保留。公开可读不等于授予未声明的再许可权利。
