# Skills · Agent 维护入口

先读 [README](README.md)，再按任务选择根 `skills/` 中的 `SKILL.md`，只展开需要的参考资料。
这里维护可跨项目复用的方法；项目的组件模型、运行契约、部署命令和常驻规则留在所属项目。

- 根 `skills/` 是技能源码的唯一维护位置，不另建 `.agents/skills/` 副本。编辑指导载体用
  [agent-guidance](skills/agent-guidance/SKILL.md)，发展尚待验证的方法用
  [skill-incubator](skills/skill-incubator/SKILL.md)。
- 内容来源、适配原因和项目边界见 [MIGRATION.md](MIGRATION.md)。历史理论原文的身份与引用边界见
  [theory/README.md](theory/README.md)。
- 修改技能时一起核对 Frontmatter、触发边界、引用、脚本和资源；详细方法放按需参考，避免把
  项目命令、私有现场或整份研究记录带成通用要求。文章保留作者语气、出处与 `_` 草稿前缀。
- `skills.sh.json` 的展示分类与在线 Pack 分别维护；源码或展示变化不代表 Pack 已更新，
  安装副本也不会自动刷新。来源和版本变化先核对差异，保留项目独有工作。
- 按实际改动验证格式、引用和相关脚本，说明静态核对、执行观察及方法效果各自的证据；
  没有运行验证就保留未知。提交、推送、安装和更新 Pack 按本次任务授权执行。
