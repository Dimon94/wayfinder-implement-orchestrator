# 拆票覆盖普查

进入 `tickets` 门禁前读取本文件；执行期出现修补票、被推翻合同或票面外发现时，
重读「执行期漂移控制」。

## 变更面普查

拆票真相源（spec、map resolutions）默认只写生产侧。发布 implementation tickets 前，
逐面普查下表；每一面要么有票，要么在 map 的 Not yet specified / Out of scope 追加
一行边界。六面各有着落，`tickets` 门禁才通过。

| 变更面 | 普查问题 | 证据动作 |
| --- | --- | --- |
| 生产侧 | 每个新合同/writer/compiler tracer bullet 是否可独立验证 | 逐条映射到 spec/route 真相源 |
| 消费投影面 | 每个新后端事实在 read model、UI 动作/进度/文案、readback 的呈现由哪张票交付 | 枚举全部消费点，逐点找到票或边界行 |
| 旧链对位 | Destination 替换现有链路时，旧链用户可见面（按钮、进度、产物展示、操作闭环）在新链的对位物是什么 | 做一次旧链对位盘点：旧面 → 新票或显式移除决策 |
| 旧真相退役 | 每个被替换的 legacy 真相（artifact/route/writer/字段）还有哪些活跃消费者 | 消费者普查：grep 引用点；逐消费者一张迁移票；退役票 Blocked by 全部迁移票 |
| 真实首穿 | 冻结合同是否被真实生产形态数据端到端穿透过 | 未穿透时首批只派真实首穿票，其余依赖票等它 readback |
| 规模档 | Destination 声明的最大规模（全量数据、并发、容量上限）由哪张票演练 | 找到承载票，或写入 Not yet specified |

## AI 估时档位

估时口径是 AI 编程时间，不是人类工时：主导项是上下文张开面与验证反馈距离，不是
代码行数。发布、补估或新建修补票时逐票打分，五因子各 0–2 分：

| 因子 | 0 分 | 1 分 | 2 分 |
| --- | --- | --- | --- |
| 上下文张开面 | 动手前要读懂 ≤3 个文件 | 4–8 个文件 | >8 个文件或跨仓库 |
| 改动面 | 新建/修改 ≤3 个文件 | 4–8 个文件 | >8 个文件 |
| 合同新旧 | 纯内部改动 | 修改现有合同 | 新合同 + 首个消费者 |
| 验证距离 | 现成测试直接跑 | 需新写测试 | 需人工验证/端到端环境/HITL |
| 票面留白 | 票面全定死 | 1–2 个小的现场判断 | 有架构级现场判断 |

总分映射档位：0–2 = S（≤15min）、3–4 = M（≤45min）、5–6 = L（≤90min）、7+ = XL。

- XL 必拆：沿合同缝隙切成可独立验证的票，直到无 XL；XL 票不得发布。
- L 需豁免：票面写一行原子性不拆理由（如迁移不可分、合同与首个消费者必须同票
  验证）；写不出就拆。
- 档位写进 ticket body 固定字段：
  `估时：M(4) | 张开面1 改动面1 合同1 验证0 留白1`；L 豁免追加 `不拆理由：<一行>`。
- 覆盖全部路线：tickets 门禁发布前逐票首估；`direct-implementation-dispatch` 的存量票
  在 dispatch 冻结前补估；执行期修补票建票即估。无档位的票不进入 execution queue。

### 超估熔断

lane packet 携带当前票的档位上限。lane 在每个 checkpoint 自检已耗墙钟：超过 2× 档位
上限且离完成还远时，按「隐藏前置升级」出口停止本 lane，在 terminal report 建议拆分
方案；结局记为 `超估熔断`。

### 校准语料

目标仓库 `docs/wayfinder/estimate-log.csv` 是估时校准真相源，随集成 commit。coordinator
在 `collect` 门禁按 lane final report 逐票追加一行（文件不存在先写表头）：

`日期,map,ticket,档位,因子分,预估上限分钟,实际分钟,执行通道,结局,不拆理由`

实际分钟取该票从 lane 领取到 checkpoint 的墙钟。结局枚举：`done`、`blocked`、
`超估熔断`、`漂移拆票`。发现档位系统性失准（如 M 常跑到 90min）时按精益思路调整
因子映射，并在本节留一行调整依据。

## 执行期漂移控制

### 修补票挂图

执行期新建的、服务于本图 Destination 的任何票（修复、前置、追加），创建时带
map child label，body 首行写 map 坐标。每个 lane terminal 后由 coordinator 重索引 map 并
重算 ready frontier。closed 票给 Decisions-so-far 追加一行，已知
未成票缺口写进 Not yet specified。map 写「（无）」而 tracker 有 open in-scope 票即为
脱图，先归位再执行下一张。

### 合同重冻结

用户决策或实现证据推翻已冻结合同时：

1. 在被推翻的真相源（spec issue、prototype resolution）追加 supersede note，
   写明作废结论与新真相源坐标。
2. 清扫依赖被推翻结论的票：open 票改写或关闭重开；已集成的 closed 票产物列入
   重冻结票的修复范围。
3. 重冻结票作为全部受影响票的 Blocked by 前置，先行派发。

### 隐藏前置升级

lane 发现票面外活跃消费者、被推翻合同或超出票面安全边界的爆炸半径时，只停止本 lane，
在 terminal report 建议独立 tracer bullet 票与 Blocked by。coordinator 落票后立即重算
frontier；不受该 blocker 支配的 lanes 继续。
