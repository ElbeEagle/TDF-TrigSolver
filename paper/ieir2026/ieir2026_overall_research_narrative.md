# IEIR 2026 Overall Research Narrative

## 1. Paper Identity

本文是一篇面向智能教育中数学问题求解的算法系统论文。研究对象是直接三角函数题求解，核心问题是如何将三角函数特有的角状态、恒等变换、区间约束和周期结构统一表示，并通过结构化、可验证的符号推理得到标量、区间集合或完整周期解集。以下叙事假定 Trig-URM、TMM-guided DIS、Raw/Oracle 两条求解轨道、全部基线、消融、冻结测试和错误分析均已完整实现，不受当前项目进度限制。

### Working Title

> **Trigonometric Function Problem Solving Based on Periodicity-Aware Symbolic Reasoning**

该标题沿用当前拟定方向，并将不自然的 `Trigonometric Function Problems Solving` 规范为 `Trigonometric Function Problem Solving`。如果后续希望在标题中进一步显式呈现两项方法贡献，可考虑：

> **TrigSolver: Periodicity-Aware Uniform Representation and Meta-Model-Guided Decoupled Inference for Trigonometric Function Problem Solving**

在本母版中，前者作为 working title，后者作为 method-explicit alternative；两者对应同一论文主张，不形成两套叙事。

### Method

整体方法统一命名为：

> **TrigSolver: Periodicity-Aware Symbolic Reasoning with Trig-URM and TMM-Guided DIS**

其中：

- **Trig-URM** 是周期性感知的三角函数统一表征模型；
- **TMMs** 是封装三角函数特定前置条件、运算和状态转换的 Trigonometric Meta-Models；
- **DIS** 是在程序推理层组织、选择和验证 TMM 状态转换的 Decoupled Inference Strategy；
- LLM 语义映射和 CAS 执行器是支持组件，不是论文的核心贡献。

方法总定义为：

> **TrigSolver maps a trigonometric problem into a periodicity-aware Trig-URM and applies TMM-guided decoupled inference to coordinate exact symbolic transformation, interval-constrained solving, periodic completion, and answer validation.**

### Core Claim

> **We introduce TrigSolver, which represents trigonometric function problems using a periodicity-aware Trigonometric Uniform Representation Model (Trig-URM) and performs Trigonometric Meta-Model (TMM)-guided decoupled inference, enabling unified symbolic reasoning for trigonometric identity transformation, interval-constrained solving, and complete periodic solution-set construction.**

### One-Sentence Thesis

> **Reliable trigonometric problem solving requires periodicity to be represented and reasoned over as a first-class structure; TrigSolver makes this structure explicit in Trig-URM and operational through TMM-guided decoupled symbolic inference.**

### Keywords

- Trigonometric function problem solving
- Periodicity-aware representation
- Trigonometric function representation
- Trigonometric meta-model
- Decoupled inference strategy
- Symbolic reasoning
- Trigonometric identity transformation
- Periodic solution sets

如果投稿模板限制关键词数量，优先保留：`Trigonometric function problem solving; trigonometric function representation; decoupled inference strategy; symbolic reasoning; periodic solution sets`。

## 2. Core Paper Story

现有通用数学求解方法通常将三角函数题视为普通表达式求值、方程求解或语言推理任务。这种处理忽略了三角函数题的结构特殊性：角度与弧度制影响表达式语义；象限和主值区间决定符号与分支；恒等变换必须保持定义域和等价条件；区间问题要求严格处理端点、并集和排除点；三角方程与不等式的最终答案通常不是单个值，而是由基本周期内解集提升得到的无限周期集合。

纯 LLM 推理可以生成看似合理的步骤，但容易遗漏分支、混淆主值与全体解或输出不可验证的等价变换。通用 CAS 可以执行局部化简和求解，但其返回结果未必满足题目要求的角状态、区间约束和周期完备性。仅将 LLM 与 CAS 串联，仍然缺少一个显式中间状态来表示问题，也缺少一个面向三角函数结构的推理控制层来决定何时变换、何时求解、如何补全周期以及如何验证答案。

