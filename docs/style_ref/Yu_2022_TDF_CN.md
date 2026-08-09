# A relation-centric algorithm for solving text-diagram function problems


# Abstract:

A tutorable algorithm for solving text-diagram function (TDF) problems is an essential technology for building the humanoid tutorial service since "function" is a core portion of mathematics. Solving TDF problems encounters challenges in understanding diagrams, representing the functions of being compound objects, and solving the mixture group of functions and universal relations. To address these challenges, this paper proposes a relation-centric algorithm, leveraging on making breakthrough in handling function, understanding diagram, and generating tutorable solution. The proposed algorithm comprises two phases: problem understanding and symbolic solver. In the problem understanding, it proposes a S2P (Syntax Semantics with Period) model method of acquiring relations from text and a  L2 (Line Segment with Labels Pattern) model method of acquiring relations from diagrams. To get the problem fully understood, this phase acquires both universal relations and period relations. In the symbolic solver, the function is first built from the acquired relations. Then an equation-function interaction method is created to solve a mixture system of relations and functions. The developed algorithm is the first one for solving text-diagram function problems. Experimental results show that the proposed algorithm not only has high accuracies of 74.5% on Math23KtoF and 80.8% on TnD1K datasets, but also can produce the tutorable solutions of TDF problems.

摘要：解决文本-图表函数（TDF）问题的可教学辅导算法是构建拟人教学辅导服务的关键技术，因为“函数”是数学的核心部分。解决TDF问题遇到理解图表、表示复合对象的函数以及解决函数和全局关系混合群的挑战。为了应对这些挑战，本文提出一种关系中心算法，通过突破处理函数、理解图表和生成可教学辅导求解方案来实现。该算法包括两个阶段：问题理解和符号求解器。在问题理解阶段，它提出了从文本中获取关系的 S2P（语法语义与 区间）模型方法和从图表中获取关系的 L2（带标签的线段模式）模型方法。为了全面了解问题，该阶段获取全局关系和区间性关系。在符号求解器中，首先从获取的关系中构建函数。然后创建一个方程-函数交互方法来解决关系和函数的混合系统。该算法是用于解决文本-图表函数问题的首个算法。实验结果显示，该算法不仅在Math23KtoF数据集上具有74.5％的高准确率，而且在TnD1K数据集上具有80.8％的高准确率，并且能够产生TDF问题的可教学辅导求解方案。




# 3. Solving principle

准备一个适当的原则是开发具有所需属性的求解算法的关键步骤。本文决定采纳求解数学问题的关系原理（relation principle）的基本思想。然而，Yu等人(2019，2022)提出的求解问题的关系原理并不包括构建函数所需的关系。因此，在问题陈述之后，我们准备了一个广义的关系原理。

## 3.1 Problem statement

本文的目标是开发一个以关系为中心的算法来解决TDF问题，因为关系为中心的方法具有所需的特性。因此，我们有以下问题陈述。
**Problem statement**：设 C 是一个包含TDF问题的语料库。本文的研究问题是开发一个满足以下条件的关系为中心的算法 $\text{Æ}$：（1）能够解决尽可能多的 C 中的问题；（2）能够进行教学。

## 3.2 Generalized relation principle

本节给出了一组定义，以建立求解TDF问题的广义关系原理的核心概念。

**Definition 1** (*Relation*). 关系是一个可量化实体的方程表达式，其中可量化实体可以是数字、变量或描述数量的短语。

**Definition 2** (*Period relation*). 区间性关系是一种具有区域修饰符的复合关系，该修饰符给出自变量的域。这里区间限制用于限定数学关系的适用范围。无区域限制修饰符的关系表示其自变量的域为 $(-\infty, \infty)$，即为全局关系。

**Definition 3** (*Compound relation*). 复合关系是一种复合对象，可以用一批相关的区域性关系和全局关系来描述。

分段函数是一个复合对象，可以通过复合关系来描述。
与现有的许多算法类似，所提出的算法包括问题理解和符号求解器两个阶段。求解算法产生的中间结果也被称为问题状态（states)。下面所定义的理解状态是其中一个关键状态。

