# Apple 设计基底与跨平台适配

用于用户选择 Apple 为设计参考，或设计 Apple 平台界面的任务。适用于不同产品，不依赖任何仓库、组件库或示例端口。先确定平台、主要活动和输入方式；不因引用本资料就把所有界面设计成 macOS，也不将 Apple 设为通用审美答案。

## 依据与适配分开

优先使用当前 Apple HIG 的平台/组件说明、官方 Design Resources 和对应原生控件。材料未给定的间距、padding、圆角和 CSS 数值明确标为设计适配，不把一套自选 token 冠名为 Apple 规范。不要混用 iOS、macOS、visionOS 的尺寸表，也不把旧 OS X 文档静默当成当前系统。

## 字体与层级

[Typography](https://developer.apple.com/design/human-interface-guidelines/typography)，2026-09-21 通过浏览器读取 legibility、hierarchy 与 macOS built-in text styles。官方 macOS Body 为 13pt，Title 2 为 17pt，Subheadline 为 11pt；这是桌面平台的原生角色参考，不是 Web px 或 CSS pt 的直接换算。小字避免轻字重，以系统字体、字重、颜色和位置共同组织层级。多行阅读需要足够行距，不能为压低控件高度而牺牲持续阅读。

Web 迁移时按实际语言、字体回退、缩放和设备重新观察；不能声称 CSS 字体样式实现了原生动态字体 API。浏览器缩放、原生 Dynamic Type 和 macOS 字体变体是不同能力。自选字号与行高保持角色关系，不机械同比缩放所有文字。

## 布局、控件与图标

[Layout](https://developer.apple.com/design/human-interface-guidelines/layout)提供平台边距、布局引导与适应内容的方向。[WWDC25：Build a SwiftUI app with the new design](https://developer.apple.com/videos/play/wwdc2025/323/)讨论控件分组、内容优先和跨平台形态；macOS 的小尺寸控件保留圆角矩形以维持横向密度。

以接近和间隔表达操作关联，按当前活动选择默认控件尺度。图标的实际轮廓与笔画要匹配相邻文字；视觉尺寸与点击区域分别设计。表单、工具栏、正文和浮层不必使用同样的空白量。桌面指针密度不能直接复制到触摸设备。

若 Web 样板需要数值起点，可尝试组内 8px、组间 16px、面板边距 24px，图标 16px、桌面点击高度 32px、触摸区域 44px；这些只是可改的适配候选，不是 Apple 规定，也不是所有产品的默认值。根据内容与整体构图验证，再决定是否提取 token。

## 材质和反馈

新设计中的材质帮助区分导航/控件与内容层。应保留内容的可读性和主位；CSS 模糊不能等同原生 Liquid Glass。原生系统字体和 SF Symbols 的具体使用遵循平台能力及许可，跨平台可使用合适的现有图标体系来保持一致。

验证真实输入、返回、长内容、缩放与不同输入方式；颜色、字重和轮廓共同维持可识别性。用户选定 Apple 基底只确定参考方向，不自动证明某组适配参数或视觉样板已经验收。