本文据此提出两项相互依赖的方法设计。第一，Trig-URM 将函数对象、角状态、表达式、约束、目标和推理所得事实组织为统一状态，使周期、定义域和答案完整性成为一等信息。第二，TMM-guided DIS 将程序推理与三角函数特定运算解耦：DIS 负责根据当前 Trig-URM 状态和求解目标组织推理路径，TMMs 负责执行恒等变换、区间求解、基本周期求解、周期提升和精确验证。

论文的主因果链固定为：

```text
Trigonometric problems contain angle, domain, branch, and periodic structures
    -> flat expressions and direct generation do not preserve these structures
    -> Trig-URM represents them explicitly
    -> TMM-guided DIS selects and executes structure-compatible operations
    -> identity, interval, and periodic-set reasoning become unified and verifiable
    -> Raw/Oracle comparisons and component ablations isolate why the method works
```

## 3. Task Formulation and Scope

### 3.1 Input and Output

给定文本三角函数题：

```text
x = (t, O)
```

其中 `t` 是题干，`O` 是可选的答案选项。Raw track 直接读取原题，Oracle track 读取人工校正的 Trig-URM。两条轨道共享相同的 TMM library、DIS、符号执行器、周期补全器和验证器。

系统输出：

```text
y = (a, S, H, z)
```

其中 `a` 是最终标量、性质值或选项，`S` 是普通集合或周期集合，`H` 是经过验证的 TMM 推理轨迹，`z` 是 `solved` 或带稳定原因的 `abstained` 状态。选择题必须先生成数学答案，再进行选项等价匹配，不允许直接预测选项字母。

### 3.2 Supported Problem Families

| Family | Main operation | Representative output contract |
| --- | --- | --- |
| `EVAL` | 特殊角、诱导公式、象限和精确求值 | scalar expression |
| `IDENTITY` | 恒等证明、化简和等价变换 | equivalent expression / proof status |
| `SINUSOID_PROPERTY` | 周期、振幅、相位、单调性、对称性、最值和值域 | scalar / interval set / periodic set |
| `EQUATION` | 基础三角方程及完整实数解 | complete periodic solution set |
| `DOMAIN_RANGE_INEQUALITY` | 定义域、值域和基础三角不等式 | ordinary or periodic interval set |

### 3.3 Research Boundary

本文研究直接三角函数题，而不是仅在几何题中使用正弦定理、余弦定理或三角比的题目。主要范围是文本、单目标和可结构化验证的问题，不将图像解析、多子题混合推理、任意超越方程、参数化根计数、形式定理证明或教学效果评价纳入核心 claim。教育意义限定为为智能数学求解、错误诊断和可解释反馈提供结构化基础，不声称已经证明学生学习效果。

## 4. Periodicity-Aware Trig-URM

### 4.1 Formal Definition

Trig-URM 形式化为六元组：

$$
\mathcal{U}_{\mathrm{trig}}=\langle F,A,E,C,G,D\rangle .
$$

| Component | Name | Responsibility |
| --- | --- | --- |
| $F$ | Function objects | 函数族、变量映射、规范形式、参数及周期属性 |
| $A$ | Angles | 角变量、角制、变量域、象限、主值区间和模周期关系 |
| $E$ | Expressions | 可执行表达式、方程/不等式、AST、引用及表达式依赖 |
| $C$ | Constraints | 题面显式条件、定义域、区间、有效性和奇点约束 |
| $G$ | Goal | 任务族、目标运算、目标引用和答案完整性契约 |
| $D$ | Derived facts | 规范化结果、恒等变换、基本周期解、区间单元和验证事实 |

$F,A,E,C$ 描述已理解的题目状态，$G$ 定义求解目标和输出契约，$D$ 在 TMM 推理过程中单调积累可验证的派生事实。原先独立的 output contract 被并入 $G$，因此六元组中的最后一项固定为 `derived_facts`，不再使用 $O$。

### 4.2 Why the Representation Is Periodicity-Aware

