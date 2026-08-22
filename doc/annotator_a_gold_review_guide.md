# TrigSolver 冻结测试集 Annotator A 标注与验收手册

- 版本：v1.0
- 适用对象：具备高中三角函数知识、没有研究或算法背景的人工标注者
- 适用数据：Trig Pilot v1 冻结候选测试集 50 题
- 标注方式：在轻量标注页面中，独立审查并修正机器预填的 Silver

## 1. 你要完成的工作是什么

你的任务不是测试求解器，也不是判断“算法会不会做”。你的任务是为 50 道已经锁定的三角函数题建立一份数学上正确、结构上规范的人工标注。

每道题需要审查两类信息：

1. **Oracle-URM**：把题目“给了什么、要求什么”准确地写成结构化输入。
2. **数学 Gold**：你独立计算得到的正确数学答案，以及选择题对应的选项字母。

页面已经预填一份 `machine_prepared_silver`。Silver 只是提高效率的候选草稿，不是标准答案。你必须自己读题、计算、核对；发现错误时直接修改。

这里的“独立”是指：

- Annotator A 和 Annotator B 不查看彼此的标注结果；
- 不查看求解器预测、运行轨迹或实验结果；
- 不查看原始 CMM-Math 的 `answer`、`analysis` 或 `solution`；
- 先独立得到数学答案，再核对选择题字母；
- 不因为题目困难或当前算法可能不会做而删除、替换或降低题目难度。

> 最重要的原则：按数学事实标注，不按求解器能力标注。

### 1.1 启动 Annotator A 页面

在仓库根目录中启动，不要把标注者 ID 改成 `annotator_b`。

macOS 或 Linux：

```bash
.venv/bin/python -m pip install -e '.[annotation,dev]'
.venv/bin/python annotation_app/run.py --annotator annotator_a --port 8501
```

Windows PowerShell：

```powershell
.venv\Scripts\python.exe -m pip install -e ".[annotation,dev]"
.venv\Scripts\python.exe annotation_app\run.py --annotator annotator_a --port 8501
```

然后在本机浏览器打开 `http://127.0.0.1:8501`。如果安装依赖或启动失败，不要自行修改 seed、模板或 manifest，应把完整错误信息发给负责人。

### 1.2 文件保存与双人隔离

Annotator A 的文件默认只保存在：

```text
annotation_runs/annotator_a/
├── annotations.jsonl    已确认完成的正式记录
├── drafts.json          页面自动保存的草稿
└── events.jsonl         最小操作记录
```

两位标注者可以使用不同电脑和不同操作系统，但必须使用同一版本的仓库、模板和 Silver seed。页面会检查 seed 与模板的哈希。标注未完成前，不要查看、复制或交换 `annotation_runs/annotator_b/` 中的任何内容。

## 2. 先认识三个概念

### 2.1 Silver：机器预填草稿

Silver 是页面启动时显示的默认内容，包括目标公式、约束、Gold 类型和候选答案。它可能完全正确，也可能在符号、端点、周期、象限、选项或答案类型上有错误。

你的工作方式应当是“自己计算后审查和修改”，而不是“默认相信，简单点保存”。

### 2.2 Oracle-URM：题目的标准结构化理解

Oracle-URM 描述的是题目本身，包括目标公式、变量、已知条件和求解目标。它相当于把自然语言题目整理成算法能够准确读取的“数学题目卡片”。

Oracle-URM **不能包含正确答案、人工推导结果或求解器预测**。例如，题目只给出 `\sin\alpha=3/5` 且说明角在第二象限，Oracle 中可以记录这两个已知条件，但不能把推导出的 `\cos\alpha=-4/5` 作为显式约束写进去。

### 2.3 Gold：标准数学答案

Gold 是你根据题面独立推导出的正确答案。它可能是：

- 一个数或表达式，如 `-\frac{3}{4}`；
- 一个普通集合，如 `[2,6]`；
- 一个无限周期集合，如 `x=\frac{\pi}{3}+k\pi,\ k\in\mathbb Z`。

页面会把你填写的 LaTeX 自动转换为 AST 或结构化集合。你不需要手写 JSON 或 AST。

## 3. 算法支持的五类题目

当前 50 题的题型已经锁定。页面左侧显示的“题型”不能修改。如果你认为某题的锁定题型明显不符合题面，应在“简短人工依据、修改理由或歧义说明”中写明理由，不要自行删除题目。

### 3.1 五类题型总览

