# CONTEXT — Wayfinder 编排布局词汇表

本仓库编排语境下 Herdr 布局相关术语的唯一定义处。只做词汇表，不含实现细节。

## 术语

- **Space**：Herdr UI 侧边栏的工作区（CLI 的 `workspace`）。一个 space 对应一次
  开发任务，即一个（仓库 × 分支/worktree）。命名为地图主要内容 + 地图 issue 编号。
- **Tab**：space 顶部的分页，一类会话的并发容器。第一个 tab 固定为 LEAD tab。
- **Pane**：tab 内的分屏，一个 worker 会话，对应一张票或一件事。
- **LEAD tab**：每个 space 的第一个 tab，主编排者（lead）独占，label 为 `LEAD`。
- **会话类型**：worker pane 的五种一级分类，决定它归属哪个类型 tab：
  - **G（拷问/规划）**：grilling、spec 拷问、规划类会话。
  - **X（执行）**：实现票的执行会话。
  - **P（原型）**：prototype 探索会话。
  - **R（评审）**：集成评审、PR review 会话。
  - **D（诊断/调研）**：debugging、research、证据收集会话。
- **类型 tab**：承载单一会话类型的工作 tab，label 为 `字母-存活编号·…`，最多并发
  4 个 issue；满员时新建同字母 tab。
- **存活编号**：tab 内尚在运行或未关闭的 issue 编号。tab label 永远只列存活编号。
- **阶段迁移**：同一 issue 编号随工作阶段在类型 tab 间先后出现（如 X → R）；
  同一时刻同一编号只允许存在于一个类型 tab。