Trig-URM 不将周期性视为答案字符串中的附加说明，而是显式表示基本周期、基本周期内的点/区间单元、定义域和排除点。完整周期解集统一写为：

$$
\mathcal{S}=\left(\bigcup_{k\in\mathbb{Z}}(\mathcal{S}_0+kT)\right)\cap\Omega\setminus\mathcal{X},
$$

其中 $\mathcal{S}_0$ 是一个基本周期内的解集，$T$ 是最小正周期，$\Omega$ 是变量定义域，$\mathcal{X}$ 是奇点、无定义点或变换产生的排除点。点解、区间解、开闭端点、跨周期区间和“全周期减排除点”均由统一的 `PeriodicSet` 结构表达。

### 4.3 Representation-Level Claim

Trig-URM 的贡献不只是为旧 URM 增加三角函数类型字段，而是把三角问题中决定推理正确性的角状态、表达式关系、区间约束、周期结构和答案完备性组织为可执行状态。它同时承担三项作用：为上游语义映射提供目标 schema，为 TMM 提供前置条件匹配接口，为最终验证提供结构化答案语义。

## 5. TrigSolver: TMM-Guided Decoupled Symbolic Inference

### 5.1 Overall Pipeline

```text
Problem text and options
    -> Formula preprocessing and grounded semantic mapping
    -> Trig-URM instantiation <F,A,E,C,G,D>
    -> TMM candidate matching and DIS route construction
    -> Controlled symbolic execution
    -> Interval and periodic completion
    -> Exact validation and option matching
    -> Verified answer and trace, or explicit abstention
```

确定性预处理器负责规范化公式、角度符号和变量表面形式，并建立表达式引用。语义映射器只把题面显式语义映射到 Trig-URM，不执行数学求解、不决定答案形式，也不补充隐藏的定义域或周期结论。核心数学决策从 Trig-URM 开始，由 TMM-guided DIS 完成。

### 5.2 Trigonometric Meta-Models

每个 TMM 是一个可检查的三角函数知识单元：

$$
M_i=\langle id_i,P_i,O_i,U_i,V_i\rangle,
$$

其中 $P_i$ 是对 Trig-URM 的结构前置条件，$O_i$ 是具体符号运算，$U_i$ 是对 $D$ 或其他状态分量的更新，$V_i$ 是该转换的局部验证条件。

核心 TMM inventory 包括：

| TMM | Main role |
| --- | --- |
| `TMM-AngleNormalize` | 统一角制、主值区间、象限和模周期关系 |
| `TMM-ExactEvaluate` | 特殊角、诱导公式和约束驱动的精确求值 |
| `TMM-IdentityTransform` | 有界恒等规则搜索、规范化和等价性保持 |
| `TMM-SinusoidCanonicalize` | 归约到 $A\sin(\omega x+\varphi)+b$ 或余弦规范形式 |
| `TMM-PropertyDerive` | 推导周期、振幅、相位、单调区间、对称性和最值 |
| `TMM-EquationBaseSolve` | 生成一个基本周期内的全部方程分支 |
| `TMM-IntervalSolve` | 处理定义域、区间约束、端点和不等式单元 |
| `TMM-PeriodicComplete` | 将基本周期结果提升为完整实数解集 |
| `TMM-AnswerValidate` | 检查符号等价、集合等价、周期完备性和选项匹配 |

### 5.3 Decoupled Inference Strategy

DIS 将“如何组织推理”与“某一步具体怎样计算”解耦。程序推理层读取 $G$ 和当前状态签名，根据任务族、表达式形态、现有约束和缺失的目标事实构造 TMM 路径；元模型层只在 $P_i$ 满足时执行 $O_i$，将通过 $V_i$ 的结果写入 $D$。推理持续到 $G$ 的输出契约被满足，或在没有可用路径、执行超时、结果不可验证时显式 abstain。

因此，TMM 不是按题型写死的完整 solver，DIS 也不是无约束调用 CAS。二者共同形成一个状态驱动的控制过程：