**Definition 4** (*Understood state*)：如果符号求解器可以从该状态生成求解方案而无需重新访问给定问题，则该状态称为给定问题的理解状态。

**Generalized relation principle** （**广义关系原理**）:一个求解算法包括两个阶段：问题理解和符号求解器。问题理解旨在获得一组区间性关系作为其理解状态，而符号求解器用于解决这组区间性关系，以获得给定问题的答案和求解方案。

下面我们将使用关系（关系原理）来同时表示关系和区间性关系（原理和广义关系原理）以简化写法。

**Proposition 1**. 设 P 是 C 中的一个TDF问题。那么存在一组关系，表示为 $\text{Œ} = \left\{r_{i}: i=1, \ldots, k\right\}$，它是P的理解状态。
（到目前为止，对命题1的理论证明尚不可用，但是在第6节的实验结果将证明其正确性。）

## 3.3 Function model

在中学数学的习题中，函数是一种特定类型的函数。为了设计解决这种类型的 TDF 问题的算法，我们识别了它们的共同特性，并定义了一些符号来描述方法和算法。

**Observation 1 (Function properties)**. 大多数基础教育中的 TDF 问题中的函数具有以下三个特性。它们是：（1）单变量（一一对应）；（2）连续；和（3）分段线性。由于函数是分段的，一组分段模型构成一个函数。由于分段模型是主要对象，我们在下面对其进行定义。

**Definition 5** (*Piece model*). 函数段模型是描述函数组件的数据模型。设 $\text{ƥ}=\left\{x, y, k, b,\left[x_{1}, x_{2}\right]\right\}$ 是一个函数分段模型，其中的自变量 $x$，因变量 $y$、起点 $s$,、终点 $e$、斜率 $k$、截距 $b$ 和阈值范围 $[x1, x2]$ 为函数基本元素。

**Definition 6** (*Function model*). 函数模型是描述函数的数据模型，表示为 $\text{Ӻ}$ ，$\mathrm{F}=\left\{\mathfrak{p}_{i}: i=1,2, \ldots, k\right\}$。

因为一个连续的分段函数由一组相连的线段组成；两个连续的线段有一个连接点。这里把连接点称为转折点，因为函数的方向在此处发生变化。上述定义和讨论实际上解释了区间性关系如何构成函数段和函数。换句话说，它们解释了 命题1 的正确性。

## 3.4 Significance of the research

这项研究具有三个重要意义，具体如下所述：
(1) 该研究创新性地提出了一种处理复合对象“函数”的方法，从而扩展了可解问题的范围。为了处理函数，它创建了一个复合对象来存储函数，提出了区间性关系来表示函数的元素，并提出了方程-函数交互来解决方程和函数的混合组。
(2) 该研究创建了一个 L2 模型方法，用于理解图表，从而将可解问题的范围从仅文本函数题目扩展到文本-图表函数题目。
(3) 该研究提供了输出可教学求解方案的潜力。这个潜力在于算法采用了以关系为中心的方法。该方法通过操作关系来解决TDF问题，以便学生可以理解算法解决过程。



# 4. The method of solving TDF problems

## 4.1. S2P model method for text understanding

正如所指出的，本文中的函数是分段的。因此，描述这些函数的关系是具有 区间修饰符的关系。为了处理函数的新对象，我们将 S2 模型方法改进为 S2P 模型方法。因此，S2 模型演化为 S2P 模型。

**Definition 7**（*S2P 模型*）。S2P 模型是一个三元组 $M=(K, P, R)$，其中K表示变量部分或函数元素的关键词，P是POS（词性）的变化模式，R是区间性关系。

与Yu等人（2019）定义的 S2 模型相比，该定义扩展了R的范围。S2P 模型方法提供了一种从函数问题文本中获取知识项的机制。

**（1）S2P 模型池**
本节准备了一个 S2P 模型池，表示为 $\Omega$。首先，它继承了在Yu等人（2022）中准备的S2模型池，表示为 $\Omega_{0}$，以提取全局关系。接着，它添加了一个 S2P 模型池，表示为 $\Omega_{1}$，以提取用于构建函数的关系。因此，$\Omega=\Omega_{0} \cup \Omega_{1}$，其中 $\Omega_{1}$ 被分为三个类别：$\Omega_{11}, \Omega_{12}, \Omega_{13}$。

