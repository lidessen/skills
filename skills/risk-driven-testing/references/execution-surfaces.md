# 按被测面选择真实工具

只在生成或维护对应执行投影时读取。先问目标失败能从哪里被观察，再核对当前工具与宿主能力；
不因某工具可截图就用它证明所有平台。这里不定义统一驱动接口、端列表 registry 或跨端执行器。

## 逻辑、API 与 CLI

规则、协议、进程退出与文件副作用沿已有测试函数、客户端或真实进程入口验证。GUI 不能替代这些
边界，mock 也不证明外部接合成立。参数用结构化调用或 executable + argv，不拼接 shell 字符串；
外部数据先验证，回执不明确先查现态，再决定是否重试。

## Web：默认 playwright-cli

用 playwright-cli 实走、更新与回放，复用项目已有启动入口、账号准备及 fixture，不另开浏览器绕过
setup，也不要求新增 Playwright Test。每次有效操作的 `Ran Playwright code` 可作 TypeScript 素材；
用 `generate-locator` 从当前 ref 提取并核对语义定位器。按行为 YAML 的 expect 补断言，不能把当前
UI 自动升为正确合同。[官方代码生成指南](https://github.com/microsoft/playwright-cli/blob/main/skills/playwright-cli/references/test-generation.md)
只提供工具用法，不改变凭据、行为期望或授权边界。

准备方已在活会话 `chat-user` 完成登录并保持开启时，后续可取新观察：

```sh
playwright-cli -s=chat-user snapshot
```

后续动作继续指定同一 `-s`，核对当前 page 与本例起点，重新解析 ref。CLI 原子动作可以是
executable `playwright-cli` 与 argv ``[`-s=${session}`, "click", currentRef]``；也可以由已有运行
入口调用接收当前 page 的普通 Playwright 函数。`run-code --filename` 载入按 CLI 合同包装的 JS
函数片段，不直接运行任意导出 TS 模块或完整 spec；多动作片段属于 flow 或组装，不因单次调用
就成为一次原子 action。agent 的自主浏览器操作也绑定同一会话，decision 只选路。

[命名会话](https://github.com/microsoft/playwright-cli#sessions)复用活实例；state-save / state-load
或持久 profile 只恢复其支持的状态，不等于活浏览器、内存和在途流程。借用已有浏览器前核对
[attach 与 open 参数](https://github.com/microsoft/playwright-cli#open-parameters)、context / page
身份及 owner；attach 借用结束时 detach，不 close 用户或其他流程持有的浏览器。

跨流程接力同时明确工作与产物目录。已有 session 的输出位置可能仍沿创建时的目录，不能假定
更换命令 cwd 就会迁移默认快照等临时产物；复用时核实实际位置，工具支持时显式指定输出路径。

## Desktop：准备 Cua Driver，再验证目标应用

桌面验证要核对 machine、display、应用与 window 身份，权限、前台焦点、缩放和屏幕变化都会影响
动作。当前截图、坐标与录制仅是现场素材，状态变化后重新观察定位；不能把浏览器页面通过当成
原生窗口、系统对话框或设备接合通过。

按 YAML 的 expect 选择 AX 或截图证据。纯文本结果若已由同一窗口的 AX 暴露，可读取独立输出并
区分输入回显与执行结果；截图不作为所有动作的前置条件。Cua Driver 的 `get_window_state` 传
`include_screenshot:false` 且不传 `screenshot_out_file` 可仅取 AX；缺少截图只在当前验证确实需要
像素证据时才构成阻断。参数与行为按已装版本核对，见
[0.38 观察合同](https://github.com/trycua/cua/blob/cua-driver-rs-v0.38.0/libs/cua-driver/rust/crates/platform-macos/src/tools/get_window_state.rs)。

发送全局快捷键前核对系统当前前台应用与目标窗口；查询某应用的第一个窗口，不代表系统焦点已在
该应用。焦点不符先纠正并重新观察，不能用无变化的窗口数推断快捷键没有影响其他应用。

桌面操作默认准备代码也可调用的 Cua Driver。先查现有安装、版本与服务；缺失时读取
[官方 Quickstart](https://cua.ai/docs/cua-driver/quickstart)，按当前平台安装并启动，把这部分作为
测试环境准备，不因 PATH 没有命令就停止，也不先退回全局键鼠脚本。已有安装可用则复用，不要求
每轮重装。区分 Cua Driver 与 Cua Spaces、Lume、SDK，按本次所需安装，不默认拉起整套产品。

沿官方文档与已装版本核对 `permissions status`、`status`、`doctor` 和目标应用发现；安装成功或
健康命令 exit 0 都不代替阅读实际警告与验证目标能力。macOS 权限须归于实际安装的 CuaDriver
应用；启动与重启沿官方应用入口，不用 shell 后台直接运行 bundle 内二进制代替，并核对实际宿主
归属。需要用户完成系统授权时说明准确对象与实际缺项，不通过其他已授权宿主冒用权限。安装与
运行沿本次授权，系统授权仍由系统实际授予。仅 localize 或编辑指导时不据此启动环境安装。
用户已确认完成授权而实际调用仍拒绝时，核对当前版本、进程归属和本轮真实回执，按需查官方
已知问题；未能解释的矛盾保留为环境或工具状态不一致，不反复要求用户完成同一项授权。

本机可先验证 Cua 对目标应用的后台输入与观察，核对实际用户指针、前台焦点和应用结果；不凭
agent cursor 或工具成功推断没有干扰。需要前台输入或后台路线拒绝时，再选择独立测试机器、
虚拟机或约定的占用时段，不静默切换到全局输入。独立窗口、进程与 session label 都不自动构成隔离。
后台建窗与读取成功不代表该窗口已有可用输入焦点；准备后分别核对定向输入和关闭能力。按实际
回执区分执行与拒绝，不因权限齐备或健康检查通过就宣称完整场景可回放。
Cua CLI 各工具回执按实际合同解析，不能对所有 `call` 统一 `JSON.parse`：观察工具可返回 JSON，
`kill_app` 可返回文本成功回执。

不把 `osascript + System Events / Accessibility` 作为默认替代路线：它可能作用于共享前台与输入，
一次回放成功不代表低干扰或稳定。确需本机共享桌面操作时，先与用户明确操作范围及占用时段。
Agent 内置工具的可用性不代表独立脚本可调用；按[执行投影](execution-projection.md)核对实走与回放
两端能力。安装失败、系统权限不足和目标应用不支持后台操作分别处理，保留具体缺口。

输入参数通过 JSON 序列化构造，先检查真实字符串与 LF、CR、TAB 等控制字符；一次拆行不足以
推断 Driver 解释了反斜杠转义或存在相应缺陷。在选定的测试环境中，键盘输入仍可能受活动输入法
改写，须核对实际输入和结果。若借助剪贴板，先保全原状态且不暴露内容，在成功与失败出口恢复；
清空不等于恢复。操作与清理绑定本轮创建的窗口，现场坐标不固化为永久身份。

trycua 的当前桌面工具以 Cua Driver 为入口，CLI / MCP 提供观察和动作。已有 recording / replay
能力也不等于稳定代码生成：轨迹可能依赖当前元素缓存，元素 token 不能跨 snapshot / session
永久复用，录制结果须筛选后提取投影并新回放。具体能力与平台条件见官方材料，按当前安装版本
核对，不把其他产品的 computer-use 工具接口冒认为 trycua API。

参考 [Cua Driver 0.38 发布](https://github.com/trycua/cua/releases/tag/cua-driver-rs-v0.38.0)与
[录制 / 回放工具合同](https://github.com/trycua/cua/blob/c2a21e764e2cc8b3a0a187aa9ca7d688265fe389/docs/content/docs/cua-driver/reference/mcp-tools/batch-recording-and-settings.mdx)。
官方支持路线与目标环境可用性分开核对；先查实际安装、系统授权与宿主条件，只有实际观察才支持
对应桌面路径已验证的结论。

macOS 本机路线要核对 [CuaDriver.app 或 embedding 的进程身份与系统授权](https://github.com/trycua/cua/blob/c2a21e764e2cc8b3a0a187aa9ca7d688265fe389/libs/cua-driver/README.md#macos-process-identity-and-permissions)，
不以任意 CLI 进程替代已授权宿主。Driver 的 [session label](https://github.com/trycua/cua/blob/c2a21e764e2cc8b3a0a187aa9ca7d688265fe389/libs/cua-driver/rust/Skills/cua-driver/RUNTIME.md#session-lifecycle)
须沿同一 daemon 使用，它不隔离应用焦点、缓存或权限；结束本轮 session 不等于停止共享服务。

## Mobile：按实际设备与工具能力选择

核对 OS、真机或模拟器、device、app session、前后台与输入状态；沿项目当前可用工具实走与回放。
模拟器通过不代表真机、硬件或系统权限已验证，桌面远控能力不自动成为手机原生 app 自动化能力。
未确认工具支持时保留缺口，不用桌面截图、移动网页或 iPhone 遥控桌面的客户端代替 iOS / Android
原生行为证据。登录与资源接力仍沿设备和 app 的真实身份、权限与 owner，不强制套浏览器 context。

Cua 仓库有 Android 模拟器与 ADB 路线，见
[Android runtime](https://github.com/trycua/cua/blob/c2a21e764e2cc8b3a0a187aa9ca7d688265fe389/libs/python/cua-sandbox/cua_sandbox/runtime/android_emulator.py)与
[本地模拟器集成入口](https://github.com/trycua/cua/blob/c2a21e764e2cc8b3a0a187aa9ca7d688265fe389/tests/integration/sandbox_sdk/test_android_local_vm.py)。
这些代码不证明目标设备已跑通，也不推导 Android 真机或 iOS 原生 app 支持。需要专用手机驱动时，
可核对 [Appium UiAutomator2](https://github.com/appium/appium-uiautomator2-driver#readme)的 Android
真机 / 模拟器路线，或 [XCUITest](https://appium.github.io/appium-xcuitest-driver/latest/overview/)的
iOS 真机 / simulator 路线；目标 OS、设备、Xcode / WDA、签名和权限条件以当前工具合同为准。