```text
Inspect current Trig-URM state
    -> retrieve TMMs compatible with goal and structure
    -> check structural and mathematical prerequisites
    -> execute one symbolic transition
    -> validate and update derived facts
    -> stop on a satisfied answer contract or abstain on unresolved state
```

### 5.4 Three Flagship Reasoning Capabilities

#### Trigonometric Identity Transformation

TrigSolver 在表达式图上应用带适用条件的恒等变换，并通过符号等价与定义域检查保证转换前后语义一致。目标不仅是生成更短表达式，也包括将输入变换为适合后续方程、不等式或正弦型性质推理的规范形式。

#### Interval-Constrained Solving

区间求解显式维护变量域、基本周期、端点开闭和排除点。方程或不等式的候选结果必须与 $C$ 中的定义域及区间约束求交，不能把无约束 CAS 结果直接当作最终答案。

#### Complete Periodic Solution-Set Construction

周期解集推理采用“基本周期求解—分支规范化—周期提升—定义域与奇点过滤—完备性验证”的过程。最终输出是具有集合语义的 `PeriodicSet`，而不是自然语言中的 `+2k\pi` 字符串。

## 6. Contributions and Experimental Evidence

### 6.1 Contributions

论文贡献固定为三点：

1. **We propose Trig-URM**, a periodicity-aware uniform representation that organizes function objects, angle states, executable expressions, constraints, solving goals, and derived facts for five families of trigonometric function problems.
2. **We develop TMM-guided DIS**, which decouples procedural control from trigonometric meta-model execution and unifies identity transformation, interval-constrained solving, periodic completion, and exact validation in one symbolic reasoning process.
3. **We establish a factorized Raw/Oracle evaluation protocol** that measures end-to-end accuracy, representation quality, solver capability, periodic completeness, selective reliability, and the causal contribution of Trig-URM, TMM routing, periodic completion, and validation.

### 6.2 Research Questions

| Research question | Main evidence |
| --- | --- |
| RQ1: Trig-URM 能否统一表示五类三角函数题及不同答案契约？ | field-level URM accuracy、schema coverage、unsupported/ambiguous rate |
| RQ2: TrigSolver 是否优于直接 LLM、CAS 和简单 LLM+CAS 流水线？ | Raw-track 和 Oracle-track overall/per-family accuracy |
| RQ3: TMM-guided DIS 是否真正贡献了求解能力？ | generic-CAS、flat-state、no-routing 及 TMM component ablations |
| RQ4: 周期性感知设计是否提高完整周期解集的正确性？ | periodic completeness、branch recall、domain/singularity error |
| RQ5: 系统在哪些复杂结构上成功或失败？ | identity、interval、periodic-set 分组结果和代表性 traces |

### 6.3 Evaluation Tracks and Baselines

Raw track 衡量从文本到最终答案的端到端能力，比较：

- Direct LLM reasoning;
- schema-constrained LLM + generic CAS;
- full TrigSolver-Raw.

Oracle track 隔离表示之后的纯求解能力，比较：

- CAS-only;
- flat expression state + generic routing;
- Trig-URM without TMM-guided DIS;
- full TrigSolver-Oracle.

Raw 与 Oracle 使用相同冻结数据、答案协议和下游模块。两者差值用于区分 semantic mapping error 与 symbolic reasoning error，而不是把 Oracle 结果作为端到端性能。

### 6.4 Core Metrics

- Problem-level accuracy，abstention 计错；
- Accuracy by task family and answer format；
- Coverage and conditional accuracy；
- Trig-URM field accuracy and goal-reference accuracy；
- Identity transformation validity；
- Interval-set equivalence；
- Periodic completeness and branch recall；
- False acceptance / validation failure rate；
- Latency and token/CAS cost，作为次级效率指标。

### 6.5 Core Ablations