| 题型 | 主要问题 | 常用操作 | 常见 Gold 类型 |
|---|---|---|---|
| `EVAL` | 求一个三角值或表达式的精确值 | `evaluate` | `expression` |
| `IDENTITY` | 化简表达式或证明恒等式 | `simplify`、`prove_identity` | `expression` |
| `SINUSOID_PROPERTY` | 求正弦型/余弦型函数的图像与性质 | `property` | `expression`、`set`、`periodic_set` |
| `EQUATION` | 求基础三角方程的全部实数解 | `solve_equation` | `periodic_set` |
| `DOMAIN_RANGE_INEQUALITY` | 求定义域、值域或基础三角不等式解集 | `domain`、`range`、`solve_inequality` | `set`、`periodic_set` |

### 3.2 `EVAL`：三角函数求值

#### 识别特征

题目要求计算一个确定的三角函数值或表达式的精确值，常见信息包括：

- 特殊角，如 $30^\circ$、$45^\circ$、$\pi/6$；
- 诱导公式、和差角公式、倍角公式；
- 单位圆坐标；
- 已知一个三角值和象限，求另一个三角值；
- 结果通常是一个数，不含待求的自由变量。

#### 示例

已知角 $\alpha$ 的终边与单位圆交于 $(-4/5,3/5)$，求 $\tan\alpha$。

因为单位圆上 $\cos\alpha=-4/5$、$\sin\alpha=3/5$，所以

$$
\tan\alpha=\frac{\sin\alpha}{\cos\alpha}=-\frac{3}{4}.
$$

该题属于 `EVAL`，Gold 是 `expression`。

#### 不属于本类的情况

- 化简一个仍含变量的通式：通常属于 `IDENTITY`；
- 求满足方程的全部 $x$：属于 `EQUATION`；
- 求函数的周期、单调性或对称性：属于 `SINUSOID_PROPERTY`。

### 3.3 `IDENTITY`：恒等变换与化简

#### 识别特征

题目主要要求：

- 化简含三角函数的表达式；
- 把表达式变换成指定形式；
- 证明等式对原表达式有定义的所有变量值恒成立。

常用公式包括平方关系、商数关系、和差角、倍角、降幂、诱导公式及积化和差等。

#### 示例

证明

$$
\frac{\sin\alpha}{1-\cos\alpha}
\cdot
\frac{\cos\alpha\tan\alpha}{1+\cos\alpha}=1.
$$

在页面中，目标公式填写等号左侧表达式，操作选择 `prove_identity`，Gold 表达式填写 `1`。题面没有显式给出额外约束时，不要为了推导方便把自己计算出的条件写入 Oracle。

#### `simplify` 与 `prove_identity` 的选择

- 题目说“化简”“求化简结果”：选择 `simplify`。
- 题目明确说“证明……等于……”或“证明恒等式”：选择 `prove_identity`。

### 3.4 `SINUSOID_PROPERTY`：正弦型函数性质

#### 识别特征

研究对象通常可以写成

$$
y=A\sin(\omega x+\varphi)+b
$$

或相应的余弦形式，问题要求计算或判断：

- 振幅、周期、频率参数；
- 相位参数、左右平移、中线；
- 最大值、最小值和值域；
- 单调递增/递减区间；
- 对称轴、对称中心。

#### 示例

函数

$$
y=2\sin\left(2x-\frac{\pi}{4}\right)
$$

的一个单调递减区间是

$$
\left[\frac{3\pi}{8},\frac{7\pi}{8}\right].
$$

该函数最小正周期为 $\pi$。若用 `periodic_set` 表示全部重复的递减区间，可在基本区间 $[0,\pi)$ 内填写上述区间，并令周期为 `\pi`。

#### 与 `DOMAIN_RANGE_INEQUALITY` 的区别

如果题目主要研究正弦型函数的图像参数或性质，属于本类。若题目直接要求一般表达式的定义域、值域，或求三角不等式解集，则属于 `DOMAIN_RANGE_INEQUALITY`。当前题型已经锁定；有疑问时记录说明，不根据求解器表现改题型。

### 3.5 `EQUATION`：基础三角方程完整实数解

#### 识别特征

题目要求解含一个主变量的基础三角方程，例如：

- $\sin(ax+b)=c$；
- $\cos(ax+b)=c$；
- $\tan(ax+b)=c$；
- 可化为上述形式的简单同元方程。

本测试集中的 10 道 `EQUATION` **全部要求完整实数周期解集**，不能只写 $[0,2\pi)$ 或其他限制区间内的基本解。

