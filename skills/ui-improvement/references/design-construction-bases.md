# 模型与 Agent 产品：设计的构建基础

2026-10-03，按用户指定对象查证。相似外观可能来自不同来源：模型默认生成倾向、
生成指导、厂商品牌、组件库底座、自建主题或具体业务编排。先分清来源，再决定能否
提炼种子；不从模型名称推断训练数据、隐藏提示或作者身份。

## 本轮取舍

| 对象                        | 已核实的构建基础                                                                                      | 如何吸收                                          |
| --------------------------- | ----------------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| Claude 生成 UI              | 官方 frontend-design 是选方向、构图和反模板的方法；artifact builder 另有 React／Tailwind／shadcn 底座 | 方法来源与反模板样本，不能当统一风格              |
| Anthropic 品牌／Claude 产品 | 品牌 skill 有色板与字体；这不是当前 Claude App 的完整设计体系                                         | 品牌候选，产品语言另核对，不以品牌参数直接收种子  |
| Codex 生成 UI               | 公开提示与 frontend 指导；区分已有设计系统、应用与营销                                                | 方法来源；应用指导部分借 Linear，不另造“Codex 风” |
| Codex 客户端                | 项目／任务／对话／审查等工作区结构，与生成网页指导不同                                                | 领域结构例子；完整视觉语言尚未核实                |
| DeepSeek Harness            | 上游设计平台与 deepsuite 变量、自写主题／控件／布局、对话和输出阅读结构                               | 固定版本结构参考，当前外观待复核                  |
| AgentParty                  | 自写 CSS、作者博客品牌演化、终端事实与协作信息架构                                                    | 有明确形神关系的独立候选，待页面观察              |

这是当前证据下的取舍，不按名气或“有独特样式”自动入选。已有库不是缺点，自写 CSS
也不证明优越；关键是哪些关系经过有意组织、怎样服务任务、能迁移到什么范围。

## Claude：当前客户端与生成基础分开

