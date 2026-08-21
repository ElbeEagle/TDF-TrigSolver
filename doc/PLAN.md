# TrigSolver 中文文本三角函数 Pilot 开发方案

## 1. 目标与验收标准

构建一套可运行的：

`Formula Preprocessor → Qwen Parser → Trig-URM → TMM/DIS → CAS → Periodic Completion → Validator`

会议版严格支持五类单目标题：

- `EVAL`：特殊角、诱导公式、象限符号与表达式求值。
- `IDENTITY`：标准恒等式化简与等价变换。
- `SINUSOID_PROPERTY`：可化为 \(A\sin(\omega x+\varphi)+b\) 或余弦形式的周期、振幅、相位、单调区间、对称性、最值和值域。
- `EQUATION`：单个仿射角参数下的基础正弦、余弦、正切方程及简单同元二次式。
- `DOMAIN_RANGE_INEQUALITY`：标准定义域、正弦型值域和单变量基础三角不等式。

验收门槛：

- 现有测试继续保持通过。
- 开发集 Oracle ≥ 84%（21/25），Raw ≥ 60%（15/25）后才运行冻结测试集。
- 冻结测试集端到端 Raw accuracy 目标 ≥ 60%（30/50），abstention 计错。
- 所有输出必须经过验证器；无法验证、超时或超出白名单时明确 abstain。

## 2. 核心接口与表示

在 `src/trig_solver/` 建立 Python 包，并通过 `pyproject.toml` 固定 SymPy、Pydantic、OpenAI SDK、python-dotenv 和 Lark 依赖。

公开接口：

```python
solve_raw(problem: RawProblem, config: SolverConfig) -> SolveResult
solve_oracle(urm: TrigURM, options: list[str] | None) -> SolveResult
```

核心类型：

- `TrigURM`：包含 `angles`、`expressions`、`constraints`、`goal`、`derived_facts`。
- `AngleState`：符号、角制、定义域、象限、主值区间和模周期关系；内部统一转为弧度。
- `ExprAST`：只允许有理数、符号、\(\pi\)、四则运算、幂、绝对值及 `sin/cos/tan`，通过白名单递归构造 SymPy 对象，不接受任意 Python 表达式。
- `GoalSpec`：任务族、操作、目标表达式引用、性质名及题面明确要求的完整性。
- `PeriodicSet`：基本周期、基本区间、点/区间单元、端点开闭和排除点，语义为各单元平移 \(kT,\ k\in\mathbb Z\) 后的并集。
- `TraceStep`：TMM、前置条件、操作、输入/输出状态摘要和验证结果。
- `AbstainCode`：公式解析、语义映射、grounding、无可用路径、CAS 超时、周期补全失败、验证失败、题型越界等稳定枚举。

Qwen 仅输出任务族、目标引用、变量和题面显式约束，不输出答案、推导或答案形式。`periodic_set` 等输出契约由 TMM Router 确定。

## 3. 实现方案

### 输入与解析