类别1：用于函数变量对的S2P模型，用 $\Omega_{11}$ 表示这些模型的集合。
自变量和因变量是TDF问题中函数的主要元素。因此，建立了一批 S2P 模型来识别以各种方式表述的函数的自变量和因变量。表 1 列出了 11 个用于抽取函数变量关系的 S2P 模型及其示例，以说明每个模型如何工作。函数变量的具体形式，对于模型1到模型2，可以直接从的函数变量对中识别出来；对于模型3到模型8，它们的变量对则由语法模式确定；而剩下的模型使用默认的变量对 $< x, y >$。

表1. 获取函数变量对关系（即 $\Omega_{11}$）的 S2P 模型列表及其对应示例

![](images/Yu_2022_TDF_Table1.png)

类别2：用于函数参数的 S2P 模型，使用 $\Omega_{12}$ 表示这些模型的集合。
函数参数的S2P模型具有函数参数的特定符号和特定函数领域术语的集合，包括系数 $k$，$b$，函数的域 $[x1, x2]$。这些模型使用符号和表达式作为文本匹配的锚点。

类别3：用于函数点的S2P模型，使用 $\Omega_{11}$ 表示这些模型的集合。
针对初级代数中出现的函数点表述类型，函数点 S2P 模型以坐标形式匹配文本或使用某些术语的文本。第一种表达方式的模型从其公式样式进行了分析。至于第二个，它们的语义部分来自于它的特定术语，如以 "\*" 开头"、以 \*" 结尾"（其中 "\*" 表示一个点）、"y-斜率"等。

因此，我们有：$\Omega_{1}=\Omega_{11} \cup \Omega_{12} \cup \Omega_{13}$ 

**（2）使用 S2P 模型提取关系**

S2P 模型方法使用 $\Omega$ 模型池来从问题语料库的文本中提取一组关系。如 **Procedure I** 所示，使用 S2P 模型进行文本理解分为两个阶段。

Procedure1: Acquiring relations from text   

![](images/Yu_2022_TDF_Procudure1.png)  

第一阶段是使用 $\Omega_{0}$ 提取全局关系。第二阶段识别函数变量对$(x, y)$，然后确定每个关系的自变量的 区间。类似地，通过将文本与 $\Omega_{12}$ 和 $\Omega_{13}$ 进行匹配，获取其他区间性关系。图1演示了Procedure I如何从文本中提取全局关系和区间性关系。

![](images/2d8b044668316878cdbdbd6782bf8c31325dfde91335ed040aad5a4290d0c9bd_56.jpg){width=56%}

图1. 使用 S2P 方法理解文本的过程。这里的字符分别代表：$n$-名词、$p$-代词、$v$-动词、$m$-数字、$q$-单位、$w$-标点符号、$W_f$-函数关键词、$s$-符号。

## 4.2 Understanding diagram

在TDF问题中，准备了三个 L2 模型，用于从图示中提取关系。然后，我们设计了一个过程来从这些图示中挖掘关系。

**（1）用于函数段模式的 L2 模型**
为了获得用于构建由图示所描述的函数的关系，引入了三个 L2 模型。这里我们使用 $\Omega_{2}$ 来表示这三个模型的集合。

**Definition 8** ( *L2 model*)。一个 L2 模型 $S = \{W, R\}$ 给出了图示中线段布局和描述函数段部分的标签的捕捉，$\mathscr{G}$ 表示线段和坐标轴的布局，$\mathscr{R}$ 是图示上下文中的关系。

根据图示中元素的布局，定义了三个 L2 模型来理解图示：第一个直接与原点相连，另一个与坐标轴通过相应的标签相连，最后一个与X轴平行。相应的关系列在 表2 中。

表2. $\Omega_{2}$ 中的 L2 模型。$\mathscr{G}, \mathscr{D}, \mathscr{R}$ 分别代表 L2 中的图形模型（G），图形模式的简要描述（D），和模型中的关系（R）

