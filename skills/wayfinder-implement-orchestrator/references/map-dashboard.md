# 票图仪表盘

两个必看节点生成并打开给用户：tickets 拆票待用户审批时、dispatch 冻结前。执行期每次
terminal fan-in 重算 frontier 后覆盖写同一文件，只写不重复打开。

## 定位

仪表盘是真相源投影：全部数据从 tracker、Git 与 `docs/wayfinder/estimate-log.csv`
现算，页面不承载独有信息，丢失后下一次重算即重生成。持久记录归 tracker 与 CSV。

## 文件与打开

- 路径固定：`$TMPDIR/wayfinder-<map-slug>.html`（`$TMPDIR` 缺失时用 `/tmp`），覆盖写。
- 联网单文件：Tailwind CDN + Mermaid CDN，无本地依赖、无常驻进程；离线或
  CDN 失败时必须仍显示纯 HTML 状态表、lane 表和风险卡。
- `<head>` 内加 `<meta http-equiv="refresh" content="60">`，浏览器常开即自动跟新。
- 必看节点用 `open <path>`（macOS）或 `xdg-open <path>`（Linux）打开，并向用户报告
  绝对路径。

## 版式

1. **状态条**：map 标题/链接、当前门禁、票数统计（done/running/ready/blocked）、
   总预估上限 vs 已耗墙钟、生成时间戳。
2. **依赖 DAG**：Mermaid `graph TD`，每票一节点，节点文本 `#issue 档位 摘要`，边为
   Blocked by。状态着色：灰 = blocked、蓝 = ready、黄 = running、绿 = done、
   红 = 超估熔断/漂移。执行期节点追加 lane 归属。
3. **Lane 泳道**（dispatch 起）：每 lane 一行——执行通道、worktree/branch、当前票、
   已耗墙钟 vs 档位上限。
4. **风险卡**（dispatch 起）：L 豁免票及不拆理由、超估熔断记录、执行期修补票。
5. **六面普查表**：变更面普查六面各一格——绿 = 有票（列 issue 号）、黄 = map 边界行、
   红 = 未着落。

tickets 节点渲染 1/2/5；3/4 从 dispatch 起出现。

## 输入安全

- tracker 标题、摘要、lane、branch 和链接都是不可信输入。写入 HTML text/
  attribute 前转义 `& < > " '`；链接只接受 `https:` / `http:`。
- Mermaid 节点 id 只用不透明稳定 id（例如 `ticket_123`），不用标题拼 id。标签
  作为 quoted string 转义换行、反斜杠和引号。
- Mermaid source 通过 DOM `textContent` 写入容器，不把 tracker 文本直接串接到
  `innerHTML`。原始值无法安全表达时使用 issue id 作回退标签。