此前将“温暖编辑风”归为 Claude 代表的判断已撤回。任务明确指当前网页／桌面客户端，
生成指导和品牌色板不能代替现行完整画面。其版本、实际观察与待核实范围见
[当前设计参考](current-design-references.md#claude当前客户端旧暖编辑归因撤回)。
通用暖编辑表达可以保留，不能继续宣称已还原当前 Claude。

[官方 frontend-design](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md)
要求根据 brief 形成方向，并列出常见生成模板：暖奶油与衬线／陶土强调、暗底鲜亮强调、
报纸细线、同质圆角卡片等。它明确这些形式可适合某些任务，问题在于不随任务选择。
用户指定方向仍优先。因此它不支持“Claude 总应长成暖纸衬线”，也不是对这些风格的禁令。

[web-artifacts-builder](https://github.com/anthropics/skills/blob/main/skills/web-artifacts-builder/SKILL.md)
提供 React、TypeScript、Vite、Tailwind 和 shadcn/ui。这解释一种可见实现底座，不能证明
所有 Claude 输出都来自它，更不能证明 Claude 产品自身的 UI 使用同一套组件。

[brand-guidelines](https://github.com/anthropics/skills/blob/main/skills/brand-guidelines/SKILL.md)
另提供 Anthropic 品牌的深浅色、橙／蓝／绿与 Poppins／Lora 字体角色。它服务品牌 artifacts，
不能把其中字体直接当 Claude App 现行字体合同。色板证明识别选择，尚不足以解释完整
导航、对话、输入与状态关系；候选语言也不应被缩减成这份品牌参数。

另外，[官方 Claude Design 说明](https://claude.com/blog/claude-design-stays-on-brand-for-daily-work)
与 [Artifacts 说明](https://support.claude.com/en/articles/17153992-what-are-artifacts-and-how-do-i-use-them)
交代输出可用用户的设计系统，成果在对话旁继续编辑。它们分别支持生成基础与产品组织，
不能将生成成果的配色当宿主 UI 的配色。

## Codex：公开前端方法不等于客户端风格

[Codex Prompting Guide](https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide)
的前端提示要求选方向、避免套用默认、跨输出变化，并保留已有设计系统。
[OpenAI 前端设计文章](https://developers.openai.com/blog/designing-delightful-frontends-with-gpt-5-4)
强调构图、内容、参考与验证；其中应用指导明确借 Linear 的节制、可读密度和工作区分工，
营销部分则是另一种表达。这是生成方法，不是名为 Codex 的固定字／色／形体系。

公开建议中的避免默认字体、默认卡片等，需要按具体目标吸收，不能升级为本 skill
对系统字体或所有卡片的禁止。DeepSeek Harness 用系统字体就有自己的任务与平台依据。

[客户端发布记录](https://learn.chatgpt.com/docs/changelog) 说明项目侧栏、任务线程与审查面板，
支持工作对象和结果审查的结构。客户端自身、CLI、模型和 frontend 指导是不同对象；本轮
没有核对当前客户端完整 token、所有页面或源码，不把稀疏中性外观提炼为已证实的视觉哲学。

## DeepSeek Harness

实际只读本地相邻仓库，版本 `639ed015397290b3745d163aafe02ffee4aa3f84`。以下链接固定版本：

- [base.css](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/client/ui-theme/src/styles/base.css)
  明确变量来自上游 deepsuite，系统／CJK、品牌和代码字体分角色；有统一圆角与运动变量。
- [design-platform.css](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/client/ui-theme/src/styles/design-platform.css)
  提供静态色板、语义别名、明暗及平台分层，注释交代设计平台字体权重与设计者针对可读性的修订。
  “Figma”在这里指设计稿来源，不等于 Figma 产品的 UI 风格。
- [Button.module.css](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/client/ui-primitives/src/Button.module.css)
  实现尺寸、填充／描边／ghost、禁用和交互状态，而非 React 默认外观。
- [columns.ts](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/client/ui-layout/src/client/columns.ts)
  规定多列空间如何退让；[ConversationRoot.module.css](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/client/ui-conversation/src/client/skeleton/ConversationRoot.module.css)
  将正文、输入及其他对话材料组织在共同宽度轴线上。
- [TurnProcessNodeView.tsx](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/client/ui-chat/src/client/chat/TurnProcessNodeView.tsx)
  根据实际结束、失败、取消及过程状态组织标记和展开，不是装饰性“正在工作”。

可保留为固定版本 Agent 对话工作台结构参考：阅读与输入保持主轴，过程和成果可回查，辅助区域按职责
分层。源码支持这些关系，但没有证据表明它们来自模型自动生成风格，或必然直接继承
Apple／Claude。上游设计稿未独立回查，不能继续猜测其更早来源。

## AgentParty：博客品牌演化与终端协作

只读浅克隆，版本 `3086c7a82b147defe8b39591bbf4fec52bf043bf`。
[package.json](https://github.com/leeguooooo/AgentParty/blob/3086c7a82b147defe8b39591bbf4fec52bf043bf/web/package.json)
是 React／Vite 与自写 CSS；桌面 Tauri 复用 Web 构建，未见以 shadcn 等作全站控件底座。

[历史设计](https://github.com/leeguooooo/AgentParty/blob/3086c7a82b147defe8b39591bbf4fec52bf043bf/docs/superpowers/specs/2026-07-03-agentparty-design.html)
明确参考作者博客；[当前 tokens](https://github.com/leeguooooo/AgentParty/blob/3086c7a82b147defe8b39591bbf4fec52bf043bf/web/src/styles/tokens.css)
与 [doodle.css](https://github.com/leeguooooo/AgentParty/blob/3086c7a82b147defe8b39591bbf4fec52bf043bf/web/src/styles/doodle.css)
已是 neo-brutalist terminal：米纸、方角墨线、淡墨硬偏移、珊瑚强调和等宽字。已取消
抖动边框与手写标题，不能让旧设计记录覆盖现状；hover／pressed 位移延续纸片隐喻。

[团队面板设计](https://github.com/leeguooooo/AgentParty/blob/3086c7a82b147defe8b39591bbf4fec52bf043bf/web/src/components/TeamTabs.design.html)
按分工、Agent 看板与协调组织内容；状态、待处置与回查是协作事实，不随纸色复制。
可提炼“终端式精确材料与较亲切的实体表面并置”，但这是源码与用途的解释，不冒充
作者已确认的完整哲学。硬影只是部分形式，不能据此推定两个产品的服务价值或任务组织相同。

保留候选及领域例子。官方 hero 是宣传插画，图标 sprite 仅能说明资产；本轮未运行
真实页面，不能评价完整密度、响应式和注意代价。源码不足以确定 UI 的生成模型。

## 下次如何核实候选

填写型界面看引导、长内容输入、错误、返回和完成；协作型界面看频道、长消息、
成员与任务状态、协调操作和窄屏。完整观察再检验内在原则是否被实际形式承载，发现
问题可收缩种子或撤回，不靠设计文档替视觉验收。模型输出倾向若需验证，应固定任务、
环境、模型与可见指导并观察不同样本，不能用一张生成图推断模型本性。
