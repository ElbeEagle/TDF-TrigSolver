# 三角函数题自动求解研究调研

> 调研日期：2026-08-07  
> 重点时间范围：2021 年至今；更早工作仅作为符号计算背景。  
> 证据来源：论文/会议官网、作者官方项目、GitHub、Hugging Face Dataset Viewer，以及仓库内 `data/` 的实际样本。OpenAlex 和搜索摘要未被用作关键结论依据。

## 结论摘要

1. **目前没有一个成熟、公开、可复现、覆盖完整 A 类三角函数题的专用 solver。** 近五年的直接工作主要集中在三个窄任务：AutoTrig 处理合成三角恒等式证明；TRIGO 处理 Lean 中的三角表达式形式化化简；SSC-CoT 在 100 道复杂三角题上改进 LLM 的逐步推理。它们尚未覆盖自然语言理解、图像解析、函数性质、图像变换、方程/不等式、完整周期解集和可验证推导这一整条链路。
2. **可复用数据是存在的，但没有一套现成数据同时满足 TDF 的范围、结构和评价需要。** 文本优先级较高的是 UGMathBench-Trigonometry、MATH-Precalculus、MathOdyssey；中文及图文题优先考虑 CMM-Math；函数图像题可从 MathVista/FunctionQA 和 MathVerse 提取；OlympiadBench 可补充高难题，但 A/B 混杂明显。
3. **仓库内两套数据的价值差异很大。** 对 `data/CMM-Math/all_data.jsonl` 的高精度规则初筛得到 499 个 A 类候选，其中 81 个包含图像引用；对 `data/multimath/multimath_function.json` 的审查表明，关键词命中的“三角”题几乎都是锐角三角比、解三角形或测量应用，即 B 类，不能直接当作三角函数结构数据。
4. **下一阶段不宜在“全部复用”和“完全自建”之间二选一。** 最合理路线是：复用公开数据形成候选池，重新按 A/B/C、题型、模态和结构字段标注，构建一个规模适中但结构化、可验证的 TDF-Trig 数据集；同时建立 raw-input 与 oracle-structure 两条评测轨道，分别测量解析和求解。

## 1. 调研范围与分类标准

### 1.1 A/B/C 分类

| 类别 | 纳入标准 | 典型题目 | 本报告处理方式 |
|---|---|---|---|
| A：直接三角函数题 | 求解对象是三角函数的定义、表达式、图像、性质、恒等变换、方程、不等式或周期模型 | 求 $y=A\sin(\omega x+\varphi)+b$ 的周期/相位；证明恒等式；求三角方程完整解集 | 核心研究对象 |
| B：几何中使用三角知识 | 核心对象是三角形、长度、角度或几何关系，三角比/正余弦定理只是工具 | 已知三角形边角求另一边；测塔高；几何图中求正弦值 | 作为相邻任务单列，不计入 A 类核心集合 |
| C：非题目求解语境 | “trigonometric” 仅出现在优化、数值计算、PDE、机器人、信号处理或教育效果研究中 | 含三角方程的逆运动学、谐波消除、教学干预 | 原则上排除 |

需要特别指出：数据集原标签 `Trigonometric Functions` 或关键词 `sin` 并不自动等于 A 类。例如 OlympiadBench 中大量标为 `Trigonometric Functions` 的高考题实际仍以三角形为对象，应归为 B 类。

### 1.2 纳入一项工作的证据标准

- 论文正文或官方项目必须明确给出任务、数据或方法；不能根据标题或搜索摘要推断。
- 综合 benchmark 必须由类别标签或实际样本确认含有三角函数题；模型只在其总榜上出现，不等于已证明具有三角函数能力。
- GitHub 仅采用论文、作者项目页或数据卡反向链接的官方仓库；未把个人练习、教学作业和通用网页计算器视为研究成果。
- “可复用”至少要求数据/代码可访问、任务边界清楚，或能从官方数据中稳定抽取样本。

### 1.3 检索覆盖与排除结果

本次交叉使用了精确题名/短语检索、Google Scholar 补充检索、论文参考链、作者项目反查和 Hugging Face Dataset Viewer。查询覆盖 `trigonometric problem solving`、`trigonometric equation solver`、`trigonometric identity theorem proving`、`automatic solving trigonometry problems`、`trigonometry dataset mathematical reasoning`、`trigonometric function large language model`、`trigonometry multimodal benchmark` 和 `trigonometric formal proof language model` 等组合。