#### 示例

解方程

$$
\sin(\pi+x)=-\sqrt{3}\cos(2\pi-x).
$$

化简得 $\tan x=\sqrt{3}$，因此

$$
x=\frac{\pi}{3}+k\pi,\qquad k\in\mathbb Z.
$$

在页面中不要把 `x=...+k\pi` 当作普通字符串答案，而应填写：

- Gold 类型：`periodic_set`；
- 最小正周期：`\pi`；
- 周期变量：`x`；
- 基本点：`\frac{\pi}{3}`。

#### 必查事项

- 是否给出了所有分支；
- 是否使用了最小正周期；
- 基本点是否全部化到 $[0,T)$；
- 是否因平方、约分或除以三角函数而产生增根或漏根；
- 是否检查了原方程的定义域。

### 3.6 `DOMAIN_RANGE_INEQUALITY`：定义域、值域与不等式

#### 识别特征

本类包含三种目标：

1. `domain`：求函数在哪些实数上有定义；
2. `range`：求函数值或参数的可能范围；
3. `solve_inequality`：求三角不等式的解集。

#### 普通集合示例

若

$$
\sqrt{3}\sin x+\cos x=4-m,
$$

求 $m$ 的取值范围。因为左侧值域为 $[-2,2]$，所以 $4-m\in[-2,2]$，得到

$$
m\in[2,6].
$$

目标公式是 `m`，已知方程写入“显式约束”，Gold 类型为 `set`，集合类型为 `interval`。

#### 周期集合示例

求 $\tan(2x-\pi/4)$ 的定义域。函数在

$$
x=\frac{3\pi}{8}+k\frac{\pi}{2},\qquad k\in\mathbb Z
$$

处无定义。因此可用 `periodic_set` 表示：周期为 $\pi/2$，基本周期内全部包含，但排除基本点 $3\pi/8$。

## 4. 核心对象：Trig-URM

### 4.1 为什么需要 Trig-URM

同一道数学题可以用很多自然语言方式表达。算法不能只看关键词，需要明确知道：

- 哪个公式是目标；
- 主变量是谁；
- 角度使用度数还是弧度；
- 题面明确给了哪些条件；
- 要执行哪类数学操作；
- 方程是否要求全部实数解。

Trig-URM 就是对这些信息的统一表示。可以把它理解为一张标准化的“题目结构卡”。

### 4.2 当前代码中的 Trig-URM 结构

```text
TrigURM
├── schema_version       结构版本
├── angles               角/主变量的状态
│   └── AngleState
│       ├── symbol       变量名，如 x、alpha
│       ├── unit         radian / degree / unspecified
│       ├── domain       默认实数域
│       └── quadrant     1 / 2 / 3 / 4，或空
├── expressions          公式列表
│   ├── E1               目标公式
│   └── E2、E3……         公式型显式约束
├── constraints          等式、不等式、成员或属性约束
├── goal
│   ├── task_family      锁定的五类题型之一
│   ├── operator         evaluate / simplify / ...
│   ├── target_refs      当前页面固定指向 E1
│   ├── property_names   要求的函数性质
│   └── completeness     解集完整性
└── derived_facts        求解过程中产生的事实；人工标注时通常为空
```

表达式会被自动转成受限的 `ExprAST`。AST 可以表示整数、有理数、符号、$\pi$、四则运算、幂、绝对值、正弦/余弦/正切、反三角函数和标量关系。它不能执行任意程序，也不接受任意未知函数。

### 4.3 Oracle-URM 与 Gold 必须分开

以“已知 $\sin\alpha=3/5$，$\alpha$ 在第二象限，求 $\cos\alpha$”为例：

- Oracle-URM 记录目标 `\cos\alpha`、条件 `\sin\alpha=3/5` 和第二象限；
- Gold 记录 `-4/5`；
- 不得把 `\cos\alpha=-4/5` 放回显式约束，因为这是答案，不是题面已知条件。

## 5. 核心对象：TMM 与 DIS

### 5.1 什么是 TMM

TMM 是 Trigonometric Meta-Model，可理解为“只负责一种典型三角运算的数学模块”。每个 TMM 都有适用条件、执行操作和输出。它不是让标注者填写的字段，但 Oracle-URM 是否准确会决定算法选择哪个 TMM。

当前代码包含以下 9 个 TMM：

