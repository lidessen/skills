# 当前设计参考与版本边界

核对于 2026-10-03—04。默认以当前官方已发布体验、现行指南和实际画面为主要参考；
历史材料解释演化。抓取日期、文章日期、产品版本、组件库版本与分批上线范围分别记录。
新文章不必意味着新外观，旧发布的形态也可能仍是当前有效指导。

## Claude：当前客户端；旧暖编辑归因撤回

参考对象是 Claude 网页／桌面客户端，不是 Claude Code 生成网页、Claude Design
营销页或 Anthropic 品牌 artifacts。此前 `claude.html` 的暖纸、衬线、陶土与札记编排
只代表一个通用暖编辑试作；撤回其对当前 Claude 客户端的代表性，不作为最新种子。

[2026-09-16 公告](https://claude.com/blog/cowork-is-now-claude/)及
[现行帮助](https://support.claude.com/en/articles/16761823-claude-cowork-and-chat-are-one-claude)
说明 chat 与 Cowork 融合、Design 进入会话，并分批推出。该日期支持功能和入口变化，
不证明用户提到的几个月前视觉改版发生于同日。准确的视觉改版日期与完整新版画面仍
待核实；暂不命名完整“最新 Claude 风”，也不以局部状态替代最新全量体验。

官方 frontend-design 的文件更新定位到
[`41bbe19`，2026-09-03](https://github.com/anthropics/skills/blob/41bbe19d1a1a7eaab5e7bb9050a417e5c6cffc8f/skills/frontend-design/SKILL.md)。
它是生成指导，不能补当前客户端外观证据。下一次还原应先拿到当前正常会话、输入、
导航与相关面板的完整画面，再提炼具体关系；不能把“更新”简单理解成改成深色。

## Apple：OS 27 的 Liquid Glass 修订

[2026-09-14 正式发布](https://www.apple.com/newsroom/2026/09/major-updates-for-apples-software-platforms-are-now-available/)
确认 iOS／iPadOS／macOS 27。当前 [Design Resources](https://developer.apple.com/design/resources/)
提供这些平台的 27 UI Kit；其他平台资源仍有旧版号，分别判断，不整体改标 27。
主要设计变化以 [WWDC26 102](https://developer.apple.com/videos/play/wwdc2026/102/)
和 [SwiftUI 更新](https://developer.apple.com/videos/play/wwdc2026/269/)为依据。

相对 2025 初版，玻璃扩散背景、暗边与镜面亮边增强分离，透明程度可调；Mac／iPad
侧栏抵窗口边缘，活跃窗口有强调色，窗口曲率更统一紧凑，滚动进入工具栏区域后有
统一表面帮助可读。核心仍是内容层清楚、导航与控制层随背景和状态变化。

已实际查看官方 [macOS 27 kit 缩略图](https://developer.apple.com/design/resources/images/thumbnails/Thumbnail-UIKit-macOS27_2x.png)
与 [iOS 27 kit 缩略图](https://developer.apple.com/design/resources/images/thumbnails/Thumbnail-UIKit-iOS27_2x.png)：
前者是分组表单和嵌套控件，后者包含 sheet 顶缘、圆形浮动控制及透背景 Dock；不能
仅凭表单缩略图推定完整玻璃导航行为。使用时再看职责相近的完整场景。
[现行 HIG Materials](https://developer.apple.com/design/human-interface-guidelines/materials)
仍限制玻璃主要用于导航与控制，不把内容卡片全部玻璃化。

此前 `apple.html`／`apple-v2.html` 是资料应用的实色近似；不能当最新 OS 27 的完整还原。
WWDC25 保留为体系起源，经典 macOS 形式仅作历史补充。

## Linear：2026 refresh 与近期现行画面

[2026-03-12 UI refresh](https://linear.app/changelog/2026-03-12-ui-refresh)及
[设计解释](https://linear.app/now/behind-the-latest-design-refresh)是本轮可证实的整体外观
更新：位置／视图／动作头部一致，导航退让，边界减少、结构仍可辨，默认灰更暖且
降低饱和度。2024 说明只解释前史。

同时核对 [当前 changelog](https://linear.app/changelog)：已读到 2026-09-24 的更新，
9 月 Priority inbox 等提供现行画面入口。近期功能更新不能被误称另一次整体视觉
改版；也不能以 8 月 StyleX 代码迁移推断换了设计语言。精确还原时以当前相应场景
画面为主，不能仅凭 3 月原则认证 `linear-v2.html` 为最新产品复刻。

## Material：现行 Expressive，包含 2026 更新

实际用浏览器查看 [2026-05-19 I/O 更新](https://m3.material.io/blog/whats-new-at-io26)、
[现行 layout](https://m3.material.io/foundations/layout/layout-overview/overview)及
[canonical examples](https://m3.material.io/foundations/layout/canonical-examples/overview)：
2026 增加 scaffold、spacing 与跨设备指导，组织 bar、rail 和内容 panes，按任务改变
list-detail、feed 与 supporting pane；不是把桌面卡片缩窄堆到手机。

[Typography](https://m3.material.io/styles/typography/overview)更新栏标 Aug 2026：根据
文字系统高度调整行高与组件尺寸。中文界面需观察实际字形，不能仅按拉丁字体试作。
[Lists](https://m3.material.io/components/lists/overview)与
[Menus](https://m3.material.io/components/menus/overview)的当前案例有分段列表、选择行、
局部鲜明菜单和层级；其更新栏分别为 Dec／Nov 2025，不能改称 2026 首次发布。

[Shape](https://m3.material.io/styles/shape/overview-principles)和
[Motion](https://m3.material.io/styles/motion/overview)的 Expressive 更新也始于 May 2025，
仍属现行指导。观察圆／方张力、按角色变化的轮廓与因果形变；空间运动与色／透明度
变化有不同物理要求，不能到处回弹。表现性字体只在任务相符的重点区域使用，
参考[当前 editorial treatments](https://m3.material.io/styles/typography/editorial-treatments)。

Compose 库的 stable／alpha 版号属于实现库，不是整个设计系统统一版本；Web 组件
尚有 Expressive unavailable，借设计不等于现成 Web 库已完整支持。旧 2025 研究可以
解释原则，但新的还原需要当前组件、布局与多语言画面。前两份 Material 试作为原
文字参考实验，v3 已补布局迁移；均未核对全部现行关系。

## 其他对象的状态

- **Figma**：当前[官方 sidebar 指南](https://help.figma.com/hc/en-us/articles/360039832014-Design-prototype-and-explore-layer-properties-in-the-right-sidebar)
  仍介绍 UI3，区分导航、底部工具条和属性；部分旧视频有旧界面提示。2024 博客可
  解释演化，不能代替当前画面；本轮尚未核实全部最新工具行为，原试作只作组织实验。
- **DeepSeek Harness**：原读本地 `639ed015`（2026-09-29）；当前远端 HEAD 已是
  `5badb15009ae1756c3afe0ae0cef1faafc290ccc`（2026-10-03）。Git tree 核对发现 client UI
  有变化，原版不再被称为最新。需要沿实际使用的主题、布局与交互重新核对，不因
  新 commit 就假设全部视觉已改变。[当前源码](https://github.com/deepseek-ai/deepseek-harness/tree/5badb15009ae1756c3afe0ae0cef1faafc290ccc)。
- **AgentParty**：远端 HEAD 核对仍为 `3086c7a`，与原研究一致；源码版本仍有效，
  原产品实际页面与完整状态尚未运行，原试作不能因此成为最新产品精确还原。

## 实作校准的边界

内部原型实验不作为公开效果证据。迁移参考时，在相同内容与尺寸条件下检查任务关系、
构图与局部工艺，分别记录实现、实际观察和用户接受。几何检查通过不等于行文节奏成立，
短摘要孤尾、图标光学关系和正常输入状态仍需实际查看。一个场景的迁移成功也不能证明
种子成熟或技能稳定提高设计质量。
