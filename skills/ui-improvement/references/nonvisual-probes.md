# 用量测缩小疑点，用实际交互检验关系

工具是观察辅助，不是自动美化器。数值事实可以不看截图取得；Agent 仍要结合用途
决定是否受损、修哪里。没有候选问题不等于设计已精致，不能让量测替代本任务要求
的实际视觉复看。工具不预设设计系统、品牌、字体、统一间距或最佳控件尺寸。

## 开始量测

已有 Playwright 的项目里可用 [scan-ui.mjs](../scripts/scan-ui.mjs)：

```sh
bun /path/to/ui-improvement/scripts/scan-ui.mjs \
  --url http://127.0.0.1:3000 --widths 1440,950,390 \
  --focus '#progress' --channel chrome --out /tmp/ui-facts.json
```

尺寸按真实布局的容纳边界选，不把示例三值当必选。`--focus` 可省；指定后会在独立
浏览器页改变焦点，可能触发应用事件，只用于已授权的预览。不要把表单输入、保存
或服务写入加入通用扫描。模块默认从当前项目解析 `@playwright/test`，也可通过
`--playwright-module` 指向已有模块；没有依赖时采用现有浏览器工具，不自动安装。
`--out` 将详细证据写入文件，终端只给覆盖、横向扩张与焦点候选摘要。先读摘要，再
按疑点定位器读取有关控件和组的数据，不把全页大 JSON 一次塞进模型上下文。
摘要的 `paintNotMeasured` 列出尚未量出绘制部件的控件地址；它是观察能力缺口，
不是缺陷或自动整改清单。评价这些组成时主动取原比例局部，不能因候选警报为空
就宣称箭头或菜单外观正常；样式化装饰也仍需看实际绘制。

若已经在状态页、有认证会话或需要更准确的等待条件，直接复用
[probe-ui.mjs](../scripts/probe-ui.mjs)，避免重新打开首页丢失现场：

```js
import { probeUI, checkpoint } from "/path/to/ui-improvement/scripts/probe-ui.mjs";
const facts = await page.evaluate(probeUI, { scope: "#settings" });
```

脚本读取当前 DOM、open Shadow root、计算样式和几何关系，不修改样式或自动修复。记录 viewport、
页面横向扩张、溢出节点、真实滚动容器、控件文字尺度与内边距、标签文字包围盒、
相关 flex/grid 子项以及当前焦点。输出定位器供同一 DOM 回查，不当跨重绘的持久身份。
跨 Shadow 的 `address` 是逐层 CSS 数组，可用 `locate(page, address)` 回查；scope 与
checkpoint 也接受这种明确地址。相同内部 ID 在多个组件出现时，不用不明确的裸 ID。
CLI 另采同源子 frame，逐个报告自身坐标；跨源 frame 保留 omitted，不自动扩大读取。

## 选中一个元素检查

[inspect-ui.mjs](../scripts/inspect-ui.mjs) 可打印该元素的 margin、padding、尺寸、
边框、字体与祖先关系，按需截取局部。它打开独立预览，适合快速复现；已有状态页
优先复用 [inspect-element.mjs](../scripts/inspect-element.mjs) 的 `inspectElement`：

```sh
bun /path/to/ui-improvement/scripts/inspect-ui.mjs \
  --url http://127.0.0.1:3000 --target '#progress' --channel chrome \
  --focus yes --out /tmp/element.json --screenshot /tmp/element.png --padding 70
```

`--width` 换窄屏，`--frame` 在指定 iframe 内选对象，跨 Shadow 可传 JSON 地址数组。
截图 padding 是本次观察范围，仍可能不含完整标签；需要整组时选父区域。数值读取
不截图；截图、focus、trial 都按显式选项执行，可能改变滚动或触发应用事件。

```js
import { inspectElement, locate } from "/path/to/ui-improvement/scripts/inspect-element.mjs";
const result = await inspectElement(locate(page, ["#widget", "#button"]), {
  trial: true,
  screenshot: { path: "/tmp/detail.png", padding: 30 },
});
```

`elementFacts` 是可序列化的单元素浏览器函数，也可用于现有 CLI 的 eval。已有
Playwright CLI 会话无需重开页面：`snapshot` 取得 ref，再 `eval` 读所选元素样式、
`screenshot` 截元素或整组。现行 agent-browser 的 `get styles` 同样能读所选元素。
当前机器实测的是已有 Playwright CLI；agent-browser 未安装，未声称两者都验证通过。

检查器还给出指定区域的 Range 文字片段、SVG fill BBox 与坐标映射、当前五点指针
命中、相关动画清单。命中异常是调查线索，再以普通点击或 `click({trial:true})`
核对动作准备；trial不提交点击，却可能滚动。透明遮挡、pointer-events:none 绘制、
合法角标和浮层不能因矩形相交自动删除。ARIA snapshot 按需通过 `semantics:true`
启用，来自 Playwright 的 DOM 语义计算，可能包含字段值，只读获授权的具体范围。

## 怎样读事实

- **页面横向扩张**：核对超出视口的对象与容纳要求。横向表格可能合理，关键操作被
  推出视野则值得修。先看列最小宽度、留白与重组时机，不先缩小全页字体。
- **局部溢出**：区分明确 scroll 容器和 hidden/clip/visible；容器的 scrollWidth 超出
  不等于内容丢失。继续核对所属祖先和必要入口，不自动给所有容器加 overflow:hidden。