| TMM | 主要职责 | 典型操作 |
|---|---|---|
| `TMM-AngleNormalize` | 统一角状态 | 识别角制、把内部计算统一到弧度、记录象限状态 |
| `TMM-ExactEvaluate` | 精确求值 | 特殊角求值；由已知 `sin/cos/tan` 和象限推出目标值 |
| `TMM-IdentityRewrite` | 恒等变换 | `trigsimp`、展开、化简和有界恒等变换，并检查前后等价 |
| `TMM-SinusoidCanonicalize` | 正弦型标准化 | 把表达式整理为 $A\sin(\omega x+\varphi)+b$ 或余弦形式，提取 $A,\omega,\varphi,b$ |
| `TMM-PropertyDerive` | 推导函数性质 | 周期、振幅、平移、中线、最值、值域、单调区间、对称轴和对称中心 |
| `TMM-EquationBaseSolve` | 求一个基本周期内的方程解 | 隔离单个三角函数，求基本分支并逐点回代 |
| `TMM-DomainRangeInequality` | 定义域、值域和不等式 | 连续定义域、正弦型值域、一个周期内的不等式区间 |
| `TMM-PeriodicComplete` | 周期补全 | 把基本点或基本区间提升为全部 $kT$ 平移后的完整集合 |
| `TMM-AnswerValidate` | 最终校验 | 精确等价检查、方程回代、与选择题选项匹配 |

### 5.2 什么是 DIS

DIS 是 Decoupled Inference Strategy，可理解为“根据题型安排 TMM 执行顺序的调度器”。当前五条主要路径是：

```text
EVAL
  AngleNormalize → ExactEvaluate → AnswerValidate

IDENTITY
  AngleNormalize → IdentityRewrite → AnswerValidate

SINUSOID_PROPERTY
  AngleNormalize → SinusoidCanonicalize → PropertyDerive → AnswerValidate

EQUATION
  AngleNormalize → EquationBaseSolve → PeriodicComplete → AnswerValidate

DOMAIN_RANGE_INEQUALITY
  AngleNormalize → DomainRangeInequality → PeriodicComplete（需要时）→ AnswerValidate
```

如果题目超出模块前置条件、符号计算无法确定结果或答案无法严格验证，算法会明确 abstain（拒答），而不是猜测。人工 Gold 仍应按正确数学答案标注，不能为了避免算法拒答而改变目标或答案。

## 6. Oracle-URM 区域逐项填写规则

### 6.1 目标公式 LaTeX

#### 含义

算法真正要处理的那个表达式、方程或不等式，即 Oracle-URM 中的 `E1`。

#### 填写原则

- 只填数学公式，不填“求”“证明”“等于多少”等中文指令；
- 不包含 `$...$` 外层定界符；
- 尽量保留题面形式，不为了迎合求解器提前完成关键化简；
- 求函数性质时，通常填写 $y=$ 右侧的函数表达式；
- 解方程时填写完整等式；
- 解不等式时填写完整不等式；
- 参数范围题中，如果目标是参数 $m$，目标公式填 `m`，题面等式放入显式约束；
- 证明 `左式=右式` 时，当前页面通常把左式作为目标，Gold 填右式或最终化简结果。

#### 例子

- 求值：`\tan\alpha`
- 函数性质：`2\sin(2x-\frac{\pi}{4})`
- 方程：`\sin(\pi+x)=-\sqrt{3}\cos(2\pi-x)`
- 不等式：`\sin x>\frac{1}{2}`

### 6.2 主变量

#### 含义

题目主要围绕哪个符号求值、变化或求解。

#### 填写原则

- 填普通安全符号名，不填 LaTeX 反斜杠；
- `x` 填 `x`，$\alpha$ 填 `alpha`，$\theta$ 填 `theta`，$\omega$ 填 `omega`；
- 方程和不等式填待求变量；
- 参数范围题若最终求 $m$，主变量应填 `m`；
- 不要把整数参数 `k` 当成主变量，`k` 只是周期解表示中的整数指标。

### 6.3 操作

操作选项由锁定题型决定：

| 题型 | 可选操作 | 何时使用 |
|---|---|---|
| `EVAL` | `evaluate` | 求精确值 |
| `IDENTITY` | `simplify` | 化简表达式 |
| `IDENTITY` | `prove_identity` | 题目明确要求证明恒等式 |
| `SINUSOID_PROPERTY` | `property` | 求函数图像或性质 |
| `EQUATION` | `solve_equation` | 求三角方程解 |
| `DOMAIN_RANGE_INEQUALITY` | `domain` | 求定义域 |
| `DOMAIN_RANGE_INEQUALITY` | `range` | 求值域或参数范围 |
| `DOMAIN_RANGE_INEQUALITY` | `solve_inequality` | 求不等式解集 |