![](images/Yu_2022_TDF_Table2.png)

**（2）使用 L2模型提取关系**
利用向量化形式的图表（De等人，2017）基于 L2模型提取关系。图表中的函数块与提出的三个 L2模型进行匹配。当一个函数块满足模型的模式时，它获取模型的相应关系，并通过在坐标系中的标签或引入新的变量来实例化这些关系。

![](images/a360fb5b6890ec844f1ed99d47ba2729ddb456218c40e767e174b92023bbf1e9_45.jpg){width=45%}

图2. 从图示中提取关系的过程。(a) 是带有函数线段的图；(b) 和 (c) 分别是 $\Omega_{2}$ 中与模型1和模型3匹配后的函数分段及其代数关系

例如，如图2所示，函数图由坐标平面中的两个连续实线段组成。由于piece 1从原点开始，它满足第一个 L2模型。然后提取以下关系：“$b = 0$”，“$6 = k * x_2$”，“$y = k * x\ ,\ x \in [0, x_2]$”。由于缺少端点标签，引入变量x2。此外，通过参考最近邻节点获得x2的范围，得到关系 $0 < x_2 < 9$。同样，可以获得piece 2的关系。

Procedure II: Acquiring relations from diagram

![](images/Yu_2022_TDF_Procudure2.png)

## 4.3 Symbolic solver

如 Procedure III 所示，符号求解器以理解状态 $R$ 作为输入，其中包括 $R_T$ 和 $R_D$。Procedure III 有三个阶段，前两个是生成混合关系，包括区间方程和全局方程。特别地，在第二阶段中构建了一个函数。最后一个阶段通过方程-函数交互法解决混合关系组。

ProcedureIII: Generating and solving the mixture relations   

![](images/Yu_2022_TDF_Procudure3.png)

生成混合关系的过程从实例化关系组 $R$ 开始，然后在函数模型中组合函数元素关系 Rf的关系来构造函数 $f$。

**（1）实例化关系组**

为了实例化 $R$ 中的关系，执行以下三个操作：

* 列出问题理解关系中出现的所有实体，并声明与其对应的变量列表；
* 创建一个相应的表 $L(O, S)$ 和变量的域；
* 并通过查找表进一步用指定的变量更新 $R$，并将它们转换为全局关系形式（例如：$k_{1} * x_{1}=6$）或区间关系形式（$k=0, \ x \in\left[x_{1}, 9\right]$）

**（2）建立函数关系**

此外，建立函数的方法是利用获得的关系实例化一般函数模型。它根据区间将与函数相关的关系 $R_f$ （即由新建立的函数指定的S2P模型提取的关系和从函数段提取的关系）重组成不同的函数分段。对于每个函数分段，它的关系要么是关于 $x, y$，或者是 $f_i$ 的参数。（在本研究中，默认的函数解析表达式形成为 $y=k_{i} * x+b_{i}, \ x \in [x_1, x_2]$ ，$k_{i}, b_{i}, x_{1}, x_{2}$ 是函数参数）。因此 $f$ 是通过在自变量域的增加序列中对所有 $f_i$ 进行排序来构造的。

**（3）求解混合关系组**

构建函数后的状态由新更新的关系组 $R$ 和函数 $f$ 组成，该函数由区间性关系的复合关系组成，称为混合关系组。显然，要解决混合关系组，就要面对何时以及如何使用函数关系的问题。

方程-函数交互方法主要是通过交替两种类型的交互来解决混合关系组：**情况1** 是与方程交互，即在全局方程和区间方程之间进行等价转换；**情况2** 是与函数交互，即对函数进行操作。

该方法的具体过程如下：根据变量和方程之间的关系，重复将混合关系划分为线性组 $G_1$ 和非线性组 $G_2$，使用消元法求解 $G_1$ 中的变量；然后用获得的结果更新 $G_2$，直到无法解决任何变量。然后，当确定一个变量与一个函数有关时，通过查找函数片段的参数或与函数片段计算来进行 **情况2** 的处理。



# 5. The proposed algorithm

## 5.1 The component structure