| Ablation | Claim tested | Expected diagnostic effect |
| --- | --- | --- |
| Flat representation replacing Trig-URM | 周期性感知状态是否必要 | 角状态、区间和答案契约错误增加 |
| Generic CAS without TMMs | 三角特定知识单元是否必要 | 恒等变换和性质推理下降 |
| No DIS routing | 程序推理与元模型解耦是否必要 | 无效操作、无路径和推理冲突增加 |
| No periodic completion | 周期提升是否必要 | 基本周期结果正确但全体实数解不完整 |
| No exact validator | 验证是否必要 | 错误选项匹配、增根和 false acceptance 增加 |
| Raw versus Oracle | 上游语义映射影响 | 分离 parsing 与 solving bottleneck |

### 6.6 Claim-Evidence Map

| Major claim | Decisive evidence |
| --- | --- |
| Trig-URM provides a unified periodicity-aware state | 五类覆盖、field accuracy、flat-representation ablation |
| TMM-guided DIS improves structured symbolic solving | 与 CAS/LLM+CAS 比较、no-TMM/no-DIS ablation、verified traces |
| Identity, interval, and periodic-set operations are unified | 三类能力分组结果、跨任务共享状态与 TMM 路径 |
| Periodic answers are complete rather than locally plausible | periodic completeness、branch recall、singularity/domain analysis |
| The system is selectively reliable | coverage、conditional accuracy、false acceptance 和 abstention breakdown |

## 7. Main Figures, Algorithm, and Tables

核心配置固定为“两张图 + 一个算法伪代码”。Figure 1 回答系统是什么以及核心贡献位于哪里，Figure 2 回答三类复杂运算如何在一个案例中连续发生，Algorithm 1 回答 TMM-guided DIS 如何执行、验证或 abstain。三者分别承担 overview、worked mechanism 和 executable control flow，不重复呈现同一信息。

### Figure 1: Periodicity-Aware TrigSolver Pipeline

Figure 1 在 Introduction 末尾首次引用，图本体放在 Method Overview。它展示 Raw question 如何经过 formula preprocessing 和 grounded semantic mapping 形成六元组 Trig-URM，随后由 TMM-guided DIS 调度 identity、property、equation、interval 和 periodic TMMs，调用受控符号执行器，并经过 periodic completion 和 exact validation 输出答案或 explicit abstention。

```text
Problem text and options
        |
        v
Formula preprocessing + grounded semantic mapping
        |
        v
Trig-URM <F,A,E,C,G,D>
        |
        v
TMM-guided DIS
  +-----+---------+----------+------------+
  | Identity TMM | Interval | Equation   | Property TMM
  +-----+---------+----------+------------+
        |
        v
Controlled symbolic execution
        |
        v
Periodic completion + exact validation
        |
   +----+----+
   |         |
Solved    Abstained
answer    with reason
```

图中应以不同视觉层明确区分：LLM semantic mapping、核心 Trig-URM/TMM-DIS、CAS executor 和 validator，避免读者把 Qwen 或 SymPy 误解为论文方法主体。

### Figure 2: From Identity Transformation to a Complete Periodic Set

Figure 2 放在三类 flagship capability 之后，采用一个能够同时体现恒等变换、区间求解和周期提升的代表题：

$$
\sin x+\cos x>1.
$$

推理链为：

```text
Original inequality
sin(x) + cos(x) > 1
        |
        | TMM-IdentityTransform
        v
sqrt(2) sin(x + pi/4) > 1
        |
        | TMM-IntervalSolve on one period
        v
S0 = (0, pi/2)
        |
        | TMM-PeriodicComplete
        v
S = union over k in Z of (2k*pi, pi/2 + 2k*pi)
        |
        | TMM-AnswerValidate
        v
verified complete periodic solution set
```

图中左侧展示 $A,E,C,G$ 的初始状态，中间展示每个 TMM 的前置条件和转换，右侧展示写入 $D$ 的事实以及最终 `PeriodicSet`。同一颜色贯穿原表达式节点、变换结果、基本区间和周期单元，使读者看到三类复杂运算共享同一个 Trig-URM 状态，而不是三个独立 solver 的拼接。

### Algorithm 1: TMM-Guided DIS for Trigonometric Symbolic Reasoning