### 6.4 角制

| 选项 | 使用条件 |
|---|---|
| `degree` | 题目使用角度符号 `°`，如 $30^\circ$ |
| `radian` | 题目使用 $\pi$ 表示角，或明确说明使用弧度 |
| `unspecified` | 抽象角只以三角值、单位圆点等出现，题面没有指定度或弧度，且单位不影响结论 |

不要因为个人习惯把度数题改成弧度表达式。若同一题的角制明显混乱，记录歧义说明。

### 6.5 象限约束

可选空、1、2、3、4。

- 题目明确写“第一/二/三/四象限”时填写对应数字；
- 题目给出的单位圆坐标符号唯一确定象限时，可以填写对应象限；
- 给出明确角度范围且唯一落在一个象限时，可以填写该象限；
- 无法唯一确定时留空；
- 一般的函数变量 $x$ 遍历实数时留空。

象限直接影响由平方关系开方时的正负号，不能凭感觉填写。

### 6.6 显式约束

#### 含义

题面明确给出的等式、不等式、成员关系或属性。每行一条。

#### 四种写法

1. 等式可直接填写：

   ```text
   \sin\alpha=\frac{3}{5}
   ```

2. 不等式可直接填写：

   ```text
   \omega>0
   ```

3. 不便写成公式 AST 的属性：

   ```text
   [property] unit_circle_point=(-4/5,3/5)
   ```

4. 集合或区间成员关系：

   ```text
   [membership] alpha=(pi/2,pi)
   ```

也可以显式加前缀 `[equation]` 或 `[inequality]`，但普通关系式通常不需要。

#### 核对原则

- 只写题面已给信息；
- 不写你推导出的中间结论；
- 不写最终答案；
- 不把选择题选项当约束；
- 不遗漏会改变正负号、定义域或参数范围的条件；
- 原题条件如 $\omega>0$、$|\varphi|<\pi$、$x\in[0,\pi]$ 都应保留。

### 6.7 性质名称

仅 `SINUSOID_PROPERTY` 使用；其他题型通常留空。性质名称表示题目究竟要求哪个函数性质，而不是你在解题过程中顺便算出的所有性质。

当前 50 题 Silver 使用的主要标签如下：

| 标签 | 含义 |
|---|---|
| `minimum_positive_period` | 最小正周期 |
| `frequency_parameter` | 由条件求频率参数 $\omega$ |
| `phase_parameter` | 由条件求相位参数 $\varphi$ |
| `horizontal_shift_right` | 向右平移量 |
| `monotonic_decreasing_interval` | 周期性的单调递减区间 |
| `restricted_monotonic_increasing_interval` | 指定区间内的单调递增区间 |
| `symmetry_axis` | 对称轴 |
| `symmetry_center_x` | 对称中心的横坐标 |

填写规则：

- Silver 标签与题意一致时保留；
- 不要为了让当前求解器更容易处理而改写题意；
- 不要自行创造同义标签，例如同时使用 `period`、`周期`、`min_period` 表示同一概念；
- 一题确实要求多个性质时用英文逗号分隔，但当前 50 题原则上是单目标题；
- 若现有标签无法准确表示题意，在说明区记录，不要随意编造新标签。

### 6.8 解集完整性

| 选项 | 使用条件 |
|---|---|
| `not_applicable` | 求值、化简、函数性质、定义域或值域等不使用“方程解集完整性”的任务 |
| `restricted` | 只求题面指定区间内的方程/不等式解 |
| `all_real` | 求全部实数解 |

当前 10 道 `EQUATION` 会强制为 `all_real`，不能修改。对于不等式，按题面是否限制区间选择；定义域和值域通常为 `not_applicable`。

## 7. 独立审查数学 Gold 区域逐项填写规则

### 7.1 先选 Gold 类型

#### `expression`

用于单个精确数值、代数表达式或参数值，例如：

- `-\frac{3}{4}`；
- `\frac{\sqrt{6}-\sqrt{2}}{4}`；
- `2\pi`；
- `\frac{3}{2}`。

填写精确形式，不用小数近似。页面会自动生成 `ExprAST`。

#### `set`

用于不依靠周期重复表示的普通实数集合，例如：