Proposition 1 表明，TDF问题具有一个理解状态，即一组关系。基于这一事实，我们首先提出了从文本和图表分别获取这些关系的方法。然后，我们构建了一个符号求解器，用于解决这组关系（这些关系可以构建函数），并可以使用它来找到解。图3展示了解决TDF问题的主要组件的结构。

![](images/a3143dbb2abb26a6c88719a41c3b0dc9a3fce39f7763f7f4e2d20c80c0cb9b77_70.jpg){width=70%}

图3. 用于解决TDF问题的主要组件的结构。实心框表示本文中要开发的组件；虚线框表示相应组件的动作。

## 5.2 The relation-centric algorithm

**Algorithm I** 是解决TDF问题的提出算法，它包含三个步骤。第一步是问题理解。**Procedure I** 进行文本理解，**Procedure II** 进行图表理解。第二步，使用 **Procedure III** 解决混合关系问题。第三步，生成并输出一个求解方案，包括求解操作、相应状态和 TDF 问题的答案。

![](images/Yu_2022_TDF_Algorithm1.png)



# 6. The application of Algorithm I

本节首先通过一个例子来说明所提出的算法的工作方式，然后展示所提出算法是可教学的。

## 6.1  Solving a TDF problem by Algorithm I

图4 展示了使用 **Algorithm I** 解决一个示例问题的过程。整个解决过程包括三个步骤。

![](images/6b0334b68b9a32a908151612cfbc3fe09cb98c55b174d5f3c0ef41989267ed99_70.jpg){width=70%}

图4. 用算法I求解TDF问题的过程。

* **Step 1：理解文本和图表**

给定的问题包括一个文本部分和一个图表。问题文本被解析并用关键词和POS进行标注，然后算法使用 $\Omega_{0}$ 和 $\Omega_{1}$ 中的模型提取关系。因此，理解文本的过程获取了关系 $\mathbf{r_1, r_2, r_3, r_4, r_5}$。我们以获取 $\mathbf{r_1}$ 作为例子解释如何进行获取关系。当确认 “ $n\ m\ q$ ” 同时出现在 $\Omega_{0}$ 和第一个语句的注释中时，我们可以得出结论： $\Omega_{0}$ 中的模型 “ $n\ m\ q$ ” 与第一个语句相匹配。因此，获取了关系 $\mathbf{r_1}:\ \text{volume} = 6 * \text{liters}$。值得注意的是一个特殊情况， $\Omega_{0}$ 中的一个模型和  $\Omega_{1}$ 中的另一个模型都匹配了 “"1.2 liters per minute”。因此，这个短语引出了一个全局关系 $\mathbf{r_6}$ 和一个函数元素关系 $\mathbf{r_7}$。

在图表理解方面，图表分析过程发现了两个分段。对于分段 1，它与第一个模型相匹配，并通过标记的数字实例化其关系。因此，获取了关系 $\mathbf{r_7, r_8, r_9, r_{10}, r_{11}, r_{12}}$。对于分段 2，获取了关系 $\mathbf{r_{13}}$ 和 $\mathbf{r_{14}}$。

从文本和图表中获取的所有关系包含全局关系 $\mathbf{r_1, r_2, r_3, r_4, r_6}$ 和区间性关系 $\mathbf{r_5, r_7, r_8, r_9, r_{10}, r_{11}, r_{12}, r_{13}, r_{14}}$。

* **Step 2：符号求解器**

更新函数变量、实体和单位后，得到关系 $\mathbf{r_8}$。相应地，通过分配变量，更新了关系 $\mathbf{r_1}$ 至 $\mathbf{r_{13}}$，例如： $\mathbf{r_1}:\ \text{a} = 6 * \text{liters}$；$\mathbf{r_3}: \ \text{b} = 7 * \text{minutes}$；$\mathbf{r_5}:\ X = f(7 * \text{minutes})$；$\mathbf{r_7}:\ k_1 = 1.2 * \text{liters/minute}$。

然后通过组合两个函数分段来获取函数 $f$。对于函数分段 1，函数元素的关系是 $\mathbf{r_7, r_9, r_{10}, r_{11}, r_{12}}$。类似地，对于函数分段 2，它具有关系 $\mathbf{r_{13}}$ 和 $\mathbf{r_{14}}$。