宽泛查询会集中返回三类噪声：机器人逆运动学中的三角方程、谐波/信号/数值算法，以及三角函数教学效果研究。它们分别属于本报告的 C 类工程应用或教育研究，未列入 solver 证据。对 2021 年以来的直接结果继续由论文正文和官方项目核验后，仍只保留 AutoTrig、TRIGO、SSC-CoT/TriMaster100 三个专用或半专用代表。

## 2. 工作与资源汇总

| 工作或资源 | 年份 | 类型 | 三角函数相关性 | 文本/多模态 | 代码或数据 | 对 TDF 的价值 |
|---|---:|---|---|---|---|---|
| [AutoTrig](https://arxiv.org/abs/2207.06679) | 2022 | 恒等式自动证明方法 | A：高度直接，但仅恒等式 | 符号/文本 | 未定位到作者官方代码或数据发布 | 规则库、规范化、短证明搜索可作 DIS 参考 |
| [TRIGO](https://aclanthology.org/2023.emnlp-main.711/) | 2023 | EMNLP 形式化证明 benchmark | A：高度直接，但仅表达式化简 | Lean 形式语言 | 论文给出构造方法；未定位到稳定官方仓库 | 可验证逐步证明与难度/分布划分参考 |
| [SSC-CoT / TriMaster100](https://arxiv.org/abs/2402.17786) | 2024 | LLM 推理方法与专用数据 | A：直接，100 道复杂三角题 | 文本 | [GitHub/数据](https://github.com/zhao-zilong/ssc-cot) | 过程级评分和复杂题基线 |
| [MATH](https://arxiv.org/abs/2103.03874) | 2021 | 竞赛数学 benchmark | A+B：Precalculus 中有大量 A 类 | 文本 | [GitHub](https://github.com/hendrycks/math) / [HF](https://huggingface.co/datasets/EleutherAI/hendrycks_math) | 英文恒等式、反函数、方程等文本题源 |
| [MathOdyssey](https://arxiv.org/abs/2406.18321) | 2024 | 高中至大学数学 benchmark | A+B：官网有 Trigonometry/PreCalculus | 文本 | [项目页](https://mathodyssey.github.io/) / [GitHub](https://github.com/protagolabs/odyssey-math) / [HF](https://huggingface.co/datasets/MathOdyssey/MathOdyssey) | 较新、测试专用的英文题源 |
| [OlympiadBench](https://arxiv.org/abs/2402.14008) | 2024 | ACL 双语多模态 benchmark | A+B：有直接方程，也有大量三角形题 | 文本+图像 | [GitHub](https://github.com/OpenBMB/OlympiadBench) / [HF](https://huggingface.co/datasets/Hothan/OlympiadBench) | 中英高难题；适合困难集，需严格去 B |
| [MathVista](https://arxiv.org/abs/2310.02255) | 2024 | ICLR 多模态 benchmark | A+B：FunctionQA 有直接函数图像题 | 图像+文本 | [GitHub](https://github.com/lupantech/MathVista) / [HF](https://huggingface.co/datasets/AI4Math/MathVista) | 三角函数图像理解小而明确的来源 |
| [MathVerse](https://arxiv.org/abs/2403.14624) | 2024 | ECCV 多模态 benchmark | A+B：Functions 子集有图像变换题 | 图像+文本，多视觉依赖版本 | [GitHub](https://github.com/ZrrSkywalker/MathVerse) / [HF](https://huggingface.co/datasets/AI4Math/MathVerse) | 可测试“是否真正看图”和视觉依赖性 |
| [MATH-Vision](https://arxiv.org/abs/2402.14804) | 2024 | NeurIPS 多模态竞赛 benchmark | 当前抽查以 B 类为主 | 图像+文本 | [GitHub](https://github.com/mathllm/MATH-V) / [HF](https://huggingface.co/datasets/MathLLMs/MathVision) | 可作 B 类/视觉迁移对照，A 类优先级较低 |
| [MultiMath-7B / MultiMath-300K](https://arxiv.org/abs/2409.00147) | 2024 | MLLM、训练数据 | 本地 function 子集的三角题几乎全是 B | 图像+文本 | [GitHub](https://github.com/pengshuai-rin/MultiMath) / [HF 数据](https://huggingface.co/datasets/pengshuai-rin/multimath-300k) | 可作几何视觉预训练，不宜作 A 类主数据 |
| [CMM-Math / Math-LMM](https://arxiv.org/abs/2409.02834) | 2024/2025 | ACM MM 中文多模态数据与 MLLM | A+B：实际存在性质、图像、周期、方程题 | 图像+中文文本 | [HF 数据](https://huggingface.co/datasets/ecnu-icalk/cmm-math) / [GitHub](https://github.com/ECNU-ICALK/EduChat-Math) | 当前最有价值的中文 A 类候选池 |
| [UGMathBench-Trigonometry](https://arxiv.org/abs/2501.13766) | 2025 | ICLR 本科数学 benchmark | A+B：有显式 Trigonometry 配置 | 文本 | [GitHub](https://github.com/YangLabHKUST/UGMathBench) / [HF](https://huggingface.co/datasets/UGMathBench/ugmathbench) | 最便于直接加载和按主题重标注的专门分区 |

## 3. 专用三角函数 solver、method 与 algorithm

### 3.1 AutoTrig：合成恒等式上的神经证明搜索

**论文：** Zhou Liu 等，[Learning to Prove Trigonometric Identities](https://arxiv.org/abs/2207.06679)，2022，arXiv。

- **任务：** 自动证明三角恒等式，并尽量缩短证明步数。
- **方法：** 定义恒等式规范形和变换规则；自动生成理论上无限的合成恒等式；用随机 BFS 产生模仿学习数据，再用强化学习改进证明策略。
- **论文结果边界：** AutoTrig 在其合成数据上生成接近 BFS 最短长度的证明，推理时间约为 BFS 的千分之一，并与 SymPy、Matlab 和人工基线比较。
- **真正的相关性：** 属于 A 类，但覆盖的是“已形式化的恒等式证明”，不处理题目理解、图像、函数性质、三角方程完整解集或应用建模。
- **可复用性：** 规范化、规则动作空间、最短证明搜索很适合迁移到 TDF 的结构化求解层；截至本次调研，arXiv 和作者链路没有给出可直接运行的官方仓库，因此工程复用性低于概念复用性。

### 3.2 TRIGO：Lean 中的三角表达式形式化化简

**论文：** Jing Xiong 等，[TRIGO: Benchmarking Formal Mathematical Proof Reduction for Generative Language Models](https://aclanthology.org/2023.emnlp-main.711/)，EMNLP 2023。

- **任务：** 给定三角表达式及其目标化简形式，在 Lean 中生成逐步可验证证明；同时考查常数项组合、分组和因式分解。
- **数据：** 从网页和高中练习/考试收集真实表达式，人工标注化简过程并转成 Lean；TRIGO-real 为 299/42/86 个 train/validation/test 样本，另用 Lean-Gym 生成不同难度和分布的合成划分。
- **方法/模型：** 将 mathlib 定理封装为 tactic，评估生成模型和 GPT 系列模型；论文明确指出该任务对 GPT-4 仍具有挑战。
- **局限：** 输入已经形式化；目标是 proof reduction，而不是从自然语言或图像建立函数模型。它不覆盖定义域、弧度/角度制、周期参数、解集完备性和图像证据。
- **可复用性：** 证明检查、规则级监督和 in-/out-of-distribution 划分值得直接借鉴。论文和 ACL 页面没有提供一个可稳定定位的官方代码/数据仓库，使用前需再次联系作者或按论文复现。

### 3.3 SSC-CoT 与 TriMaster100：复杂三角题上的过程级 LLM 推理

**论文：** Zilong Zhao 等，[Stepwise Self-Consistent Mathematical Reasoning with Large Language Models](https://arxiv.org/abs/2402.17786)，2024，arXiv。

- **任务：** 改善 LLM 在复杂、多步三角题上的推理，而不是构造符号专用求解器。
- **方法：** Stepwise Self-Consistent CoT 在多条推理链之间选择一致的中间步骤，并查询相关领域知识图谱以发现关键步骤。
- **数据：** TriMaster100 含 100 道复杂三角题；每道解答拆成可评分的中间步骤。论文报告 SSC-CoT 在该集合上的效果约为当时方法的三倍，并在 MATH Level 5 上测试通用性。
- **可复用性：** [官方仓库](https://github.com/zhao-zilong/ssc-cot)公开代码和 TriMaster100，适合作为复杂文本题与过程评分基线。
- **局限：** 规模小；依赖 LLM 生成和知识检索；没有符号完备性保证，也没有图像解析或专门的周期解集验证。

### 3.4 成熟 CAS 能力不等于成熟题目 solver

[SymPy `solveset` 文档](https://docs.sympy.org/latest/modules/solvers/solveset.html)等计算机代数系统能够化简三角表达式、求部分方程并用 `ImageSet` 表示周期解。这是应复用的符号基础设施，但它们通常要求已解析的数学表达式，也不会自动完成：

1. 从中文/英文题干和函数图像提取结构；
2. 判断题型与选取人类可读策略；
3. 处理所有隐含定义域、角度制、分支和参数约束；
4. 生成与题目条件对齐、可解释且可核验的完整解答。

因此，“存在成熟 CAS”不能支持“已经存在成熟的专用三角函数题 solver”这一结论。

## 4. LLM/MLLM 工作中的三角函数能力

### 4.1 能直接支持结论的研究

| 研究 | 直接证据 | 可以声称什么 | 不能据此声称什么 |
|---|---|---|---|
| TRIGO | 专门的 Lean 三角表达式 benchmark，包含 GPT-4 等模型实验 | 生成模型能够被直接评测形式化三角化简 | 能解决自然语言、函数图像和完整方程题 |
| SSC-CoT | TriMaster100 专门由复杂三角题构成 | LLM 推理策略可在三角题上做过程级评价 | 已有通用、可靠的三角 solver |
| Math-LMM | 训练/评测使用 CMM-Math；本地数据确认存在 A 类样本 | 中文 MLLM 的训练语料和总体评测确实覆盖部分三角题 | 论文总分等同于 A 类三角能力 |
| MultiMath-7B | MultiMath-300K 覆盖 K-12 图文数学；本地 function 子集有三角关键词 | 模型接触了大量几何三角比和图文数学 | 已覆盖周期、相位、图像和方程等 A 类结构 |

### 4.2 综合 benchmark 中的模型结果应如何解释

MathVista、MathVerse、MATH-Vision 和 OlympiadBench 分别评测过 GPT-4V/GPT-4、Gemini、Claude、LLaVA、Qwen-VL、DeepSeekMath 等闭源或开源模型；MATH 和 MathOdyssey 也被大量数学 LLM 使用。由于这些论文大多报告总体、学科或模态平均分，而不是本报告定义的 A 类三角函数子集分数，严谨表述应是：

> “这些模型在包含若干三角函数题的综合 benchmark 上接受过评测”；不能写成“这些模型已被证明具备三角函数题求解能力”。

TDF 后续实验需要重新生成固定的 `trig_A` 题目清单和独立指标，才能比较 LLM、MLLM、CAS 与 TDF 的真实三角能力。

## 5. 数据集与 benchmark 的实际核验

### 5.1 核验结果总表

下表的“命中”是候选检索规模，不等于人工确认后的 A 类数量。`\sin` 命中可能来自题目或解答；最终仍需人工/结构规则复核。

| 数据集 | 官方规模/配置 | 实际核验 | A/B 判断 | 模态与可用性 | 建议优先级 |
|---|---|---|---|---|---|
| TriMaster100 | 100 题 | 官方说明每题含分步评分 | A 为主 | 文本；代码/数据公开 | 高：过程评价，小规模 |
| TRIGO | real 299/42/86 + 合成划分 | 论文正文确认真实与生成数据 | A，但仅形式化化简 | Lean；公开仓库不明确 | 中：形式验证参考 |
| UGMathBench | 全集 5,062；`Trigonometry/test` 当前 178 条 | 样本含周期、振幅、中线、正切周期、恒等式、反函数、方程和周期建模；也含勾股基础 | A+B，标签最清楚 | 文本；每题 3 个随机版本 | **最高：直接加载后重标注** |
| MATH | 12,500；Precalculus test 546 | Dataset Viewer 对 `\sin` 检索命中 203 条；row 431 为反三角函数与和差公式，row 364 为恒等化简 | A+B；Precalculus 内 A 丰富 | 文本，完整分步解 | 高：英文训练/测试题源 |
| MathOdyssey | 官方仓库 387 条；当前 HF Viewer 显示 389 条 | 官方为 2 条 Trigonometry + 47 条 PreCalculus；Viewer 对 `\sin` 命中 22 条，row 233 为精确三角函数值 | A+B | 文本；许可明确禁止用作训练集 | 高：较新隔离测试集 |
| CMM-Math | 本地/官方 28,069 条 | 高精度规则得到 499 个 A 类候选，81 个含图像引用；已抽查周期、相位、图像平移、方程根和周期建模 | A+B；官方 subject 不足以区分 | 中文图文；本地缺对应图像文件 | **最高：中文和多模态候选池** |
| MathVista | 6,141 | test 对普通 `sin` 命中 9 条；PID 3061 为 $\sin\theta\approx\theta$ 函数图像，PID 5434 为 $A\sin(\omega x+b)$ 图像读值 | 确认存在 A，也含 B | 图像+文本；test 答案受限 | 高：小规模函数图像测试 |
| MathVerse | 2,612 个原题、6 个视觉依赖版本 | testmini 对 `\sin` 命中 50 个版本；problem 630/row 3147 为 $y=5\sin x$ 首个最大点 | A+B | 图像+文本；多版本可诊断视觉依赖 | 高：视觉消融测试 |
| OlympiadBench | 8,476 | 英文 text competition `\sin` 命中 39，含直接方程；中文 text CEE 233、中文 MM CEE 378，但抽样多为解三角形/测量 | A+B，B 占比高 | 双语、文本+图像、详细解答 | 中高：困难集，必须二次分类 |
| MATH-Vision | 3,040 + 304 mini | test 中 `\sin` 19、`\cos` 17、`trigonometry` 0；抽样 subject 为 metric geometry-angle/length | 当前证据以 B 为主 | 图像+文本、竞赛题 | 低至中：A 类不应优先 |
| 本地 MultiMath function 子集 | 19,345 条 | 宽松三角关键词命中 736，714 含 `<image>`；严格/人工抽查只得到 2 个直接候选，且均为测量应用 B 类 | 几乎全为 B | 图像+中英文本、分步解 | 低：A 类；高：B 类视觉预训练 |

### 5.2 CMM-Math 本地初审

本地文件：`data/CMM-Math/all_data.jsonl`，共 28,069 条，其中 train 22,248、test 5,821。字段包括 `question`、`solution`、`answer`、`subject`、`level`、`image` 等。

本次使用“直接三角函数触发词 + 排除明显三角形/向量/极坐标语境”的高精度规则初筛，得到：

- 499 个 A 类候选；
- 81 个候选包含非空图像引用；
- 年级主要集中在高中二年级（433 条）和高中三年级（58 条）；
- 代表样本：ID 17824（单调区间）、17825（对称性与相位）、17845（图像平移与周期）、17859（周期与振幅）、17861（从图像推断 $A,\omega,\varphi$）、17871（摆的正弦模型）、17880（潮汐模型）、17823（选择 $y=-x\cos x$ 图像）、17805（由函数图像判断三角方程根）。

这些数字是**候选量，不是最终 gold 数量**。此外，本地目录只有 JSONL 和索引，没有题目引用的实际图片，因此若建设多模态子集，需要从官方发布补齐图像并校验文件映射。CMM-Math 的 `subject` 标签还存在“解析几何/度量几何”等粗分类，不能替代 A/B 人工标注。

### 5.3 本地 MultiMath 初审

本地文件：`data/multimath/multimath_function.json`，共 19,345 条，包含中英题目、图像、图像描述、考点和中英解答。

- 宽松检索“正弦/余弦/正切、sin/cos/tan、三角函数”等得到 736 条，714 条题面含图像标记。
- 逐字段和高精度规则审查后，直接候选只剩 2 条：管道包角和三角形土地面积；二者本质仍是测量/几何应用，属于 B 类。
- 大量命中考点是“锐角三角函数”“特殊角三角函数值”“解直角三角形”，而不是周期、振幅、相位、恒等式、三角方程或函数图像。

结论是：该本地 function 子集可支持 B 类图像解析和三角比知识迁移，但不适合作为 TDF 三角函数 A 类主数据。论文所称 MultiMath-300K 与当前 HF 页面展示的记录展开方式也不应和本地 19,345 条 function 子集混为一谈。

### 5.4 其他 benchmark 的可复现样本证据

- **MATH：** `precalculus/test` row 431 要求计算 $\sin(\arcsin 0.4+\arcsin 0.5)\sin(\arcsin 0.5-\arcsin 0.4)$；row 138 处理反三角函数主值；row 364 化简高次正余弦式。这些是明确 A 类。
- **MathOdyssey：** 官方仓库说明原始集合为 387 题，其中 Trigonometry 2 题、PreCalculus 47 题；当前 HF Viewer 却显示 389 行，且个别 `reasoning` 字段可见下一题文本拼接，使用前应以官方仓库重新校验。Viewer row 233（label `PreCal-3`）使用和角公式求 $\sin255^\circ$ 的精确值，说明仅看 2 条 Trigonometry 标签会漏掉 PreCalculus 中的 A 类题。
- **OlympiadBench：** `OE_TO_maths_en_COMP` row 268 直接求三角多项式方程的全部周期解，属 A 类；`OE_TO_maths_zh_CEE` row 500 和 `OE_MM_maths_zh_CEE` row 883 虽标作 `Trigonometric Functions`，但题目对象是三角形，属 B 类。
- **MathVista：** PID 5434 需要从图像读取 $f(x)=A\sin(\omega x+b)$ 的 $f(0)$，属于直接多模态 A 类。
- **MathVerse：** problem 630 的视觉强化版本要求由正弦图像变换确定 $y=5\sin x$ 的第一个最大点，属于直接多模态 A 类。
- **MATH-Vision：** row 2982 给定三角形图和 $\sin R$ 求 $\sin T$，row 186 由图求线段长；均属于 B 类。当前检索没有发现独立 Trigonometry 学科标签。
- **UGMathBench：** row 39 要求由表格求周期、振幅和中线；row 52 求 $2\tan(11\pi x/8-9\pi/10)$ 的周期；row 90 建立动物种群的正弦周期模型；row 143–159 覆盖恒等式和方程。这些直接覆盖 TDF 所需结构。

## 6. GitHub 与 Hugging Face 资源清单

| 资源 | 官方入口 | 可直接获得的内容 | 使用注意 |
|---|---|---|---|
| SSC-CoT | [zhao-zilong/ssc-cot](https://github.com/zhao-zilong/ssc-cot) | 方法代码、TriMaster100 | 检查许可；规模仅 100 |
| MATH | [hendrycks/math](https://github.com/hendrycks/math)、[HF mirror](https://huggingface.co/datasets/EleutherAI/hendrycks_math) | 题目、分步解、类别 | Precalculus 仍需 A/B 重标 |
| MathOdyssey | [官方 GitHub](https://github.com/protagolabs/odyssey-math)、[HF](https://huggingface.co/datasets/MathOdyssey/MathOdyssey) | 测试题与解答 | 官方条款禁止作为训练集；优先以 387 题官方仓库版本为准 |
| OlympiadBench | [OpenBMB/OlympiadBench](https://github.com/OpenBMB/OlympiadBench)、[HF](https://huggingface.co/datasets/Hothan/OlympiadBench) | 分类 JSON、图像、评测代码 | `subfield` 不能替代 A/B 分类 |
| MathVista | [lupantech/MathVista](https://github.com/lupantech/MathVista)、[HF](https://huggingface.co/datasets/AI4Math/MathVista) | 数据、元数据、评测代码 | test 答案不全部公开；保留 source/license |
| MathVerse | [ZrrSkywalker/MathVerse](https://github.com/ZrrSkywalker/MathVerse)、[HF](https://huggingface.co/datasets/AI4Math/MathVerse) | 六种视觉依赖版本、评测 | 同一原题的版本不得跨 split 泄漏 |
| MATH-Vision | [mathllm/MATH-V](https://github.com/mathllm/MATH-V)、[HF](https://huggingface.co/datasets/MathLLMs/MathVision) | 3,040 题、图像、评测 | 现有三角命中主要为 B 类 |
| MultiMath | [pengshuai-rin/MultiMath](https://github.com/pengshuai-rin/MultiMath)、[HF dataset](https://huggingface.co/datasets/pengshuai-rin/multimath-300k)、[HF model](https://huggingface.co/pengshuai-rin/multimath-7b-llava-v1.5) | 训练数据、模型、代码 | 官方 300K 名称、HF 展开行数和本地子集规模需分开记录 |
| CMM-Math | [HF dataset](https://huggingface.co/datasets/ecnu-icalk/cmm-math)、[EduChat-Math](https://github.com/ECNU-ICALK/EduChat-Math) | 中文图文数据、模型相关代码 | 本地副本缺图片；先补齐映射 |
| UGMathBench | [YangLabHKUST/UGMathBench](https://github.com/YangLabHKUST/UGMathBench)、[HF](https://huggingface.co/datasets/UGMathBench/ugmathbench) | 16 学科配置、三版本题目 | Trigonometry 内仍含 B 类基础题 |

## 7. 现有工作的主要不足

### 7.1 任务碎片化，尚无端到端 A 类覆盖

AutoTrig 和 TRIGO 从形式化表达式开始；SSC-CoT 从自然语言题开始但缺少符号完备性；综合 MLLM benchmark 强调视觉问答但不保证数学推导可靠。没有工作把“题面/图像解析—结构建模—策略选择—符号求解—完整周期解—可验证解释”统一起来。

### 7.2 A/B 混淆掩盖真实能力

多数数据把三角函数和三角形几何放在同一标签下。B 类可依赖图形长度、正弦定理或余弦定理；A 类则要求理解周期性、相位、主值、恒等变换和无限解集。若不重标，模型在 B 类上的表现会被误报为三角函数结构推理能力。

### 7.3 图像理解和数学求解没有解耦

现有多模态总分无法说明失败来自 OCR/曲线读取、坐标系理解、参数恢复，还是后续代数求解。MathVerse 的多视觉依赖版本提供了有用方向，但尚未形成面向三角函数图像的结构化 oracle 评价。

### 7.4 完整性和可验证性不足

三角方程的关键不是只给出一个根，而是给出满足定义域和角度制的完整周期解集；反三角函数还涉及主值分支；恒等式变换必须保持适用条件。LLM 的最终答案准确率不能检测漏分支、增根、周期参数错误或不等价变换。

### 7.5 数据结构过粗，过程标注不足

综合数据通常只有题面、图像、答案和自由文本解答，缺少可执行的中间表示，例如函数族、$A/\omega/\varphi/b$、定义域、周期、关键点、变换规则、方程分支和图像证据坐标。TRIGO 和 TriMaster100 有过程标注，但前者过度形式化、后者规模小。

### 7.6 数据污染与切分风险

MATH 等经典集合已被广泛用于训练；MathVerse 同题存在六个版本；合成恒等式容易在结构上重复。若按行随机切分，会产生模板或同题泄漏。需要按“原题/表达式骨架/函数参数模板”分组切分，并保留较新的隔离测试集。

## 8. TDF 可以形成的研究贡献

### 8.1 空白一：A 类三角函数的结构化统一表示

在现有 TDF/URM 框架上扩展三角函数表示，而不是把三角题当作普通自由文本。建议至少包含：

- `function_family`: sin/cos/tan/cot/compound；
- `amplitude`, `angular_frequency`, `phase`, `vertical_shift`；
- `domain`, `range`, `angle_unit`, `period`；
- `task_type`: property/graph/identity/equation/inequality/modeling；
- `solution_family`: 基本解、周期参数及 $k\in\mathbb Z$；
- `evidence`: 题干片段、图像坐标轴、关键点、极值点、零点和读取置信度；
- `transformation_trace`: 使用的恒等式、代换、因式分解和等价条件。

这能把 CMM-Math、UGMathBench、MATH、MathVista 和 MathVerse 的异构题面映射到同一求解接口。

### 8.2 空白二：神经解析 + 符号执行 + 完备性验证

建议保持 TDF 的“模型选择/模型执行”解耦：LLM/MLLM 负责识别题型、解析图像和提出结构；DIS/符号层负责恒等变换、方程求解和条件传播；验证器检查数值代回、等价性、分支覆盖和周期完备性。与纯 CoT 相比，这一贡献可以给出可复现的失败位置和更强的正确性边界。

### 8.3 空白三：面向多模态三角函数题的诊断式评测

建立两条互补轨道：

1. **Raw track：** 输入原始文字和图像，评价端到端性能；
2. **Oracle-URM track：** 输入人工校正的结构，评价纯求解性能。

再报告结构字段准确率、图像关键点误差、策略选择准确率、步骤合法率、最终答案、周期解集完备率和计算成本。Raw 与 Oracle 的差距直接量化解析瓶颈，避免把上游视觉失败误判为求解算法失败。

## 9. 推荐的数据建设与实验路线

### 阶段 1：复用数据形成候选池

1. 以 **UGMathBench-Trigonometry 的 178 条**建立英文主题骨架，先按 A1–A6 与 B 重标。
2. 从 **CMM-Math 的 499 个高精度候选**开始人工复核，补齐 81 个图像候选的官方图片。
3. 从 MATH-Precalculus、MathOdyssey 和 OlympiadBench 追加高难文本题；保留原始来源和许可。
4. 从 MathVista/FunctionQA 与 MathVerse 选择直接函数图像题，建立多模态核心测试集。
5. TriMaster100 用于过程级基线；TRIGO 用于形式化/规则级迁移；MultiMath 与 MATH-Vision 暂作 B 类或视觉预训练对照。

### 阶段 2：构建 TDF-Trig 结构化 gold set

建议先建设 500–1,000 道高质量题，而不是立即追求十万级规模。按以下六类平衡：

- A1 定义、值域、奇偶性、单调性与周期性；
- A2 图像、振幅、频率、相位和平移；
- A3 恒等式证明与表达式化简；
- A4 三角方程与完整周期解集；
- A5 三角不等式、参数与定义域；
- A6 周期现象和文字建模。

每题保留原题、来源、A/B 标签、模态、URM、标准步骤、最终答案、验证程序和图像证据；至少双人复核一部分数据，记录争议和修订。

### 阶段 3：建立不泄漏的评测

- 以原题 ID、表达式骨架和图像版本为 group 切分；MathVerse 六版本必须同组。
- 设置 in-distribution、参数外推、组合外推和新模板测试。
- 分别比较 CAS、纯 LLM/MLLM、LLM+CAS、TDF oracle、TDF raw。
- 对方程题使用集合等价/采样验证和符号验证，不只用字符串 exact match。

## 10. 对四个核心问题的明确回答

### 是否已经存在成熟的专用三角函数题 solver？

**没有。** 有成熟 CAS 的局部符号能力，也有 AutoTrig、TRIGO 和 SSC-CoT 这三类直接工作，但没有一个公开系统同时覆盖自然语言、图像、三角函数性质、恒等式、方程/不等式、周期解集和可验证解释。若把“专用 solver”限定为恒等式或形式化化简，已有原型；若按本调研的 A 类完整范围，仍是明显空白。

### 哪些数据集最适合提取或构建 TDF 三角函数子集？

推荐顺序为：

1. **CMM-Math + UGMathBench-Trigonometry：** 前者提供中文、高中和图像候选，后者提供明确的三角主题结构；最适合作为主体。
2. **MATH-Precalculus + MathOdyssey：** 补充英文高质量文本题和隔离测试。
3. **MathVista/FunctionQA + MathVerse：** 构建函数图像多模态核心测试。
4. **OlympiadBench：** 补充高难中英题，但必须剔除或单列 B 类。
5. **TriMaster100/TRIGO：** 作为过程级和形式化辅助集，而不是端到端主数据。

本地 MultiMath function 子集和 MATH-Vision 当前不宜作为 A 类主来源。

### TDF 最值得继续研究的 2–3 个空白是什么？

1. **统一的三角函数 URM 与 A/B 清晰数据集**：把周期、相位、图像证据和周期解集变成可执行结构。
2. **神经解析—符号执行—完备性验证的解耦求解器**：尤其解决分支、定义域、角度制和无限解集问题。
3. **raw/oracle 双轨的多模态过程评测**：分别量化图像/文本解析、策略选择和实际求解能力。

### 下一阶段应优先复用现有数据，还是自行构建结构化数据集？

**先复用题目，再自行构建结构化标注。** 公开数据足以避免从零搜题，但它们的标签和解答不足以直接支持 TDF。建议先用已有数据做 500–1,000 道去重、重标和可验证标注的 gold set；验证 URM 与 solver 后，再按覆盖缺口定向生成或采集新题。完全从零构题成本高且缺乏真实分布；直接拼接现有数据则无法解决 A/B 混淆、结构缺失和评测泄漏。

## 参考文献与官方链接

1. Hendrycks et al. [Measuring Mathematical Problem Solving With the MATH Dataset](https://arxiv.org/abs/2103.03874). NeurIPS 2021.
2. Liu et al. [Learning to Prove Trigonometric Identities](https://arxiv.org/abs/2207.06679). arXiv, 2022.
3. Xiong et al. [TRIGO: Benchmarking Formal Mathematical Proof Reduction for Generative Language Models](https://aclanthology.org/2023.emnlp-main.711/). EMNLP 2023.
4. Lu et al. [MathVista: Evaluating Mathematical Reasoning of Foundation Models in Visual Contexts](https://arxiv.org/abs/2310.02255). ICLR 2024.
5. He et al. [OlympiadBench: A Challenging Benchmark for Promoting AGI with Olympiad-Level Bilingual Multimodal Scientific Problems](https://arxiv.org/abs/2402.14008). ACL 2024.
6. Wang et al. [Measuring Multimodal Mathematical Reasoning with the MATH-Vision Dataset](https://arxiv.org/abs/2402.14804). NeurIPS 2024 Datasets and Benchmarks Track.
7. Zhao et al. [Stepwise Self-Consistent Mathematical Reasoning with Large Language Models](https://arxiv.org/abs/2402.17786). arXiv, 2024.
8. Zhang et al. [MathVerse: Does Your Multi-modal LLM Truly See the Diagrams in Visual Math Problems?](https://arxiv.org/abs/2403.14624). ECCV 2024.
9. Fang et al. [MathOdyssey: Benchmarking Mathematical Problem-Solving Skills in Large Language Models Using Odyssey Math Data](https://arxiv.org/abs/2406.18321). arXiv, 2024.
10. Peng et al. [MultiMath: Bridging Visual and Mathematical Reasoning for Large Language Models](https://arxiv.org/abs/2409.00147). arXiv, 2024.
11. Liu et al. [CMM-Math: A Chinese Multimodal Math Dataset To Evaluate and Enhance the Mathematics Reasoning of Large Multimodal Models](https://arxiv.org/abs/2409.02834). arXiv 2024；ACM MM 2025（以[官方仓库](https://github.com/ECNU-ICALK/EduChat-Math)标注为准）。
12. Xu et al. [UGMathBench: A Diverse and Dynamic Benchmark for Undergraduate-Level Mathematical Reasoning with Large Language Models](https://arxiv.org/abs/2501.13766). ICLR 2025.
13. SymPy. [Solvers / solveset documentation](https://docs.sympy.org/latest/modules/solvers/solveset.html).