- 值域 `[2,6]`；
- 指定区间内的解集；
- 有限参数集合；
- 若干区间的并集。

#### `periodic_set`

用于由一个基本周期中的点或区间经过 $kT$ 平移得到的无限集合，例如：

- 三角方程的全部实数解；
- 全部单调区间；
- 全部对称轴或对称中心横坐标；
- 周期性不等式解集；
- 周期性定义域及排除点。

所有 `EQUATION` 都强制使用 `periodic_set`。

### 7.2 Gold 表达式 LaTeX

- 填最终数学答案，不填推导过程；
- 不带 `$...$`；
- 使用精确分数、根式和 $\pi$，不使用近似小数；
- 负号必须明确；
- 不要把选择题字母填在这里；
- 不要手写 AST，页面会自动生成。

### 7.3 普通集合的六种类型

| 集合类型 | 含义 | 如何填写 |
|---|---|---|
| `empty` | 空集 | 无需额外内容 |
| `reals` | 全体实数 | 无需额外内容 |
| `finite` | 有限集合 | 每行一个元素 |
| `interval` | 一个区间 | 如 `[0,2]`、`(-\infty,-1]` |
| `union` | 至少两个集合的并 | 每行一个区间、有限集、`R` 或 `empty` |
| `difference` | 集合差 | 分别填写“基础集合”和“移除集合” |

#### 端点规则

- `[` 或 `]` 表示包含端点；
- `(` 或 `)` 表示不包含端点；
- 无穷端点必须开放，如 `(-\infty,2]`；
- 解不等式时尤其检查等号、原式定义域和分母为零点；
- 多个分量每行一个，不要把整段中文解集填进文本框。

### 7.4 周期集合字段

设最小正周期为 $T$。页面固定以半开基本区间 $[0,T)$ 规范化周期集合。

#### 最小正周期

- 填精确正数，如 `\pi`、`2\pi`、`\frac{\pi}{2}`；
- 优先使用最小正周期；
- 不填 `k\pi`，周期本身不含整数参数；
- 周期必须是确定的正常数。

#### 周期变量

填写被周期平移的变量，如 `x`、`alpha`。通常应与 Oracle 的主变量相同。

#### 基本点

- 每行一个点；
- 每个点必须在 $[0,T)$ 内；
- 等价点只保留一个；
- 建议从小到大排列；
- 不写 `+kT`，页面的 `periodic_set` 已经表示对所有 $k\in\mathbb Z$ 平移。

例如 $x=\pi/3+k\pi$ 填：

```text
周期：\pi
基本点：\frac{\pi}{3}
```

#### 基本区间

- 每行一个区间；
- 每个区间必须位于 $[0,T]$ 内；
- 跨越周期端点的区间必须拆成两行；
- 若区间右端等于 $T$，必须右开，因为 $T$ 与下一个周期的 0 是同一点；
- 仔细检查单调区间端点是否应包含，以及不等式是严格还是非严格。

例如跨越 $0$ 的解集可写成：

```text
[0,\frac{\pi}{6})
(\frac{11\pi}{6},2\pi)
```

#### 基本周期内全部包含

勾选 `full_period` 表示每个基本周期原则上全部包含，通常与“排除点”一起表示周期性定义域。

勾选后不能再填“基本点”或“基本区间”。

#### 排除点

- 每行一个在 $[0,T)$ 内的点；
- 用于原表达式无定义、分母为零或题目明确排除的位置；
- 不要把已经不在包含区间内的点重复排除；
- 必须回到原式检查，防止约分后丢失定义域限制。

例如 $\tan(2x-\pi/4)$ 的定义域：

```text
周期：\frac{\pi}{2}
full_period：勾选
排除点：\frac{3\pi}{8}
```

### 7.5 Gold 选项

仅选择题需要填写 A、B、C 或 D。

必须按以下顺序操作：

1. 不看 Silver 选项，先独立计算数学 Gold；
2. 把数学 Gold 与每个选项比较；
3. 确认唯一匹配后再选择字母；
4. 再检查字母位置有没有看错。

开放题的 Gold 选项由页面强制为 `null`。如果两个选项数学等价、没有唯一正确选项，必须在说明区记录，不要根据原始答案键猜测。

### 7.6 简短人工依据、修改理由或歧义说明

建议写一至三句，记录能够支持审查的关键数学依据，例如：

```text
单位圆点给出 sin=3/5、cos=-4/5，因此 tan=-3/4；数学 Gold 对应 D。
```

以下情况必须说明：