在解决混合关系组时，通过解决线性组部分推导出了函数 $f$ 的参数，并更新了 $f$，表示为 $\mathbf{r_{11}}:\ y = 1.2 * x,\ x \in [0, 5]$；$\mathbf{r_{14}}:\ y = 6, \ x \in [5, 9]$。$X$ 的关系来自函数 $f$ 中的一个函数点，即 $\mathbf{r_5}:\ X = f(7 * \text{minutes})$。然后它与 $f$ 进行交互。通过比较函数分段的定义域，确定 $(7, X)$ 属于函数分段 2，并得到答案 $\mathbf{r_{15}}$。

* **Step 3：生成求解方案**

最后，通过组织上述两个步骤中提到的操作及其结果，生成一个可教学的求解方案。例如，在理解文本过程中，它生成了以下操作和更新状态的结果。

（**Action** $\rightarrow$ 将模型 $\Omega_{0}$ 和 $\Omega_{1}$ 与语句进行匹配，**Result** $\rightarrow$ 从语句1获取的关系 $\mathbf{r_1}$，...，从语句2获取的关系 $\mathbf{r_6}$），

在理解图表后：
（**Action** $\rightarrow$ 将函数分段与 $\Omega_{2}$ 中的模型匹配，**Result** $\rightarrow$ 获取分段 1中的关系 $\mathbf{r_8, r_9, r_{10}, r_{11}, r_{12}}$，以及分段 2中的关系 $\mathbf{r_{13}}$ 和 $\mathbf{r_{14}}$）

在构建函数后：
（**Action** $\rightarrow$ 通过不同的函数分段来分组关系，**Result** $\rightarrow$ 分段 1中的关系： $\mathbf{r_7, r_9, r_{10}, r_{11}, r_{12}}$，以及分段 1中的关系： $\mathbf{r_{13}}$ 和 $\mathbf{r_{14}}$）

在解决混合关系时：
（**Action** $\rightarrow$ 解决混合关系组的线性部分，**Result** $\rightarrow$ “$x_1 = 5$”）；
（**Action** $\rightarrow$ 使用 $f$，**Result** $\rightarrow$ “ $\text{ans} = 6 * \text{liters}$ ”）。

## 6.2 Tutorable solution of the proposed algorithm

**Proposition 2**. Algorithm I 为TDF问题提供了可教学的求解方案。

我们首先讨论了一个求解方案可教授的标准，然后通过证明所提出算法产生的求解方案符合这些标准来证明命题2。
Murray等人（2004）在其论文中认为，教学辅导的主要任务可以看作是决定要采取的行动以及由行动引起的状态改变。Faldu等人（2021）中指出，数学推理的可解释性是解决问题的关键因素。基于以上讨论，可教授的算法必须满足两个条件。第一个条件是一系列连续的行动和生成的状态。第二个条件是所有解决步骤及其推理对学习者能够理解。
在这里我们通过展示算法I满足上述两个条件来证明它是可教授的。
（1）所提出的问题理解方法使学习者聚焦于问题文本或图表中仅有的一些信号。通过使用S2P模型方法，通过识别基于相关事实（即句法和语义信息）的匹配模型来提取语句之间的关系。在图表理解中，强调的是如何逐个获取函数片段。获取函数片段的任务是使用 L2 模型将两个或三个函数元素进行匹配。因此，我们可以看到，文本理解和图表理解是事实识别步骤，因为它们包含学习者可以直接从问题中收集到的信息，这对学习者来说是容易跟随的。
（2）通过从定义5和定义6中引出因果关系的解释，建立函数的过程是将函数片段组装在一起，这使得学习者能够学习。在本研究中，从文本和图表中推导出的关系重新组织函数片段是一个明确的过程。
（3）解决混合关系组是一个关系转换的过程。它从解决线性方程开始，然后选择在输入问题的当前状态上进行操作的行动，并以一个转化后的状态结束。这些转换遵循等价关系的原则。ðAction；StateÞ的模式支持因果推理。在此基础上，算法I可以为解决混合关系组生成一个可解释的推理路径。

