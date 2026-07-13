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

## 执行期漂移控制

### 修补票挂图

执行期新建的、服务于本图 Destination 的任何票（修复、前置、追加），创建时带
map child label，body 首行写 map 坐标。`collect` 门禁每次检查时重索引 map：
closed 票给 Decisions-so-far 追加一行，已知未成票缺口写进 Not yet specified。
map 写「（无）」而 tracker 有 open in-scope 票即为脱图，先归位再派发下一批。

### 合同重冻结

用户决策或实现证据推翻已冻结合同时：

1. 在被推翻的真相源（spec issue、prototype resolution）追加 supersede note，
   写明作废结论与新真相源坐标。
2. 清扫依赖被推翻结论的票：open 票改写或关闭重开；已集成的 closed 票产物列入
   重冻结票的修复范围。
3. 重冻结票作为全部受影响票的 Blocked by 前置，先行派发。

### 隐藏前置升级

implementation worker 发现票面外活跃消费者、被推翻合同或超出单个 worker pane
安全边界的爆炸半径时：worker 停止并在 final report 给出新前置票建议；lead 把
发现切成独立 tracer bullet 票并建立 Blocked by，原票保持原范围。
