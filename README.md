# Skills

这个仓库收录用于 Agent 开发协作的通用技能，以及相关的理论、感悟和文章。技能覆盖架构与界面设计、文档写作、调研、分治协作和项目整理，供不同项目按任务选用；理论与文章也可以独立阅读。

## 内容

- [skills/](skills/)：可安装的技能，每个目录以 `SKILL.md` 为入口，包含方法说明和必要资源。
- [theory/](theory/README.md)：理论原文与方法摘编，涉及表达、信息管理、技能方法和结构整理。
- [notes/](notes/)：个人观察、短想法和有待探索的问题。
- [blog/](blog/)：围绕 Agent 与软件设计的文章草稿及图片。以 `_` 开头的文章保留草稿状态。

## 安装

### 按任务选择技能

15 个技能按用途组成下面几组。Pack 提供分组浏览和安装入口，技能源码仍统一维护在本仓库的 `skills/` 中。

| Pack | 技能数 | 包含的技能 |
| --- | ---: | --- |
| [lidessen](https://skills.sh/p/VwNOI0FZ0EAGV7Hy) | 15 | 以下各组去重后的全部技能 |
| [agent](https://skills.sh/p/djYQ0UTttmOpfna4) | 4 | [skill-incubator](skills/skill-incubator/SKILL.md)、[agent-guidance](skills/agent-guidance/SKILL.md)、[agent-personality](skills/agent-personality/SKILL.md)、[divide-and-conquer](skills/divide-and-conquer/SKILL.md) |
| [development](https://skills.sh/p/SazSJU8yDLRSqIF5) | 11 | [architecture](skills/architecture/SKILL.md)、[assurance-review](skills/assurance-review/SKILL.md)、[concept-naming](skills/concept-naming/SKILL.md)、[defrag](skills/defrag/SKILL.md)、[design-forge](skills/design-forge/SKILL.md)、[design-steward](skills/design-steward/SKILL.md)、[doc-writing](skills/doc-writing/SKILL.md)、[interface-design](skills/interface-design/SKILL.md)、[oneshot](skills/oneshot/SKILL.md)、[ui-improvement](skills/ui-improvement/SKILL.md)、[research-synthesis](skills/research-synthesis/SKILL.md) |
| [workflow](https://skills.sh/p/id3m9AGDJSzskEsP) | 1 | [research-synthesis](skills/research-synthesis/SKILL.md) |

Pack 可以交叉包含技能。例如 `research-synthesis` 同时属于 `development` 和 `workflow`，两处使用同一份技能源码；项目按任务选择所需技能即可。

Pack 的完整安装尚未通过验收，已有验证副本未完整取得部分技能的引用文件和脚本。完整验证前，项目安装请继续使用下面的 GitHub 直接安装命令。

### 从 GitHub 安装

需要 Node.js 22.20 或更高版本。使用官方 [Skills CLI](https://github.com/vercel-labs/skills/blob/main/docs/commands.md)，可先查看可安装的技能：

```sh
npx --yes skills@1.7.4 add lidessen/skills --list
```

在项目根目录安装需要的技能，例如界面设计。安装会替换同名技能目录；已有本地改动时，先另行备份再执行：

```sh
npx --yes skills@1.7.4 add lidessen/skills --skill interface-design -a codex --copy -y
```

该命令将技能完整复制到项目的 `.agents/skills/`，并在项目根目录记录 `skills-lock.json`。示例选择 Codex；使用其他 Agent 时，按 CLI 文档调整 `-a` 参数。将安装目录与锁文件一起纳入项目版本控制。

## 使用

从当前任务选择方法：[architecture](skills/architecture/SKILL.md) 用于职责、依赖与整体结构设计，[interface-design](skills/interface-design/SKILL.md) 用于界面视觉与交互，[doc-writing](skills/doc-writing/SKILL.md) 用于项目文档，[oneshot](skills/oneshot/SKILL.md) 用于一次明确请求直接落地并验收。

安装后，在 Agent 任务中明确所需技能和要解决的问题，例如“使用 interface-design 检查这个页面的视觉层级与交互，并说明改进建议”。技能的发现与调用方式以所用 Agent 为准。

阅读所选技能的 `SKILL.md`，再按任务需要使用其中的参考资料和脚本。跨技能链接提供相邻方法的阅读入口；需要使用这些方法时再安装对应技能。

脚本依赖按需准备：`interface-design` 的图像处理脚本使用 Python 3 和 Pillow；相关浏览器采集测试及 `ui-improvement` 的浏览器脚本使用 Playwright。具体依赖和参数见各技能说明。

## 更新

更新前先检查安装目录中的本地改动。CLI 会替换同名技能目录；确认需要保留的改动已另行保存后，重新运行对应的 `add` 命令，沿用所需技能名称、Agent 和复制方式。项目专属规则使用独立命名的技能维护，避免混入上游安装副本。

项目中的安装副本不会随 GitHub 或 Pack 变更自动同步。Pack 的成员也需分别维护：调整一个分组，不会自动修改其他重叠分组。使用 Pack 安装时，应在其内容更新后主动执行 CLI 更新；具体方式见官方 [Pack 更新说明](https://www.skills.sh/docs/packs#update-a-pack)。

## 来源

内容来源、命名变更和迁移记录见 [MIGRATION.md](MIGRATION.md)，逐文件来源见 [migration-manifest.json](migration-manifest.json)。文献、素材与第三方引用的出处保留在各文件中。