- 规范化 Unicode、LaTeX、角度符号、全角标点和选项格式，为公式分配 `E1...En`。
- 使用固定 `qwen3.7-flash-2026-07-15`、`temperature=0.01`、`enable_thinking=false` 和 JSON 输出；schema 失败时只重试一次。
- Qwen 请求只包含题干、选项和公式引用表，绝不读取 `answer`、`analysis`、`solution`。
- LaTeX 解析使用受适配器隔离的 Lark 后端；解析异常、歧义、未知命令或 AST 超过 256 节点即 abstain。Lark 对不完整表达式采用严格失败，但 SymPy 官方仍将 LaTeX parser 标为实验能力，因此必须配套固定版本和回归样例。[SymPy parsing](https://docs.sympy.org/latest/modules/parsing.html)

### TMM 与 DIS

每个 TMM 统一实现 `match(state) → bool` 和 `execute(state) → transition`：

- `TMM-AngleNormalize`：角制转换、周期归约、奇偶性、象限符号。
- `TMM-ExactEvaluate`：特殊角及已知三角值求值。
- `TMM-IdentityRewrite`：诱导公式、平方关系、和差角、倍角、降幂、积和变换；采用深度 4、beam 12 的有界搜索。
- `TMM-SinusoidCanonicalize`：识别单一谐波并提取 \(A,\omega,\varphi,b\)。
- `TMM-PropertyDerive`：生成周期、相位、单调区间、对称点/轴、最值和值域。
- `TMM-EquationBaseSolve`：在一个基本周期内求基础分支。
- `TMM-DomainRangeInequality`：生成定义约束、值域或一个周期内的不等式解。
- `TMM-PeriodicComplete`：将基本解提升为完整周期集合并处理排除点。
- `TMM-AnswerValidate`：回代、等价性检查及选择题选项匹配。

DIS 首先按 `(task_family, expression_shape, goal)` 使用预定义路径；没有精确路径时进行最多 8 次状态转换的探索式匹配，仍未满足目标则 abstain。每一步记录状态哈希，禁止重复应用同一 TMM。

SymPy 仅通过受控 CAS executor 调用 `trigsimp`、`expand_trig`、`solveset`、`periodicity`、`continuous_domain` 和单变量不等式接口；每次调用限时 2 秒。`ConditionSet`、未实现异常或不确定的符号等价结果不得冒充答案。官方文档明确指出三角不等式通常只返回一个周期内的结果，因此完整周期提升必须由自定义模块完成。[SymPy inequalities](https://docs.sympy.org/latest/modules/solvers/inequalities.html)、[SymPy solveset](https://docs.sympy.org/latest/modules/solvers/solveset.html)

选择题同样先生成数学答案，再与选项做符号匹配；禁止让 Qwen直接预测选项字母。符号验证不确定时，数值采样只用于拒绝错误候选，不能单独作为接受依据。

## 4. 数据、测试与实验

在 `data/benchmarks/trig_pilot_v1/` 新增派生清单，不修改现有 795 条数据：

- Development：25 题，每类 5 题，固定为 2 道选择题 + 3 道开放题。
- Frozen test：50 题，每类 10 题，固定为 5 道选择题 + 5 道开放题。
- 仅选择无图片、单目标、单主变量、处于白名单且答案可规范化的题。
- 按原题 ID、规范化题干和公式骨架分组，模板近似题不得跨 development/test。
- 开放题重新整理为结构化 `gold_answer`，不直接以原始长篇 `answer` 字符串评分。
- Development 可由一人标注；冻结测试集的 Oracle-URM 与规范化答案由第二人独立复核并记录裁决结果。

测试层次：

- 单元测试：ExprAST、角制转换、恒等规则、正弦型参数、周期点集/区间集、CAS 超时和答案等价。
- 端到端离线测试：每类至少 2 个固定 Qwen JSON fixture，默认测试不访问网络。
- API 集成测试：五类各 1 题，显式启用时才真实调用 Qwen。
- 安全测试：未知 LaTeX、缺失公式引用、多目标、视觉依赖、复杂超越方程必须稳定 abstain。
- 回归测试：现有 16 passed、1 skipped 基线不得退化。

正式实验：

1. Oracle-URM → Full Solver。
2. Raw Question → Qwen → Full Solver。
3. Oracle + CAS-only 基线。
4. Full Solver 去除 periodic completion。
5. Full Solver 去除 validator。

报告 overall accuracy、五类准确率、coverage、conditional accuracy、Oracle/Raw 差距、periodic completeness、平均延迟和 token 用量。最终结果文件记录数据哈希、prompt 哈希、模型快照、Git commit 和逐题失败阶段。

失败类型固定为：

`UNSUPPORTED_INPUT / FORMULA_PARSE / RAW_SCHEMA / GROUNDING / NO_ROUTE / TMM_PRECONDITION / CAS_TIMEOUT / CAS_UNSOLVED / PERIODIC_FAILURE / VALIDATION_NO_MATCH / VALIDATION_AMBIGUOUS / WRONG_ANSWER`。

若 Oracle 未过门槛，只修规则、TMM 和周期层；若 Oracle 通过而 Raw 未过门槛，只用 development 调整 prompt/grounding；冻结测试运行后无论结果如何都不再据此调参。

## 5. 运行命令与交付节奏

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pytest -q
RUN_LLM_INTEGRATION=1 .venv/bin/python -m pytest -q -m integration

.venv/bin/python -m trig_solver.experiments.run --split dev --mode oracle
.venv/bin/python -m trig_solver.experiments.run --split dev --mode raw
.venv/bin/python -m trig_solver.experiments.run --split test --mode both --freeze-check
.venv/bin/python -m trig_solver.experiments.summarize --latest
```

时间安排：

- 8月20–21日：冻结 schema、白名单、25/50 清单及人工标注规范。
- 8月22–24日：实现预处理、Trig-URM、TMM/DIS、CAS 和周期集合。
- 8月25–26日：完成单元测试、Oracle development 和规则修复。
- 8月27日：接入 Raw Parser，完成 Raw development。
- 8月28日：冻结代码、prompt 和测试集，运行一次正式实验。
- 8月29–30日：结果表、失败分析、代表案例和论文撰写。
- 8月31日：复核并提交。

最终交付必须包含：实际运行命令、逐模式结果表、各类失败数量、代表成功/失败轨迹、未达到 60% 时的真实原因，以及后续优先修复建议。

默认不支持图片、多子题、周期情景建模、向量/几何混合题、复杂参数根计数、任意超越方程和教学式自然语言解答；这些输入统一明确 abstain。
