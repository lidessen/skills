# 方法来源与取舍

本资料保留合并前 design-review 的通用设计评审方法来源。下列公开材料用于启发判断方式，并非 skill 的运行依赖。
上游内容可能变化；采用这些原则时仍以当前用户需求为边界。

## Impeccable

- [Critique](https://github.com/pbakaus/impeccable/blob/main/skill/reference/critique.md)：借鉴先判断整体设计与产品特征，再综合机械证据；防止检测清单锚定审美判断。
- [Layout](https://github.com/pbakaus/impeccable/blob/main/skill/reference/layout.md)：借鉴空间主张、缩小后的视觉层级检查、疏密节奏、按语义组织关系。
- [New work](https://github.com/pbakaus/impeccable/blob/main/skill/reference/new-work.md)：借鉴区分局部打磨与整体方向探索，保留品牌时仍允许重组结构。

不移植强制检测器、数值评分、固定选项数量、随机方向与审批流程。它们不是审美证据，也不应改变调用方的授权与工作方式。

## Anthropic frontend-design

[SKILL.md](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md)：借鉴从真实产品内容形成视觉表达，以及有意识地选择字体、布局与一个核心记忆点。

不把特定颜色、字体或“常见 AI 风格”作为一律禁止的对象。已经确立的品牌、操作习惯和用户偏好优先；差异性必须服务内容。

## UI UX Pro Max 与 Vercel Web Interface Guidelines

- [UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/main/.claude/skills/ui-ux-pro-max/SKILL.md)可作为配色、字体、布局与平台经验的检索资料，检索命中不等于设计适配。
- [Web Interface Guidelines](https://github.com/vercel-labs/agent-skills/blob/main/skills/web-design-guidelines/SKILL.md)适合规范检查，不能代替整屏审美与设计方向评判。

本 skill 不要求安装二者，也不内置它们的规则清单。需要技术审查时，由调用方另行选择合适能力。

## 能辨认方法是否生效的现象

有价值的评审能说明哪个整体关系不成立，提供可见的替代，并选择一个连贯方向。
如果反馈仍只有字号、边距、按钮降权，先检查是否已经默认现有构图正确。
如果候选只换了颜色和圆角，检查是否把风格参数误当成空间设计。
如果“好看”只能靠删减真实内容成立，应退回内容与布局共同设计，而不是宣称已完成。
