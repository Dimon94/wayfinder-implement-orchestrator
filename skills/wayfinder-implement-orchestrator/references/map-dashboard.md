# 票图仪表盘

shell 是静态资产，数据是唯一动线：每轮只覆盖写数据层，不重新生成 HTML。
派发优先：任何一轮都先派 maximal safe batch，再刷新数据层；仪表盘不阻塞派发。

## 定位

仪表盘是真相源投影：全部数据从 tracker、Git 与 `docs/wayfinder/estimate-log.csv`
现算，页面不承载独有信息，丢失后下一次刷新即重建。持久记录归 tracker 与 CSV。

## 文件契约

- shell：首次使用时把本 skill 的 `assets/map-dashboard-shell.html` 复制为
  `$TMPDIR/wayfinder-<map-slug>.html`（`$TMPDIR` 缺失时用 `/tmp`），之后不再改写。
- 数据层：每次刷新覆盖写同目录 `wayfinder-<map-slug>-data.js`，内容为一个
  `window.WAYFINDER_DATA = {…};` 赋值（`file://` 下 fetch JSON 受 CORS 限制，
  故数据层用 JS 赋值承载 JSON）。
- shell 内置 60s meta refresh，按「同名 + `-data.js`」约定自动重载数据层；
  浏览器常开即实时。

## 刷新与打开时机

| 时机 | 动作 |
| --- | --- |
| tickets 拆票待审批 | 刷新数据层，`open` 给用户审拆分与档位 |
| dispatch 冻结 | 先派发 maximal safe batch，派发完成后刷新数据层并 `open` |
| 执行期每次 terminal fan-in | collect/integrate/重派发完成后刷新数据层，不重复 `open` |

`open <path>`（macOS）/ `xdg-open <path>`（Linux），并向用户报告绝对路径。

## 数据层 schema

```js
window.WAYFINDER_DATA = {
  generatedAt: "2026-07-14 10:30",
  map: { title: "…", url: "…", gate: "dispatch", slug: "…" },
  totals: { done: 2, running: 3, ready: 1, blocked: 2, estimateCapMin: 240, spentMin: 95 },
  tickets: [{ id: "#12", title: "…", tier: "M", score: 4,
              state: "done|running|ready|blocked|fused|drift",
              lane: "L1", blockedBy: ["#11"] }],
  lanes: [{ id: "L1", channel: "…", worktree: "…", branch: "…",
            current: "#12", spentMin: 30, capMin: 45, state: "running" }],
  risks: { waivers: [{ id: "#13", reason: "…" }], fuses: [{ id: "#14", note: "…" }],
           patches: [{ id: "#15", title: "…" }] },
  census: [{ surface: "生产侧", status: "green|yellow|red", refs: "#12 #13" }],
};
```

shell 渲染五节：状态条、依赖 DAG（Mermaid，状态着色 + 档位标注 + lane 归属）、
lane 泳道、风险卡、六面普查表。tickets 阶段 `lanes`/`risks` 留空数组即自动隐藏。

配色沿用 improve-codebase-architecture 报告的 editorial 风格：`stone-50` 底、白卡片 +
`slate-200` 细边框、衬线标题、`text-xs uppercase tracking-wider` 小节标签；用色克制——
indigo 单一 accent，amber 警示，red 风险，emerald 完成，状态一律浅底色块；Mermaid 用
`neutral` 主题。

## 输入安全

- tracker 标题、摘要、lane、branch 和链接都是不可信输入。coordinator 写数据层时只放
  原始值；shell 渲染时转义 `& < > " '`，任何不可信值不得直接串接进 `innerHTML`，
  纯文本一律走转义或 DOM `textContent`。链接只接受 `https:` / `http:`。
- Mermaid 节点 id 只用不透明稳定 id（例如 `t123`），不用标题拼 id。标签作为
  quoted string 转义引号、反斜杠和换行；原始值无法安全表达时用 issue id 作回退标签。
- shell 是联网单文件：Tailwind CDN + Mermaid CDN，无本地依赖、无常驻进程；离线或
  CDN 失败时必须降级为纯 HTML 状态表、lane 表和风险卡，DAG 显示纯文本依赖列表。