- 修改了 Silver 的任何实质字段；
- 周期、端点、排除点或选项存在容易混淆之处；
- 题面有歧义、排版错误或疑似多解；
- 你认为锁定题型或输出格式可能不合适；
- 页面 schema 无法表达正确答案。

不要粘贴原数据解析、来源答案、求解器输出或另一位标注者的结论。

## 8. 五个完整标注示例

### 8.1 示例一：`EVAL` 单位圆求值

题目：已知角 $\alpha$ 的终边与单位圆交于 $(-4/5,3/5)$，求 $\tan\alpha$。

```text
Oracle-URM
目标公式：\tan\alpha
主变量：alpha
操作：evaluate
角制：unspecified
象限约束：2
显式约束：[property] unit_circle_point=(-4/5,3/5)
性质名称：留空
解集完整性：not_applicable

Gold
类型：expression
表达式：-\frac{3}{4}
Gold 选项：D
```

说明：单位圆点横坐标为余弦、纵坐标为正弦，因此 $\tan\alpha=(3/5)/(-4/5)=-3/4$。

### 8.2 示例二：`IDENTITY` 证明恒等式

题目：证明

$$
\frac{\sin\alpha}{1-\cos\alpha}
\frac{\cos\alpha\tan\alpha}{1+\cos\alpha}=1.
$$

```text
Oracle-URM
目标公式：\frac{\sin\alpha}{1-\cos\alpha}\frac{\cos\alpha\tan\alpha}{1+\cos\alpha}
主变量：alpha
操作：prove_identity
角制：unspecified
象限约束：留空
显式约束：留空
性质名称：留空
解集完整性：not_applicable

Gold
类型：expression
表达式：1
Gold 选项：开放题，自动为 null
```

说明：Gold 表示原式在其定义域内的化简结果。不要把“原式分母不为零”误写成题面显式给出的附加条件。

### 8.3 示例三：`SINUSOID_PROPERTY` 周期单调区间

题目：函数 $y=2\sin(2x-\pi/4)$ 的一个单调递减区间是哪个选项？

```text
Oracle-URM
目标公式：2\sin(2x-\frac{\pi}{4})
主变量：x
操作：property
角制：radian
象限约束：留空
显式约束：留空
性质名称：monotonic_decreasing_interval
解集完整性：not_applicable

Gold
类型：periodic_set
最小正周期：\pi
周期变量：x
基本区间：[\frac{3\pi}{8},\frac{7\pi}{8}]
full_period：不勾选
排除点：留空
Gold 选项：A
```

说明：$2x-\pi/4\in[\pi/2,3\pi/2]$ 时正弦函数递减，解得该基本区间，并以 $\pi$ 为周期重复。

### 8.4 示例四：`EQUATION` 完整周期解

题目：解 $\sin(\pi+x)=-\sqrt3\cos(2\pi-x)$。

```text
Oracle-URM
目标公式：\sin(\pi+x)=-\sqrt{3}\cos(2\pi-x)
主变量：x
操作：solve_equation
角制：radian
象限约束：留空
显式约束：留空
性质名称：留空
解集完整性：all_real（页面锁定）

Gold
类型：periodic_set（页面锁定）
最小正周期：\pi
周期变量：x
基本点：\frac{\pi}{3}
基本区间：留空
full_period：不勾选
排除点：留空
Gold 选项：A
```

说明：完整答案是 $x=\pi/3+k\pi$，不是只有 $x=\pi/3$。页面用“周期 + 基本点”表达全部整数平移。

### 8.5 示例五：`DOMAIN_RANGE_INEQUALITY` 参数范围

题目：已知 $\sqrt3\sin x+\cos x=4-m$，求 $m$ 的取值范围。

```text
Oracle-URM
目标公式：m
主变量：m
操作：range
角制：unspecified
象限约束：留空
显式约束：\sqrt{3}\sin x+\cos x=4-m
性质名称：留空
解集完整性：not_applicable

Gold
类型：set
集合类型：interval
区间：[2,6]
Gold 选项：A（若该记录为选择题）
```

说明：目标是参数 $m$，不是左侧三角表达式；左侧表达式的值域只是求 $m$ 范围所需的已知关系。

## 9. 每道题的标准操作流程

建议对每题严格执行以下 8 步：