Algorithm 1 放在 Method 末尾。输入为 Raw/Oracle problem、TMM library、最大状态转换数和 CAS policy；输出为结构化答案、verified trace 和 status。高层控制流固定为：

1. Preprocess formulas and instantiate Trig-URM;
2. Inspect the current state and goal contract;
3. Retrieve TMMs whose structural prerequisites are satisfied;
4. Select the next TMM under the DIS route policy;
5. Execute the symbolic operation with bounded CAS support;
6. Validate the transition and update $D$;
7. Apply interval/domain filtering and periodic completion when required;
8. Return the verified answer when $G$ is satisfied;
9. Otherwise return explicit abstention for no route, timeout, unsupported structure, periodic failure, or validation failure.

正文只保留一个编号算法。具体恒等式规则和 handler 细节放在文字说明、附录或代码中，不拆成第二个主算法。

### Tables

| Table | Content |
| --- | --- |
| Table 1 | 五类任务、输入结构、主要 TMM 和答案契约 |
| Table 2 | Raw/Oracle 主结果以及 LLM、LLM+CAS、CAS-only 比较 |
| Table 3 | Trig-URM、TMM/DIS、periodic completion 和 validator 消融 |

分题型结果可以并入 Table 2 的 grouped columns；错误类型和复杂运算细分优先放在 Table 3 或紧凑正文中，避免为小型会议论文堆叠过多表格。

## 8. Paper Structure

论文以 IEEE 双栏 6--8 页为目标，正文建议控制在约 3,200--3,800 个英文词。

| Section | Main responsibility | Suggested length |
| --- | --- | --- |
| Introduction | 从周期性结构缺失引出 Trig-URM、TMM-guided DIS 和三项贡献 | 0.9--1.1 pages |
| Related Work | 三角专用求解、LLM 数学推理、CAS/neuro-symbolic 和 TDF/URM-DIS | 0.5--0.7 page |
| Task Formulation and Trig-URM | 五类任务、Raw/Oracle、六元组和 PeriodicSet 语义 | 0.9--1.1 pages |
| TrigSolver Method | pipeline、TMM、DIS、三类 flagship reasoning capability | 1.4--1.8 pages |
| Experiments | setup、main comparison、Raw/Oracle、ablations、failure analysis | 1.8--2.2 pages |
| Analysis and Conclusion | 解释周期性感知机制、适用边界和意义 | 0.5--0.7 page |

### Introduction Argument

Introduction 采用：

```text
intelligent mathematical problem solving
    -> trigonometric problems require periodic and branch-aware reasoning
    -> LLM/CAS/direct pipelines lack explicit structured state and completeness control
    -> Trig-URM + TMM-guided DIS
    -> three contributions and experimental evidence
```

第一段说明三角函数题是智能数学求解中的结构化难题；第二段提出角状态、恒等变换、区间和周期完备性四个技术瓶颈；第三段综合现有专用 solver、LLM 和 CAS 的能力边界；第四段引出 TrigSolver、核心 claim 和三项贡献。

### Related Work Organization

Related Work 按机制而不是按论文年份组织：

1. Trigonometric identity and formal symbolic solving；
2. LLM-based mathematical problem solving；
3. CAS and neuro-symbolic mathematical reasoning；
4. TDF solving, uniform representation, and decoupled inference。

每部分都落到同一缺口：现有方法没有同时把三角函数的周期结构作为统一表示对象，并用元模型引导的解耦推理完成恒等、区间和完整周期集合运算。

### Experiments Argument

Experiments 采用证据阶梯：

```text
benchmark and protocol validity
    -> end-to-end Raw main result
    -> Oracle solver capability
    -> fair baseline comparison
    -> component ablations
    -> identity/interval/periodic-set diagnostics
    -> errors, abstention, and efficiency
```

Results 只报告观察和数据；Analysis 解释为什么周期性感知表示、TMM 前置条件和验证机制产生这些变化，不逐表重复数值。

## 9. Terminology Ledger

