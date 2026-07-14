# CONTEXT — Wayfinder 编排布局词汇表

本仓库编排语境下 Herdr 布局相关术语的唯一定义处。只做词汇表，不含实现细节。

## 术语

- **Space**：Herdr UI 侧边栏的工作区（CLI 的 `workspace`）。一个 space 对应一个 map/交付
  任务和它的 integration target；各 execution lane 的 worktree/cwd 由 pane 独立携带。
  space 命名为地图主要内容 + 地图 issue 编号。
- **Tab**：space 顶部的分页，一类会话的并发容器。第一个 tab 固定为 LEAD tab。
- **Pane**：tab 内的分屏，一个 worker 会话。设计 pane 对应一个判断问题；执行 pane 对应
  一条 execution lane。
- **Decision ticket**：Wayfinder map 的 child issue，只用来解决一个决策或为决策
  清障。resolution 进入 map `Decisions-so-far`；不承载实现交付。
- **Implementation ticket**：spec 或小型化跳过证据之后的交付票，进入 execution
  lane 和 implementation dependency graph。它可回链 map，但不是 map child，也不写入
  `Decisions-so-far`。
- **LEAD tab**：每个 space 的第一个 tab，主编排者（lead）独占，label 为 `LEAD`。
- **会话类型**：worker pane 的五种一级分类，决定它归属哪个类型 tab：
  - **G（拷问/规划）**：grilling、spec 拷问、规划类会话。
  - **X（执行）**：execution lane 的执行会话。
  - **P（原型）**：prototype 探索会话。
  - **R（评审）**：集成评审、PR review 会话。
  - **D（诊断/调研）**：debugging、research、证据收集会话。
- **类型 tab**：承载单一会话类型的工作 tab，label 为 `字母-存活编号·…`，最多并发
  4 个 issue；满员时新建同字母 tab。
- **Execution lane**：一个 AFK owner、一个独立 worktree/branch 和一条可串行验证的
  implementation ticket 链。lane 内串行；lane 间在 dependency 与 mutable resources
  独立时并发。
- **Lane ID**：execution lane 的稳定短标识，形如 `L1`。X tab 和 pane label 同时显示
  lane ID 与当前 ticket 编号，例如 `L1(#142)`；lane 领取下一张票时更新括号内编号。
- **Terminal fan-in**：lead/coordinator 只在 worker `completed` 或 `blocked` 时读取一次
  final report、验证并集成，然后重算 ready frontier；routine progress 不进入 lead 上下文。
- **存活编号**：设计 tab 内是尚未关闭的 issue 编号；X tab 内是存活 lane ID。tab label
  永远只列当前存活单位。
- **阶段迁移**：同一 issue 编号随工作阶段在类型 tab 间先后出现；同一时刻同一 issue
  只允许一个 writer lane，read-only review 可以并行但必须标成 R。
