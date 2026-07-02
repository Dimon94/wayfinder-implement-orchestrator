# 阶段门禁子线程派发包

用于派发一个非实现类门禁子线程：PRD 合成、issue 拆分、只读 review
或证据收集。

```text
项目：
父编排线程：
门禁：prd | issues | review | evidence
路由 skill：/to-prd | /to-issues | /code-review | none
基线分支：
基线提交：

真相源坐标：
- Wayfinder map：
- PRD：
- Tracker issues：
- Research/prototype artifacts：
- Source worktree：

目标说明：
- 如果 Source worktree 不是可创建 Codex 线程的 project target，就在已创建
  的项目线程里把这些绝对路径当作只读证据读取。

允许范围：
- 可以写入/发布：
- 只读：
- 禁止范围：

停止条件：
- 如果需要用户判断、缺少证据、tracker 鉴权失败、真相源冲突或需要改代码，
  立即停止并报告。

预期产物：
- PRD URL/body | issue split proposal/issue URLs | review report | evidence

`prd` 和 `issues` 门禁的 tracker 发布保护：
- 创建 issue 前，先搜索/读取 tracker，确认同一个 PRD 或同名 slice 是否已有
  子 issue。如果存在部分重复，停止并报告已有 ID，不要再发布一组重复 issue。
- 不要把 Markdown 正文塞进 shell 引号里的 inline string。使用临时 body 文件、
  JSON encoder，或 tracker helper 的文件输入，确保反引号、checkbox、`$`
  和引号原样保留。
- 按依赖顺序发布。每次 create/update 后立刻读回 tracker issue，核对标题、
  label、父引用、依赖文本、checklist 数量，以及源正文里的代码字面量。
- 如果 create/update 部分成功或读回失败，停止。final report 必须列出所有已
  创建 ID、失败字段，以及 rerun 是否会造成重复工作。

执行规则：
- 使用 fresh session。
- 不要再派发子线程。
- 不要进入 `/implement`。
- 不要集成、push、打开/更新 MR，也不要评论 MR。
- 在本子线程 final answer 中输出完整 final report。
- 如果 `send_message_to_thread` 可用，final report 准备好之后，向父编排线程
  发送一个紧凑 handoff。
- 如果无法 handoff 给父线程或 handoff 失败，在 final report 里说明。

Final report：
门禁：
状态：completed | blocked
线程：
产物：
父线程 handoff：sent | unavailable | failed <reason>
已使用的真相源坐标：
-
验证：
-
`prd`/`issues` 门禁创建的 tracker items：
- <id/url, readback status, dependency state>
阻塞：
-
下一门禁建议：prd | issues | dispatch | integrate | mr | ask-user | blocked

父线程 handoff message：
门禁：
状态：
线程：
产物：
阻塞：
下一门禁建议：
```
