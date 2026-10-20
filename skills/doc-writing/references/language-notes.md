# 中英文各自的表达习惯

这些是从维护良好的开源文档中观察到的习惯，用来校准，不是格式规范。项目已有约定时
以项目为准；同一份文档内保持一致比选哪一种更重要。

## 中文

**混排与标点。** 中英文之间是否留空格分两派：前端和数据库文档（antd、Vant、TiDB、阮一峰）严格加空格
（`TiDB 是一个兼容 MySQL 协议和语法的分布式数据库`），Java 系文档（Hutool、RocketMQ）基本不加（`支持JDK8+`）。
跟随项目已有写法；没有惯例时加空格。英文紧邻中文标点时不加空格。正文用全角标点，并列用顿号，
代码、命令、路径用反引号包住并保留半角。括号补充很常见并且常承载关键限定：`（默认）`、
`（不要引用 @types/antd）`、`（需要注意的是超过订阅队列数的 Consumer 实例无效）`。

**术语与过度翻译。** 领域术语和社区惯用语保留英文，不翻译成没人用的中文。26 篇中文样本里
issue 126 次、“议题”0；token 129 次、“令牌”0；Pull Request / PR 34 次、“拉取请求”只在 RocketMQ
指“拉取消息的请求”时出现；hook 5 次、“钩子”1；“哈希”6、“散列”0。Region、Raft、Producer、
tree shaking、Key-Value 同样保留。已被社区接受的译名照用（“开箱即用”9 次、“运行时”7 次）。
判断标准是目标读者社区怎么叫，不是能不能译：跟随项目已有中文文档；没有先例时保留英文，
第一次出现跟一句中文解释。命令、参数、代码标识符、文件名、错误信息原文一律不译（`--dry-run`
不是“干跑”）。英文习语不逐字译：“under the hood”是“内部实现”，“battle-tested”是“在生产
环境跑过”，“if the stars align”是“顺利的话”。全篇一个叫法，不轮换同义词。

**用英文习惯写中文是最常见的不自然。** 中文原生写法让主语直接做动作、用动词而不是名词化短语，
靠上下文而不是代词和连词衔接：

- 每句都带主语和代词回指（“它”“这”“这些”起句）：中文承前省略主语，或重复名词。
- 英文的定语从句和 make / allow 结构照搬：“其他搜索工具所服务的许多使用场景”“这使得可以
  在模式中使用环视”“仍然存在某个本 README 未列出的、你所依赖的其他功能”。中文把从句拆成
  并列短句，按说明顺序排：“你依赖的某个功能，本 README 还没有列出来”。未列出不能改写为
  不支持，也不能凭语境猜出其他工具是否支持。
- 冠词式的“一个”（“一个高性能的日志库”）：删掉，或换成有信息的限定。
- 显式逻辑连词成套出现（“因为……所以……”“虽然……但是……”“如果……那么……”）、“当……时”连排：
  中文常只留后半（“Redis 不可用，就放行不限速”），连词留给真正需要标记转折的地方。
- 句首“然而”“此外”“同时”“另外”对应 However / Additionally：语料 26 篇里句首“然而”0 次、
  “此外”3、“同时”2、“另外”6，而且“另外”后面都跟着新事实，不是复述。
- 复数和时态标记照英文加（“用户们”“将会”“已经……了”）：中文靠语境。
- 引号、逗号、句号用半角：中文正文用全角，见上。

- `对配置进行加载` → `加载配置`；`实现了对……的支持` → `支持……`。
- `被` 字句只在受事确实是话题时用：`文件被删除后` 可以，`该功能被设计为……` 通常是英文思维。
- 长定语堆在一个名词前时拆成短句：`基于令牌桶的、按域名维度的、可由运营配置的限速方案`
  → `按域名限速，用令牌桶实现，运营可以改单个域名的额度`。“的”本身不是问题，说明型文档里
  “的”比推广文案还多；问题是一口气修饰到读者要回头重读。
- `它是……的`、`……是十分重要的` 这类判断句多半可以换成陈述事实。
- `进行` 作形式动词填充（`进行安装`、`进行消费`）在部分项目里很多，但前端文档几乎不用；
  能直接写动词就直接写。
- 译文痕迹：`我们认为，这种模式为 X 提供了最佳平衡` 这类评价句，`这听起来可能……但` 的让步开头，
  以及每个术语后都跟英文括注。本地写的文档直接给结论和条件。

**节奏。** 中文技术文档接受用逗号串起来的长句，只要一句只推进一个意思（TiDB、阮一峰的文档都这样写）。
段落长短随内容变化：一段可以只有一句（“这部分用户不需要担心。”“不推荐。对内接口不保证兼容性。”）。
重要的地方写四段，次要的地方一句带过，不追求每节等长。

**人称。** 维护者自称“我们”并承担决策（“我们对事务的大小做了限制”）；对读者用“你”或省略主语。
“您”集中在阿里系和商业文档，人类文档里“你”“您”混用也不少见，但新写时选一个用到底。
指令用“请 + 动词”，步骤用“即可”“就可以了”收尾；不用“让我们”。