1. **只读题面和选项。** 先确认题目问什么，不先看 Silver 是否“像对的”。
2. **在草稿纸上独立求解。** 写出关键公式、定义域、基本解和周期。
3. **核对锁定元数据。** 查看题型、输出格式和题面是否一致；不一致时记录说明。
4. **审查 Oracle-URM。** 逐项核对目标公式、主变量、操作、角制、象限、显式约束、性质名称和完整性。
5. **审查数学 Gold。** 先决定 `expression`、`set` 或 `periodic_set`，再核对具体内容。
6. **最后核对选择题字母。** 数学 Gold 正确后，再确认 A/B/C/D。
7. **查看结构化预览。** 确认 AST、集合端点、周期、基本点和排除点没有被错误解析。
8. **填写简短依据并保存。** 看到“结构校验通过”后，仍要自己确认数学正确，再点击“确认并保存人工审查”。

页面会自动保存草稿。只有点击“确认并保存人工审查”后，该题才算正式完成。

## 10. “结构校验通过”不代表什么

绿色提示只说明填写内容满足数据结构要求，例如：

- 公式能转换成允许的 AST；
- 选择题字母存在；
- 周期是正数；
- 基本点位于 $[0,T)$；
- 区间格式合法。

它**不能**证明：

- 目标公式抄对了；
- 题型理解正确；
- Silver 的答案正确；
- 端点的开闭正确；
- 周期是最小正周期；
- 方程没有漏根或增根；
- 选择题字母和数学 Gold 一致。

数学正确性只能由你人工核算确认。

## 11. 遇到问题时怎么处理

### 11.1 Silver 明显错误

直接修改为你独立得到的正确内容，并在说明中写明修改的字段和数学理由。

### 11.2 题目困难但属于范围

保留并完成。不能因为难、耗时或怀疑算法不会做而删除或换题。必要时可以暂停该题，先做其他题，最后回来复核。

### 11.3 题面有歧义或疑似错误

不要私自猜测原作者意图。记录：

- 哪一段题面有问题；
- 存在哪几种数学解释；
- 不同解释是否导致不同答案；
- 你暂时采用了哪一种解释及理由。

### 11.4 页面无法表达正确答案

不要用错误结构勉强保存。例如方程确实无实数解但页面又强制非空 `PeriodicSet` 时，不得伪造基本点。应在说明中明确写“正确答案与当前 schema 冲突”，并及时报告负责人。

### 11.5 Silver 与你的结果不同

重新独立计算一次，重点检查符号、象限、端点、周期、定义域和选项顺序。仍不一致时，以数学推导为准修改 Silver，并记录理由；不要查询求解器输出来“投票”。

## 12. 50 题完成后的验收标准

Annotator A 的结果只有同时满足以下条件才算合格：

- 50 题全部显示为已完成人工审查；
- 每题均独立核算，不直接接受机器 Silver；
- Oracle-URM 只包含题面目标和显式信息，没有答案泄漏；
- 目标公式、主变量、操作、角制、象限和约束均与题面一致；
- `SINUSOID_PROPERTY` 的性质名称准确对应题目所问内容；
- Gold 类型选择正确，表达式使用精确形式；
- 普通集合的端点、开闭、并集和排除关系正确；
- 周期集合使用最小正周期，基本点位于 $[0,T)$，跨周期区间已拆分；
- 10 道 `EQUATION` 全部为 `all_real + periodic_set`，没有只写限制区间内解；
- 所有方程均检查漏根、增根和原式定义域；
- 选择题先有独立数学 Gold，再确认唯一选项字母；
- 开放题的 `gold_option` 为 `null`；
- 修改 Silver、发现歧义或遇到 schema 问题时写有清楚说明；
- 未查看 Annotator B 的文件、原始答案、求解器预测或实验结果；
- 每题保存前都检查过自动生成的结构化预览。

## 13. 最后一分钟检查表

保存每题前快速问自己：

```text
[ ] 我能用自己的推导解释答案吗？
[ ] Oracle 写的是题面信息，而不是我推导出的答案吗？
[ ] 目标公式和主变量选对了吗？
[ ] 度数、弧度和象限核对了吗？
[ ] Gold 类型选对了吗？
[ ] 分数、根式、π 使用的是精确值吗？
[ ] 集合端点开闭、定义域排除点检查了吗？
[ ] 周期是最小正周期吗？基本点都在 [0,T) 吗？
[ ] 方程写的是全部实数解吗？
[ ] 选择题字母与数学 Gold 一致吗？
[ ] 绿色结构校验之外，我确认了数学正确性吗？
```

只要其中一项不能确定，就先不要点击最终确认，重新检查或在说明中明确记录问题。
