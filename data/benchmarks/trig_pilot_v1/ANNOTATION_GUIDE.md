# Trig Pilot v1 独立 Gold 标注与冻结规范

## 1. 当前冻结边界

`test_selection.jsonl` 中的 50 条题目已经锁定：五类各 10 条，每类 5 道选择题和 5 道开放题。不得根据当前求解器的正确或错误表现替换题目。`EQUATION` 的 10 条题均要求全部实数解，不得改成限制区间内求解。

当前只冻结了题目选择和 Gold schema，尚未冻结测试 Gold。`manifest.json` 必须保持 `frozen=false`，直到两位人工标注者完成独立标注与裁决。

## 2. 两位标注者的独立工作

标注者 A、B 分别复制 `test_annotation_template.jsonl`，在不查看对方结果的情况下逐题完成：

1. 独立解题，判断题目是否确属给定 `task_family`；困难但在研究范围内的题不得因难度被删除。
2. 填写完整 `oracle_urm`，只编码题面显式信息与求解目标，不写入来源答案或求解器输出。
3. 填写结构化 `gold_answer`，禁止使用展示字符串作为 Gold。
4. 对选择题先独立求出数学 Gold，再匹配选项并填写 `gold_option`；开放题的 `gold_option` 必须为 `null`。
5. 填写本人姓名或稳定标识、`annotation_status=completed` 和必要说明。

原始 CMM-Math 的 `answer`、`analysis` 只能在两位标注者都提交后用于裁决核验，不能代替独立解题。

推荐通过仓库根目录的 `annotation_app/` 完成上述步骤。A、B 必须使用不同的 `--annotator`，并分别启动自己的本地会话；页面只负责字段引导、AST 生成和结构校验，不负责判断答案在数学上是否正确。具体命令及保存位置见 `annotation_app/README.md`。

## 3. Gold schema v0.2

每条 `gold_answer` 必须且只能属于以下一种：

- `expression`：标量或表达式，保存为受限 `ExprAST`。允许有理数、符号、`pi`、四则运算、幂、绝对值、`sin/cos/tan`、`asin/acos/atan` 和关系节点。
- `set`：非周期普通实数集合，保存为 `SetSpec`，支持空集、实数集、有限集、区间、并集和差集。
- `periodic_set`：无限周期点集或区间集，保存为 `PeriodicSet`。

选择题必须同时保存独立数学 `gold_answer` 与 `gold_option`。评分先比较数学 Gold，再在完整实验中检查选项字母；数学等价但书写不同不得判错。

## 4. 周期集合的规范化

标注 `PeriodicSet` 时遵循以下规则：

1. 优先取最小正周期 `period`；若使用非最小但等价周期，必须在说明中注明。
2. 基本区间固定理解为半开区间 `[0, period)`。
3. 离散解写入 `points`，化到基本区间内、去重并按数值顺序排列。
4. 连续解写入 `intervals`，明确 `left_open` 和 `right_open`；跨越周期端点的区间拆成两段。
5. “全部实数但排除周期奇点”使用 `full_period=true` 与 `excluded_points`，不要写成长字符串。
6. 反三角函数采用 SymPy 主值：`asin∈[-pi/2,pi/2]`、`acos∈[0,pi]`、`atan∈(-pi/2,pi/2)`。
7. 必须检查端点、奇点和原方程定义域；由变形引入的增根必须删除。

## 5. 分歧裁决

汇总 A、B 两份结果后，逐字段比较：题型、目标、约束、数学 Gold、周期、基本单元、排除点和选择题选项。数学等价但表示不同的情况应先用结构化等价器核验，再统一为规范表示；不能仅比较 JSON 字符串。

若任一标注者认为题目越界、歧义或原数据有误，必须记录具体证据。只有确实不满足既定研究范围或无唯一可判定数学答案时才能重新打开题目选择；“当前求解器不会做”不是更换理由。

裁决完成后填写 `independent_reviewer`、`adjudication_status=resolved`，并将记录级复核状态设为 `double_verified`。

## 6. 最终冻结门禁

最终冻结前必须同时满足：

- 50 条记录全部包含可校验的 `oracle_urm` 和 `gold_answer`；
- 每类仍为 10 条，且选择/开放仍为 5/5；
- `EQUATION` 10 条的 `GoalSpec.completeness` 全部为 `all_real`，Gold 全部为 `periodic_set`；
- 25 条 dev 与 50 条 test 使用同一 Gold schema v0.2；
- 选择题同时有数学 Gold 和唯一 `gold_option`；
- 两位标注者与裁决状态完整；
- dev/test 不存在同源父题、规范化题干重复或公式模板泄漏；
- 生成最终 `test.jsonl` 后写入 `test_sha256`，最后才把 `manifest.json` 的 `frozen` 改为 `true`。

冻结前运行：

```bash
.venv/bin/python scripts/build_trig_pilot_benchmark.py
.venv/bin/python -m pytest -q
.venv/bin/python -m trig_solver.experiments.run --split test --mode both --freeze-check
```

第三条命令在 Gold 尚未双人复核或哈希不匹配时必须失败；这属于正确的保护行为。
