# 人类维护者文档样本与观察

人类维护者写的文档样本，以及从中观察到的特征。样本有两个用处。动笔前挑与手头文档同类、
同语言的一两份从头读到尾，让接下来写的东西跟着这种说话方式走。写完需要校准时再并排
对照相应段落，看读者的问题怎样得到解释、作者怎样表达立场。两个用处都不模仿具体句子，也不把
某个项目的习惯当成全行业标准。下面的“值得看什么”一栏是给挑样本用的，不代替原文。
链接指向上游源文件，版本会变；访问受限时按 SKILL.md 的样本降级方式继续，不把找齐样本作为写作门槛。

## 英文样本

| 类型             | 项目 / 文件                                                                                                          | 值得看什么                                                                                                                                           |
| ---------------- | -------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| README（小工具） | [esbuild README](https://github.com/evanw/esbuild/blob/main/README.md)                                               | 全文 40 行。开头直接是问题：“Our current build tools for the web are 10-100x slower than they could be”。特性列表是名词短语加链接，没有形容词        |
| README（CLI）    | [ripgrep README](https://github.com/BurntSushi/ripgrep/blob/master/README.md)                                        | 有一节 “Why shouldn't I use ripgrep?”，列举不适用场景；比较其他工具时给测量数据                                                                      |
| README（CLI）    | [fzf README](https://github.com/junegunn/fzf/blob/master/README.md)                                                  | 长文档，几乎全是可运行的例子和它们的效果；解释性段落短                                                                                               |
| README（库）     | [tokio README](https://github.com/tokio-rs/tokio/blob/master/README.md)                                              | 一句话定义后给例子；MSRV、LTS 等维护政策写成具体版本和日期                                                                                           |
| 设计文档         | [Go: Less Error-Prone Loop Variable Scoping](https://github.com/golang/proposal/blob/master/design/60078-loopvar.md) | 背景直接给出错代码；小节标题是主张（“Static analysis is not a viable alternative”）；有 Open issues；措辞里保留 “perhaps Go 1.22 if the stars align” |
| 设计文档模板     | [Go proposal TEMPLATE](https://github.com/golang/proposal/blob/master/design/TEMPLATE.md)                            | Abstract / Background / Proposal / Rationale / Compatibility / Implementation / Open issues，全部一句话说明                                          |
| RFC              | [Rust RFC 1105: API evolution](https://github.com/rust-lang/rfcs/blob/master/text/1105-api-evolution.md)             | Drawbacks and Alternatives、Unresolved questions 是正式节；作者标出 “(unofficial)” 的推测段                                                          |
| 设计原则         | [Django design philosophies](https://github.com/django/django/blob/main/docs/misc/design-philosophies.txt)           | 开头一句 “This document explains…Its goal is to explain the past and guide the future”；每条原则两三句，直接说 “Redundancy is bad”                   |
| 贡献指南         | [curl CONTRIBUTE](https://github.com/curl/curl/blob/master/docs/CONTRIBUTE.md)                                       | 命令式短段；直接说什么会被拒                                                                                                                         |
| 何时不用         | [SQLite: Appropriate Uses](https://sqlite.org/whentouse.html)                                                        | 单独一节 “Situations Where A Client/Server RDBMS May Work Better”，逐条写自己不适合的场景                                                            |

## 中文样本

| 类型                  | 项目 / 文件                                                                                                                                 | 值得看什么                                                                                                                                                               |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 组件库介绍            | [Ant Design 介绍](https://github.com/ant-design/ant-design/blob/master/docs/react/introduce.zh-CN.md)                                       | 第一句 “`antd` 是基于 Ant Design 设计体系的 React UI 组件库，适合企业级中后台产品与前台桌面网站”；用引用块写 “强烈不推荐使用已构建文件” 并说原因；版本边界写成具体版本号 |
| FAQ                   | [Ant Design FAQ](https://github.com/ant-design/ant-design/blob/master/docs/react/faq.zh-CN.md)                                              | 问题是用户真问过的；回答直接说“不会支持”“这是设计如此”                                                                                                                   |
| 快速上手              | [Vant 快速上手](https://github.com/youzan/vant/blob/main/packages/vant/docs/markdown/quickstart.zh-CN.md)                                   | 按读者任务分节（现有项目 / 新项目）；推荐工具时说明理由（“由 Vant 作者开发…第一优先级支持”）                                                                             |
| 最佳实践              | [TiDB 最佳实践](https://github.com/pingcap/docs-cn/blob/master/best-practices/tidb-best-practices.md)                                       | 逗号串起的长句解释机制；“这部分用户不需要担心”；限制写成 5000 条 / 6MB / 10G；用 “比如把数据库当做计数器用” 这类具体反例                                                 |
| 架构说明              | [TiDB 整体架构](https://github.com/pingcap/docs-cn/blob/master/tidb-architecture.md)                                                        | 每个组件一段，说它做什么和不做什么                                                                                                                                       |
| 设计文档              | [RocketMQ 设计](https://github.com/apache/rocketmq/blob/develop/docs/cn/design.md)                                                          | 每个机制先讲问题（遍历 commitlog 检索低效）再讲结构；数字具体到 1G、20 位文件名、400M                                                                                    |
| 教程                  | [阮一峰 ES6 入门：简介](https://github.com/ruanyf/es6tutorial/blob/gh-pages/docs/intro.md)                                                  | 用读者常问的问题做小节标题；历史叙述带具体年份和原因；“日常场合，这两个词是可以互换的” 这种替读者做的判断                                                                |
| 推广型 README（对照） | [Sentinel 介绍](https://github.com/alibaba/Sentinel/wiki/介绍)、[Hutool README](https://github.com/dromara/hutool/blob/v5-master/README.md) | 加粗小标题特性列表、“丰富”“完备”“广泛”。它们能成立是因为每条后面跟着具体事实（近 10 年双十一、500 台集群、Spring Cloud/Dubbo/gRPC）。写说明文档时不沿用这种口吻          |

## 观察到的共同特征

**开头。** 第一句说它是什么、给谁，或直接说要解决的问题：中英文样本各约一半以 “X is a…” /
“X 是一个…” 开头（中文 26 篇里 11 到 12 篇，取决于把 frontmatter 后哪一行算第一句），这个结构
本身不是 AI 味。第二句立刻给具体事实：版本、二进制名、
平台、去哪看。设计文档摘要直接写决定。口号只放在页头，正文不重复；没有 “In today's world”，
没有 “本文将带你”。Django、TiDB 会用一句 “This document explains…” / “本文档总结…” 说明范围，仅此一句。

**先说 why。** esbuild、Vite、Sentinel 都先说现状有什么问题，再说自己做了什么。README 读者
第一件事是判断要不要继续读。

**限制与不适用场景是正式内容。** ripgrep、SQLite 单开一节；antd、TiDB 用引用块或一句话
（“强烈不推荐”“这并不意味着在任何场景都能”）。维护者知道自己的东西哪里不行，并且写出来。

**数字代替形容词。** 10-100x、5000 条、6MB、1G、20 位、近 10 年。没有数字时用具体行为
（ripgrep：“won't search files ignored by your `.gitignore`… won't search hidden files and it won't
search binary files”），不用 “高效”“稳定”。

**结构随内容。** esbuild README 只有 “Why?” 一节；Go 设计文档 Rationale 一节下有 14 个主张式
小节。节数、列表长度、段落长短都不整齐：中文样本约 90 个多项列表里 25 个是三条，
13 个超过八条；ripgrep 一个列表里混着 “It can…” “Like other tools…” “Applies…” 三种句式。
重要处写四段，次要处一句带过，模板里没内容的节留空或写 “None.”。

**立场明确。** “Redundancy is bad.” “不推荐。对内接口不保证兼容性。” “Static analysis is not a
viable alternative.” “非常不推荐手动部署，后期的维护和升级会很麻烦。” 维护者替读者做了取舍，
并说理由；否定后面常跟条件或替代（“通常情况下慢 20%……如果可能，建议避免”）。

**“冗余”在哪里。** 人类说明文档删掉重复和举例后其实很短，但那些句子不是废话。TiDB 讲 Raft：
“每次写入都要写入多数副本，才能对外返回成功，这样即使丢掉少数副本，也能保证系统中还有最新的
数据。比如最大 3 副本的话，每次写入 2 副本才算成功……相比 Master-Slave 方式的同步……写入的延迟
取决于最快的两个副本，而不是最慢的那个副本。所以使用 Raft 同步的情况下，异地多活成为可能。
在典型的两地三中心场景下……”一个机制，后面跟后果、例子、对比、推论、场景五层。Django 每条
原则都是“主张 → For example → 限定”：“The various layers of the framework shouldn't know
about each other… For example, the template system knows nothing about web requests…
Although Django comes with a full stack for convenience, the pieces are independent.”
Effective Go 讲完 range 的例子后加一句 “Finally, Go has no comma operator”，是替读者答下一个
会问的问题。这些句子不增加事实，增加的是理解。模型产物里这一层普遍缺席：语料中文每千字
0.6 到 2.7 处举例标记、英文每千词 1.7 到 5.2，产物多为 0。

**设计说明的推进方式。** 提案类（Go、Rust RFC、KEP）按模板走问题 → 方案 → 被否方案 → 未决；
架构和最佳实践类（TiDB、RocketMQ）是“机制 → 后果 → 建议”：先讲 Raft 写多数派，再推出延迟取决于
最快的两个副本，再收“但这并不意味着任何场景都能跨机房”。两种都先给真实代码、数字或事故，再给结论。

**不确定性有具体形状。** Go 提案写发布时间是 “perhaps Go 1.22 if the stars align”；Redis 写平台支持是
“our support for this platform is best effort and Redis is not guaranteed to work”；ripgrep 写某些
构建配置是 “bugs I don't know how to fix and don't have the time to fix”。每一句都说了不确定的是什么、
到什么程度、原因是什么。“may vary depending on your use case” 三样都没说。

**结尾在内容结束处。** 链接、许可、社区入口或最后一个事实。没有总结段，没有 “希望本文对你
有帮助”。

**段末不总结，节首不预告。** 读完一节直接进入下一节。需要引导时指向别处（“See the FAQ”“详见 X”），
而不是复述。

以上是这批样本的观察，不是禁止总结或复述的规则。新文稿中的重复仍要看其阅读作用：
唤回上下文、加深印象和强调重要性都可以成立，不能因为样本少见或没有新增事实就删掉。

**不追求光滑。** 样本里留着拼写错误、半角全角混杂、TODO 注释和个人化的旁白（“(Apologies!)”、
“那啥，试试 npmmirror”）。精确但不打磨过的句子是维护者文档的常态；反过来，每句都圆润、
每段都等长才显得不像人写。写的时候不要为了“完整”“工整”添内容；也不要故意留错。

**推广口吻与说明口吻是两套。** 同一篇 Hutool README 前半用加粗特性和“强大”，后半讲 PR 原则时
换成一句成段的个人说明。企业维护的 README（Redis、Vite、Sentinel）最接近 LLM 的节奏：加粗
小标题、“Whether you're…”“In summary”、评价性总结句。校准时以单维护者 README、RFC、FAQ、
最佳实践这类说明口吻为准。

## 使用方式

写完初稿后选同类样本对照三处：开头前三句、任意一个中段（列表和段落的比例、每条里的事实
密度）、结尾。差别明显的地方回到 [ai-patterns.md](ai-patterns.md) 找对应症状。样本的项目
惯例（emoji 特性列表、编号小节）不自动迁移到别的项目。