- **控件内部**：对照字号、内边距和框宽；原生 select 给出当前文字宽度估计及扣除
  padding/border 后的宽度，箭头占用仍未知。剩余空间紧张是调查线索，不是箭头碰撞
  的已确认事实。文本估计与标签 Range 包围盒含字体、空白影响，不是字形墨迹边界。
  内部宽度估计使用未变换的 layout CSS 像素，不能与 transform 后的外框混算。
  箭头位置未知时，局部图核对值与箭头、箭头与内缘的留白，而不是把外框 padding 当
  箭头位置的证明。原生部件的绘制未必跟随 CSS padding；修后仍按真实画面核对。
  默认装饰不合当前语言时，可在保留原生select行为的前提下接管装饰，或复用项目已有
  控件；选择依据是当前内部关系，不能通用地禁用原生样式。`appearance` 与背景位置/
  大小能解释CSS装饰的布局，却不是图形墨迹的证明；替换后复看窄空间、最长当前值、
  焦点及正常键盘选择，不靠加右padding宣称浏览器箭头已经移动。
- **整组关系**：比较标签、控件和同行动作的尺度、间距、轴线，合法差异可以保留。
  焦点时，outline 的包围范围进入标签文字空间会作为候选报告；检查圆角、真实轮廓
  与邻接，不能用一个统一阈值自动判错。默认扫描没有聚焦，不声称检查过焦点态。

记录具体证据与理由后再修源码。修后在相同状态、尺寸和范围重新量测，比较最初的
受损关系和邻接代价。先改责任位置，工具不写 CSS，也不把修复某个样板的参数发布
为全产品规范。

从受损关系回查原因：元素本身、父容器的列宽/最小内容宽度、nowrap、固定高度与裁切
可能共同造成症状。必要时在隔离预览临时改一个可疑属性验证因果，再修源码的责任位置，
重新加载确认。不要把 computed CSS 整体复制成补丁，也不要只缩小溢出对象。
绘制部件缺失时，还查组合声明是否重置了主题提供的装饰。例如真实表单里，公共
Select 已用 `appearance:none` 接管箭头，应用的 `background` 覆写却把主题的
`background-image` 清掉。应追到这条覆盖并恢复组件主题，再看完整控件组；追加
另一套箭头会留下平行样式。源码修正后确认预览已重新构建，旧画面与新源码不能合成
一份“修后通过”的证据。
响应式问题围绕布局发生变化的宽度检查，并复看邻近宽度；两端正常不能证明中间都正常。
合法头像叠放、角标、开关滑块与局部滚动不因矩形相交或 scrollWidth 变大自动判错。

## 用正常操作探测接续

`checkpoint(page, {fields, scrollers})` 只读取显式选择的字段、滚动容器、window
位置与当前焦点。字段值可能包含草稿，输出仅存授权现场，不把用户正文上传或提交。
它不自动推断哪个容器拥有阅读位置；先用 probe 的滚动信息与实际滚动核对。

```js
const before = await checkpoint(page, { fields: ["#draft"], scrollers: ["#reading"] });
await page.getByRole("button", { name: "另一篇" }).click();
await page.getByRole("button", { name: "原篇" }).click();
const after = await checkpoint(page, { fields: ["#draft"], scrollers: ["#reading"] });
// 按产品合同核对草稿、对象身份及真正拥有滚动的位置；不是要求所有快照逐字相同。
```

操作用普通 click、键盘和真实入口。`evaluate(el.click)`、直接设业务状态、
`selectOption` 可以定位接线，却不能声称用户点击、菜单键盘或返回动线通过。
动作后先看当前工作区域中的可见后果，再读取有关 DOM 核对：文本存在、`isVisible`
为真或值已改变，不能证明提示处于当前前景、属于正在编辑的对象，或关联图形也已同步。
模态内的反馈尤其要看实际层次与邻接；背板下仍可辨的全局提示不等于完整的模态反馈。
必要时对反馈区域作带周边截图，命中数据只辅助解释层次，不把非交互文字的指针穿透
自动判错。改变一个状态时核对同事实的字段、预览、标签和图形，不只挑其中一个断言。
按已有权限在隔离样板做改值/保存实验；真实服务的提交不因使用这个工具自动获授权。
不要再建立动作 DSL、固定最低步数或全产品一律执行的测试循环。

## 观察能力的边界

工具覆盖 light DOM 与 open Shadow；报告截断、Shadow host 与 iframe 数量。子 frame
独立采样，内部可用不证明外层未裁切或遮挡，不能混加不同 frame 的坐标。closed
Shadow 数量未知。节点可布局不代表未遮挡或当前可见，transform 的
矩形包围盒也不是实际轮廓。原生选项弹层、闭合 Shadow DOM、遮挡、光学对齐、色彩
协调与动效过程不能由这里证明。图片依赖、字体替换和加载中的状态也会改变量测。
CLI 只等页面 load 与字体 ready；需其他稳定条件时复用模块，在应用自己的就绪点后
执行，不用固定 sleep 宣称所有动画已完成。

方法依据：[Playwright CLI 的元素读取](https://github.com/microsoft/playwright-cli/blob/main/skills/playwright-cli/references/element-attributes.md)、
[Shadow 定位](https://playwright.dev/docs/locators#locate-in-shadow-dom)、
[动作准备检查](https://playwright.dev/docs/actionability)、
[Range 几何的定义](https://www.w3.org/TR/cssom-view/#extensions-to-the-range-interface)、
[SVG 几何接口](https://www.w3.org/TR/SVG2/types.html#InterfaceSVGGraphicsElement)。