| Canonical term | First-use definition | Avoid or qualify |
| --- | --- | --- |
| trigonometric function problem solving | 直接三角函数题求解任务 | `trigonometric function problems solving` |
| TrigSolver | 整体系统与方法 | 同时使用多个系统名 |
| Trigonometric Uniform Representation Model (Trig-URM) | 六元组 $\langle F,A,E,C,G,D\rangle$ | UFR、URM、Trig representation 混用 |
| Trigonometric Meta-Models (TMMs) | 三角函数特定知识单元库 | FMM、rule、handler 随意互换 |
| Decoupled Inference Strategy (DIS) | 程序推理与 TMM 执行解耦 | 只写 generic routing |
| TMM-guided decoupled inference | 方法运行机制 | `decoupled meta-model inference` 与之混用 |
| periodicity-aware symbolic reasoning | 论文总体方法特征 | 仅写 symbolic computation |
| trigonometric identity transformation | 证明、化简及等价变换 | identity solving |
| interval-constrained solving | 定义域或给定区间下的求解 | interval solving |
| complete periodic solution set | 完整分支和整数周期提升后的集合 | one-period result、representative roots |
| controlled symbolic executor | 被 TMM/DIS 调用的 CAS | 把 SymPy 称为整体 solver |
| explicit abstention | 无受支持或可验证路径时的结构化状态 | failure/refusal/rejection 混用 |

## 10. Boundaries and Non-Claims

- 本文声称的是定义范围内五类文本三角函数题的统一表征和符号推理，不声称覆盖完整三角学。
- 本文的核心贡献是 Trig-URM 与 TMM-guided DIS，不把 LLM、prompt 或通用 CAS 包装为算法创新。
- `complete` 只修饰定义任务中的周期解集完整性，不用于声称系统覆盖所有三角函数问题。
- 可验证 trace 支持错误定位和解释，但不等同于已经验证教学有效性或学生学习增益。
- Raw/Oracle 差距用于诊断上游语义映射与下游符号推理，不将 Oracle performance 当作端到端结果。
- 数值采样可以用于拒绝错误候选，但不能单独接受符号答案或证明恒等性。

## 11. Relationship to the Scenario-to-Function Paper

两篇 IEIR2026 论文属于同一条“structured and verifiable mathematical reasoning”研究主线，但任务边界互补且不重叠：

| Paper | Starts from | Ends at | Core method |
| --- | --- | --- | --- |
| Scenario-to-function paper | 情景文本和可观察图示事实 | 实例化函数模型或 abstention | MLC-RPM |
| TrigSolver paper | 三角函数题及其显式数学语义 | 经过验证的最终答案或完整解集 | Trig-URM + TMM-guided DIS |

Scenario-to-function 论文把隐含函数模型发现变成独立中间任务，不执行最终求解；TrigSolver 论文研究特殊函数知识已经进入结构化状态后，如何表示和执行周期性感知的数学推理。前者的关键词是 `model discovery, evidence grounding, relation-pattern matching`，后者的关键词是 `periodicity, symbolic transformation, interval constraints, periodic solution sets`。两篇论文可以共享 TDF 的总体研究背景，但不能复用同一任务定义、方法 claim 或实验结论。

## 12. Final Narrative Anchor

> **Trigonometric problems cannot be solved reliably by treating periodicity as an afterthought attached to a locally computed answer. We therefore introduce Trig-URM, a periodicity-aware representation of function objects, angle states, expressions, constraints, goals, and derived facts, and TMM-guided DIS, which coordinates trigonometric meta-models for identity transformation, interval-constrained solving, and periodic completion. Through Raw and Oracle evaluation, baseline comparisons, component ablations, periodic-completeness analysis, and verified reasoning traces, TrigSolver demonstrates that making periodic structure explicit enables unified and reliable symbolic reasoning across diverse trigonometric function problems.**

后续摘要、Introduction、Method、Experiments、Figure 1、Figure 2 和 Algorithm 1 都必须直接服务这条因果链。任何不能解释“为什么需要周期性感知表示”“TMM 与 DIS 如何产生可验证推理”“三类复杂运算如何被统一”或“实验如何隔离这些贡献”的内容，都不应占据论文主线。