**少见的写法。** 26 篇中文样本（汉字约 4.7 万，另含代码和英文）里：`综上所述` 1 次（承接三条列表
后做真实推论）、`值得注意的是` 1 次（引出具体数字）、`总而言之`/`赋能`/`致力于`/`本文将`/
`不仅……而且` 0 次、`让我们` 1 次（“请让我们知道”）、`首先/其次/最后` 只有两处连成整套。
说明型正文里感叹号为 0，`暂无计划` 为 0；维护者写 `不支持`、`无法`、`不再支持` 加版本号。四字短语排比、“……性”
名词堆叠、`强大的`、`一站式`、`优雅` 全部出自推广型 README。这些不是禁词，出现时先问
这句在传达什么事实；删掉或换成事实通常更好。推广口吻（加粗小标题特性列表、社会证明数字、
标题 emoji）读者能识别，写说明文档时不沿用。

## English

**Voice.** Maintainers write "we" for themselves and "you" for the reader, and use the
imperative for instructions ("Check out the getting started instructions"). Contractions
are normal ("loops like this one don't do what they look like they do"). Passive voice is
fine when the actor is irrelevant ("Files removed locally are not deleted").

**Sentences.** Mix lengths freely. A short declarative after a long explanation is the
usual anchor: "That is, this code has a bug." "SQLite does not compete with client/server
databases. SQLite competes with fopen()." One sentence, one point. Fragments are fine in
lists and captions, rare in body prose. README paragraphs run 1–4 sentences; many are a
single sentence introducing a command or code block.

**Concreteness.** Numbers, versions, flags, file names and error messages carry the
document; adjectives do not. "10-100x slower than they could be", "~14k min.gz'd",
"added in curl v7.87.0", "about 1 in 8,000 loops" are how maintainers say fast, small,
new and rare. Claims point outward ("See the FAQ", "see linkgit:git-rebase[1]") instead of
being restated. Staleness is marked: "as of this writing (2015)", "The currently existing
filter types (curl 8.5.0) are:".

**Limitations.** Stated flat, with the reason and often a workaround: "SQLite will work
over a network filesystem, but because of the latency ... performance will not be great."
"none of them seem to work right ... and I don't have the time to fix." Hedges name the
condition: "any site that gets fewer than 100K hits/day should work fine", "our support for
this platform is _best effort_". Empty template sections stay empty ("None.") rather than
being padded.

**Punctuation.** 16 of 22 sample files contain no em dash at all; commas, periods, colons,
`--` and parentheses do that work. Parentheticals are the main aside mechanism and are very
frequent. Exclamation marks in prose are situational ("(Please file a bug report!)").
Question headings appear in a few READMEs and only as questions a reader would ask ("Why
shouldn't I use ripgrep?"); rhetorical questions in body text are rare.

**Rarely seen.** Across ~14,600 lines: "In conclusion", "Key Features", "seamless",
"delve", "crucial", "empower", "streamline" 0; "In summary" 1; "worth noting" 4;
"robust" 2; "Whether you're" 1. Bold lead-in bullets occur in 6 files and cluster in
corporate READMEs; single-maintainer READMEs and RFC-style docs use none. Not a banned
list: when one shows up, ask what fact it stands in for and write the fact.

**Chinese habits carried into English.** These show up when the writer thinks in Chinese,
including when translating Chinese docs:

- Comma-spliced run-ons (逗号串句): "The worker takes a task, checks the bucket, if no
  token it requeues." Break into sentences or use a conjunction; English readers expect a
  period where Chinese uses a comma.
- Missing or mechanical articles and plurals: "config file is in home directory" /
  "the configs". Decide whether the noun is specific, countable, or generic.
- Topic-comment order: "This option, we do not recommend." → "We do not recommend this
  option."
- Word-for-word verbs and hedges: "carry out" (进行), "realize" / "achieve" (实现) for
  implement or support, "solve the problem of" (解决……问题), "relatively" (比较),
  "a certain" (一定的), "the related / relevant" (相关), "at present" (目前), "and so on"
  (等), "at the same time" / "meanwhile" as a paragraph opener (同时), "through configuring"
  (通过配置), "make X become".
- Impersonal 建议 rendered as "It is recommended to" in every paragraph. Maintainers write
  "We recommend" or the imperative ("Use TiUP"). Same for "In addition" (此外) and
  "However" (但是) opening consecutive paragraphs when the Chinese used them as light
  connectors; drop them.
- Evaluative idioms translated as imagery: 极具亮点 as "a real highlight", 非常方便 as
  "very convenient and easy to use", 会很麻烦 as "will be troublesome". Translate the
  judgment in plain English ("performs well on OLAP queries", "is easy to use", "is hard
  to maintain") and keep its strength; do not upgrade or soften it.
- Jargon calqued literally: 压测 is "load test", not "pressure test"; 灰度 is "canary" or
  "staged rollout", not "gray release"; 兜底 is "fallback"; 落地 is "ship" or "roll out",
  not "land"; 闭环 in the business sense has no English equivalent and is usually a
  placeholder for a fact.
- Tense drift: describe behavior in the simple present throughout; do not switch to
  "will" because the Chinese had 会.

**Translating.** The unit is the meaning of a sentence, not its clause order. Read the
source sentence, ask how a native maintainer would state that meaning, then check that
nothing was added or dropped. Keep the source's structure, facts, stance, hedges and
omissions; a translation is not a rewrite. Terms, commands and community words follow the
rules above. If the source itself has AI-flavor tells, translate them faithfully and say so
in the delivery note; fixing them is a separate task the user has to ask for.

中英文各自的完整高频词表、句式和标点痕迹见 [ai-patterns.md](ai-patterns.md)；这里只记语料里
观察到的频率。两种语言共用的规则（标题、加粗、列表、结尾）在 SKILL.md 的“写句子时”一节，
不在这里重复。
