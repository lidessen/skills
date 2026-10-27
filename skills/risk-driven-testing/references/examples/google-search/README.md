# Google 搜索：行为与执行投影

本目录模拟一个测试项目的根目录。Google 是外部被测系统，项目本身没有产品 `src/`。
[`specs/stories/google-search.yaml`](specs/stories/google-search.yaml) 描述搜索 Playwright
文档、细化查询并打开官方定位器文档的行为；代码按[执行投影](../../execution-projection.md)
从这份行为提取步骤，并使用 Playwright Test 的 fixture、断言和报告。

```text
google-search/                          项目根目录
├── specs/stories/google-search.yaml    行为知识库：业务动作与期望
├── tests/e2e/                          本例的 Web 执行投影
│   ├── actions/google-search.ts        搜索、读取结果和打开文档的具体步骤
│   ├── flows/google-search.ts          runStory(page)：组装动作与断言
│   ├── google-search.spec.ts           运行入口：本地验证与真实站点用例
│   └── fixtures/google-search-seam.ts  本地验证桩，不是业务投影的必要部分
├── playwright.config.ts                测试发现、fixture 与浏览器配置
├── package.json / package-lock.json    依赖与运行命令
└── tsconfig.json                       类型检查配置
```

这是一种项目布局示例；实际目录沿目标项目已有约定选择。YAML 可以独立作为知识库保留，
本例选择 Web 流程不代表每份 YAML 都要生成 E2E 测试。组装代码与测试入口的文件注释都指向
源 YAML，动作和组装分别维护：
[动作](tests/e2e/actions/google-search.ts) → [组装](tests/e2e/flows/google-search.ts) →
[测试入口](tests/e2e/google-search.spec.ts)。这里没有为凑层级添加 feature、case 或 `ref`。

`runStory` 使用调用方传入的活 `Page`；导入业务模块不启动浏览器，也不关闭借入的页面。
调用者需在 Playwright Test 环境内调用，由原 owner 管理页面生命周期和起始条件。

第二次搜索是否刷新，以提交后观察到带该查询的成功主文档导航响应、当前文档 URL 和
搜索框值为依据。两次结果链接相同也可以继续；只有 URL、标题或旧列表变化不足以证明刷新。
若站点采用其他刷新方式而无法取得此证据，流程以 `UNKNOWN` 跳过；结果区域观察不足也跳过。
结果链接会等待出现；首次结果须有文档主题，官方域名本身不足以证明这一点。
跳过不是行为通过。Playwright 可能对包含跳过的测试返回退出码 0，必须同时查看报告。

## 运行

需要 Node 24、npm 和本机 Chrome。依赖由 lockfile 固定，锁定包来自公开 npm registry，
并使用锁文件中的 integrity 校验。以下命令在本目录（示例项目根）执行：

```sh
npm ci
npm run typecheck
npm test
```

默认测试中 `tests/e2e/fixtures/google-search-seam.ts` 拦截所有页面网络请求：Google 与 Playwright 文档由本地桩回填，其他请求
直接中止；真实 Google 用例默认跳过。`RDT_CHANNEL` 可选择其他已安装的 Playwright 浏览器通道。
在获得授权且 Google 可访问时，可用 `RDT_REAL=1 npm test` 运行真实入口；这会实际访问外站。

## 本轮证据

2026-10-27 实走中，首页和搜索框已观察，输入第一次查询并提交后 Google 返回 `/sorry`、
HTTP 429 验证页；未绕过验证。第一次结果期望、第二次搜索及文档页在真实站点均未观察。

本候选更新后，`npm run typecheck` 退出码 0；`npm test` 退出码 0，Playwright 报告
4 passed、3 skipped。四项本地测试分别验证：新的主文档响应后延迟出现相同链接仍能到达文档页；
只有 `pushState`、标题变化和旧列表新增链接时，不会认定有新搜索；官方域名的无关页面不会被
当作文档结果；同名的非目标链接排在前面时仍会打开已确认的官方文档。两个本地未知路径和真实
站点入口均被跳过。

本地桩仅证明这些受控接缝，不能证明真实 Google 结果页的结构、定位、刷新方式或文档断言。
本轮没有真实站点的完整代码回放，真实行为仍未验证。

公开依赖锁在独立临时目录使用空 npm 缓存执行 `npm ci --ignore-scripts` 验证，退出码 0，
安装了五个锁定包；它们的版本与 integrity 均与原候选一致。
