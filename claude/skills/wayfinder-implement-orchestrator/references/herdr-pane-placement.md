# Herdr Pane 落点与 Space 容量

只有在需要创建、补建或替换 Herdr worker panes 时才读取本文件。

## 术语与坐标

- Herdr UI 侧边栏的 "space" 就是 CLI 的 `workspace`；本文统一说 space。
- lead 自身坐标来自环境变量：`HERDR_WORKSPACE_ID`、`HERDR_TAB_ID`、`HERDR_PANE_ID`。

## 硬规则：落点必须显式

裸 `herdr pane split` 和裸 `herdr agent start`（不带 `--workspace`/`--pane`/`--current`）
的落点是**用户当前聚焦的 pane/space**，不是 lead 所在的 space，也不是 map 对应的
space。用户随时在切换视图，裸命令等于把 worker 派进随机 space。因此：

- 每条创建命令必须显式定位（`--workspace <id>`、`--pane <id>` 或 `--current`）。
- 每条创建命令必须带 `--no-focus`，批量派发不许抢用户焦点。

## 解析目标 space

1. 确定 map key：优先 tracker 号形态，例如 `#608`。
2. 运行 `herdr workspace list`，在 labels 里找包含 map key 的 space，含尾号变体
   （`剧本格式#608`、`剧本格式#608-2`）。命中的集合就是候选池。
3. 无命中时：若 lead 自己 `HERDR_WORKSPACE_ID` 的 label 与当前 map 明确一致，直接用；
   否则创建 `herdr workspace create --label "<map-label>" --cwd <repo-root> --no-focus`
   并记录返回的 `workspace_id`。
4. lead 正运行在哪个 space、用户正看着哪个 space，都不是派发依据；map key 匹配才是。

## 容量与同名加尾号溢出

- 每个 space 的 pane 上限默认 4（按 space 内现有 pane 总数计，含 lead pane；用户
  显式要求时可调整）。
- 每次创建前用 `herdr pane list --workspace <id>` 计数，不凭记忆。
- 候选池按尾号从小到大找第一个未满的 space；全满则创建下一个尾号：
  `herdr workspace create --label "<base-label>-<n>" --cwd <repo-root> --no-focus`，
  `<base-label>` 为不带尾号的原 label，`<n>` 从 2 递增。溢出 space label 必须保留
  map key，让 agent list 中同一 map 的 workers 仍然归组。
- 同一批 workers 允许跨多个尾号 space；worker 归属以记录坐标为准。
- 批次收尾、space 内 panes 全部关闭后，用 `herdr workspace close <id>` 关闭空的
  溢出 space。

## 标准创建命令

```
herdr agent start <pane-label> \
  --workspace <workspace_id> \
  --cwd <worktree-or-repo-path> \
  --no-focus \
  -- claude --dangerously-skip-permissions
```

需要在已有 pane 旁精确布局时改用：
`herdr pane split --pane <pane_id> --direction right|down --ratio 0.5 --cwd <path> --no-focus`，
然后 `herdr pane rename <new-pane> <pane-label>`，
再 `herdr pane run <new-pane> 'claude --dangerously-skip-permissions'`。

## 创建后验证（每个 pane 必做）

1. `herdr pane get <pane_id>`，确认 `workspace_id` 等于目标 space。
2. 落点不符时 `herdr pane close <pane_id>`，重新解析目标 space 后用显式参数重建；
   连续两次落点错误则停下问用户。
3. 把 space label、`workspace_id`、pane label、`pane_id` 写进 worker 坐标记录，并要求
   worker readback 原样回报。
