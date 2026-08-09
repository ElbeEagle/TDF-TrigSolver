# A relation-centric algorithm for solving text-diagram function problems  


# ABSTRACT  

A tutorable algorithm for solving text-diagram function (TDF) problems is an essential technology for building the humanoid tutorial service since "function" is a core portion of mathematics. Solving TDF problems encounters challenges in understanding diagrams, representing the functions of being compound objects, and solving the mixture group of functions and universal relations. To address these challenges, this paper proposes a relation-centric algorithm, leveraging on making breakthrough in handling function, understanding diagram, and generating tutorial solution. The proposed algorithm comprises two phases: problem understanding and symbolic solver. In the problem understanding, it proposes a $S^2P$ (Syntax Semantics with Period) model method of acquiring relations from text and a $L^2$ (Line Segment with Labels Pattern) model method of acquiring relations from diagrams. To get the problem fully understood, this phase acquires both universal relations and period relations. In the symbolic solver, the function is first built from the acquired relations. Then an equation-function interaction method is created to solve a mixture system of relations and functions. The developed algorithm is the first one for solving text-diagram function problems. Experimental results show that the proposed algorithm not only has high accuracies of 74.5% on Math23KtoF and 80.8% on TnD1K datasets, but also can produce the tutorial solutions of TDF problems.  

Keywords: Relation-centric algorithm Symbolic solver Syntax semantics model with period Diagram understanding  

 

# 3. Solving principle  

Preparing a proper principle is a critical step for developing a solving algorithm with the desired property. This paper decides to absorb the basic idea of the relation principle of solving problems. However, the relation principle of solving problems presented in Yu et al. (2019, 2022) does not include the relations for building functions. Therefore, we prepare a generalized relation principle below after the problem statement.  

# 3.1. Problem statement  

The objective of this paper is to develop a relation-centric algorithm for solving TDF problems since the relation-centric approach has desired characteristics. As such, we have the following problem statement.  

Problem statement: Let $C$ be a corpus of TDF problems. The research problem of this paper is to develop a relation-centric algorithm $\mathcal{E}$ satisfying that (1) it can solve the problems in $C$ as many as possible; and (2) it is tutorable.  

# 3.2. Generalized relation principle  

A set of definitions are given to build the core concepts of the generalized relation principle of solving TDF problems.  

Definition 1 (Relation). A relation is an equation expression of quantifiable entities, where a quantifiable entity can be a number, a variable, or a phrase describing a quantity.  

Definition 2 (Period relation). A period relation is a relation with a period modifier giving the domain of independent variables.  

Here a period is used to tell the range that the corresponding relation is applicable. The relation without period modifier means that the domain of its independent variable is $(-\infty, \infty)$, so also called as universal relation.  

Definition 3 (Compound relation). A compound relation is a compound object that can be described by a batch of related period relations and universal relations.  

A piece-wise function is a compound object, and it can be described by a compound relation.  

Like many of the existing algorithms, the proposed algorithm comprises two phases of problem understanding and symbolic solver. The intermediate results produced by a solving algorithm are also called problem states. The understood state defined below is one of the critical states.  

Definition 4 (Understood state). A state is called as an understood state of a given problem if a symbolic solver can produce the solution from this state without revisiting the given problem.  

Generalized relation principle: A solving algorithm comprises two phases: problem understanding and symbolic solver. Problem understanding is designed to acquire a group of period relations as its understood state, and symbolic solver is set to solve the group of period relations for getting the answer and the solution of a given problem.  

Hereafter we will use relation (relation principle) to indicate both relation and period relation (principle and generalized relation principle) for simplicity when no confusions occur.  

Proposition 1. Let P be a TDF problem in C. Then there is a group of relations denoted as $\mathbb{E}=\{r_i:i=1,\ldots,k\}$ such that it is an understood state of P.  

A theoretical proof for Proposition 1 is not available so far, but the experimental results in Section 6 will testify its correctness.  

# 3.3. Function model  

The functions in exercise problems in the secondary mathematics are a specific kind of functions. In order to design the algorithm for solving such kind of TDF problems, we identify their common properties and define some notations to be used in presenting the methods and the algorithms.  

Observation 1 (Function properties). Most of functions in TDF problems in basic education possess the following three properties. They are: (1) single variable (one-to-one correspondences); (2) consecutive; and (3) piece-wise linear. Since functions are piecewise, a set of piece model constitute a function. Since piece model is the main object and we define it below.  

Definition 5 (Piece model). A piece model is a data model that describes function pieces. Let $\beta=\{x,y,k,b,[x_1,x_2]\}$ be a piece model, whose elements represent the independent variable and the dependent variable, slope, intercept and domain ranges, respectively.  

Definition 6 (Function model). A function model is a data model of describing functions, denoted as f, then $f=\{\hat{p}_i:i=1,2,\ldots,k\}$.  

Since a continuous piece-wise function consists of a group of connected line segments; two consecutive segments have a joint point. We call a joint point as a turning point because the direction of function turns at it. The above definitions and discussions actually explain how the period relations can constitute function pieces and functions. In the other words, they explain that Proposition 1 is correct.  

# 3.4. Significance of the research  

This research has triple significances, further explained as follows.  

(1) This research innovates a method to handle the compound object 'function' so that it extends the scope of the solvable problems. To handle the function, it creates a compound object to store the function, proposes the periodic relation to express elements of function, and proposes the equation-function interaction to solve the mixture group of equations and functions.

(2) This research creates a $L^2$ model method to understand diagrams so that it can extend the scope of solvable problems from text-only function problems to text-diagram function problems.  

(3) This research provides a potential of outputting the tutorable solution. This potential lies in that the algorithm adopts the relation-centric approach. This approach solves TDF problems through operating relations so that the students can understand the algorithmic solving process.  

# 4. The method of solving TDF problems  

# 4.1. $S^{2}$P model method for text understanding  

As pointed out, the functions in this paper are piece-wise. Consequently, the relations describing these functions are the relations with period modifiers. To cope with the new objects of function, we enhance $S^{2}$ model method into $S^{2}P$ model method. Accordingly, $S^{2}$ models evolve into $S^{2}P$ models.  

Definition 7 ($S^{2}P$ model). A $S^{2}P$ model is a triplet $M=(K,P,R)$, where $K$ represents a keyword of variable parts or function elements, $P$ is a change pattern of POS (parts-of-speech), and $R$ is a period relation.  

Compared with the $S^{2}$ model defined in Yu et al. (2019), this definition extends the scope of $R$. $S^{2}P$ model method provides a mechanism for acquiring the knowledge items from function problem text.  

# (1) The pool of $S^{2}P$ models  

This section prepares a pool of $S^2P$ models, denoted as $\Omega$. First of all, it inherits the pool of $S^2$ models prepared in Yu et al. (2022), denoted as $\Omega_0$, to extract universal relations. It adds a pool of $S^2P$ models, denoted as $\Omega_1$, to extract the relations for building functions. As such, $\Omega = \Omega_0 \cup \Omega_1$. $\Omega_1$ are divided into three categories $\Omega_{11}$, $\Omega_{12}$, $\Omega_{13}$.  

Category 1: $S^{2}P$ models for function variable, using $\Omega_{11}$ to denote the set of such models.  

An independent variable and a dependent variable are the main elements of a function in TDF problems. Hence, a batch of $S^{2}P$ models is built to identify the independent variable and the dependent variable of function which are stated in various ways. Table 1 lists this batch of $S^{2}P$ models and it also gives an example to illustrate how each model works. The specific form of function variables can be directly identified from the pair of function variables in model 1 to model 2; as for model 3 to model 8, their variable pairs are determined by syntax patterns; while the remaining models use the default variable pair <x,y>.  

Category 2: $S^{2}P$ models for function parameter, using $\Omega_{12}$ to denote the set of such models.  

The $S^{2}P$ models for function parameters have a collection of specific symbols and specific function terms for function parameters, including coefficients $k$, $b$, domain of a function $[x_{1}, x_{2}]$. The models use symbols and expressions as anchors for text matching.  

Category 3: $S^{2}P$ models for function points, using $\Omega_{13}$ to denote the set of such models.  

$S^{2}P$ models for function point match the text in the form of coordinate or the text of using some fixed terms. Models for the first expression way is analyzed from its formula styles. As for the second one, their semantic parts are from its specific terms, such as "beginning with **", "with the end of **" (where "**" expressing a point), "y-interpreter", etc.  

Hence, we have $\Omega_{1}=\Omega_{11}\cup\Omega_{12}\cup\Omega_{13}$.  

(2) Extracting relations using the $S^{2}P$ models  

$S^{2}P$ model method uses the pool of $\Omega$ to extract a group of relations from text for a corpus of problems. As depicted in Procedure I, text understanding of using $S^{2}P$ models is divided into two stages. The first stage is to extract universal relations with $\Omega_{0}$. The second stage identifies the function variable pair $(x,y)$ and then it derives the period for the independent variable of each relation. In a similar way, it acquires other period relations by matching text with $\Omega_{12}$ and $\Omega_{13}$. Fig. 1 illustrates how Procedure I extracts universal relations and period relations from text.  

Procedure1: Acquiring relations from text   

![](images/Yu_2022_TDF_Procudure1.png)  

# 4.2. Understanding diagram  

Three $L^{2}$ models are prepared to extract relations from diagrams in TDF problems. Then, we design a procedure to mine relations from these diagrams.  

(1) $L^{2}$ models for function piece patterns  

To obtain relations for building the function described by diagram, three $L^{2}$ models are introduced. Here we use $\Omega_{2}$ to denote the set of these three models.  

Definition 8 ($L^{2}$ model). A $L^{2}$ model $\mathcal{S}=\{W,R\}$ gives the captures of the layout of a line segment and the labels of describing the function piece in diagram, $\mathcal{G}$ represents the layout of the line segment and the coordinate axis. $\mathcal{R}$ is the relations from the context of the diagram.  

Three $L^{2}$ models are defined for diagram understanding according to the layout of the elements in diagram, the first one is directly connected with the origin, another is linked with the coordinate by the corresponding labels, and the last one is parallel to the X-axis. The corresponding relations are listed in Table 2.  

(2) Extracting relations using $L^{2}$ models  

$L^{2}$ models are utilized to extract the relations based on the vectorized form of diagrams (De et al., 2017). Function pieces in diagrams are matched with the proposed three $L^{2}$ models. When a function piece satisfies the pattern of a model, it acquires the corresponding relations of the model, and further instantiates these relations either with the labels in the coordinate or by introducing new variables.  

For instance, as shown in Fig. 2, the function graph is consisted of two continuous solid segments in a coordinate plane. Since piece 1 starts from the origin point, it satisfies the first $L^2$ model. Then the following relations, "$b=0$", "$6=k*x$", "$y=k*x$ & $x\in[0,x_2]$" are extracted. As the endpoint label is missing, a variable $x_2$ is introduced. Besides, the range of $x_2$ is further obtained by referring to the nearest neighbors, then the relation $0<x_2<9$ is obtained. Similarly, it can get the relations of piece 2.  

Procedure II: Acquiring relations from diagram

![](images/Yu_2022_TDF_Procudure2.png)

# 4.3. Symbolic solver  

As presented in Procedure III, it takes the understood state $R$ as its input, which consists of $R_{T}$ and $R_{D}$. Procedure III has three stages, the first two is to generate mixture relations, including period equations and universal equations. Specially, a function is built in stage 2. The last stage solves the mixture relation group by an equation-function interaction method.  

ProcedureIII: Generating and solving the mixture relations   

![](images/Yu_2022_TDF_Procudure3.png)

The process of generating mixture relations starts with instantiating the relation group of $R$, then assembles the relations of function elements $R_j$ in function model to construct $f$.  

(1) Instantiating the relation group

To instantiate the relations in $R$, it performs three actions: list all entities appearing in the problem understanding relations and declare a list of variables corresponding to them; create a corresponding table $L(O,S)$ and the domains of variables; and further update $R$ with specified variables by looking up the table and transform them into universal  

Table 1 The list of the $S^{2}P$ models for acquiring the relations of function variables (that is $\Omega_{11}$) and their corresponding examples   

![](images/Yu_2022_TDF_Table1.png)

In this table, the symbol $F$ represents function analytic expressions, $F_{\nu}$ denotes a variable pair of $F$. $W_{f}$ key words of function, $n$ nouns, $s$ variable symbols in text, $d$ a direct proportional function, $\nu$ verbs and $e$ segment names.  

relation forms (e.g., $k_1 * x_1 = 6$) or period relation forms ($k = 0 \ \& \ x \in [x_1, 9]$).  

(2) Building a function relation  

Furthermore, the way of building function is to use the acquired relations to instantiate the general function model. It turns to reorganize function-related relations $R_{\mathcal{I}}$ (i.e., relations extracted by the newly built function specified $S^{2}P$ models and ones from function segments) into  

different function pieces according to their periods. For each function piece, its relations are either about $x,y$, or the parameters of $f_i$. (In this study, the default function analytical expression is formed as $y = k_i * x + b_i$ & $x \in [x_1, x_2]$ and $k_i, b_i, x_1, x_2$ are the function parameters.) Thus $f$ is constructed with function pieces by ranking all $f_i$ in the increasing order of the independent variable domain.  

![](images/2d8b044668316878cdbdbd6782bf8c31325dfde91335ed040aad5a4290d0c9bd_56.jpg){width=56%}  
Fig. 1. The process of understanding the text by using $S^2P$ method. Here $n$, $p$, $v$, $m$, $q$, $w$, $W_f$, and $s$ stand for nouns, pronouns, verbs, numerals, units, punctuation marks, key words of function and symbols, respectively.  

Table 2 $L^{2}$ models in $\Omega_{2}$. $\mathcal{S}_{\mathcal{D}}$ and $\mathcal{R}$ respectively denotes a (g) raph pattern of an $L^{2}$ model, a brief (d) escription of a graph pattern, and the (r) relations of a model   

![](images/Yu_2022_TDF_Table2.png)

(3) Solving the mixture relation group  

The state after building function is composed of the newly updated relation group $R$ and a function $f$, being in compound of period relations, called the mixture relation group. Obviously, to solve the mixture relation group, it is confronted with when and how to use the function relation.  

The equation-function interaction method is designed to solve the mixture relation group mainly by alternating two types of interacting: Situation 1 interacting with equations, which means the equivalent transformation performed between universal equations and period equations and Situation 2 interacting with function, which means performing operations on functions.  

The specific process of the method is as follows: it repeats to divide the mixture relations into linear group $G_1$ and nonlinear group $G_2$ according to the relationship between variables and equations, use the elimination method to solve the variables in $G_1$; then update $G_2$ with the obtained results, until no variable can be solved. Following, when identifying that a variable is related with a function, it performs Situation 2 by either looking up the parameters of a function piece or computing with a function piece.  

# 5. The proposed algorithm  

# 5.1. The component structure  

Proposition 1 shows that a TDF problem has an understood state, being a group of relations. Based on this fact, we first propose the methods of acquiring these relations from text and diagram separately. We then construct a symbolic solver to solve the group of relations that can construct functions from relations and can use it to find the solution. Fig. 3 depicts the structure of the main components for solving TDF problems.  

# 5.2. The relation-centric algorithm  

Algorithm I is the proposed algorithm for solving TDF problems, which has three steps. The first step is problem understanding. Procedure I conducts text understanding and Procedure II conducts the diagram understanding. Step 2 uses Procedure III to solve mixture relations. Step 3 generates and outputs a solution, including solving actions, corresponding states and the answer of a TDF problem.  

![](images/a360fb5b6890ec844f1ed99d47ba2729ddb456218c40e767e174b92023bbf1e9_45.jpg){width=45%}  
Fig. 2. The process of extracting relations from diagram. (a) is a diagram with function line segment; (b) and (c) are function pieces and their relations after matched with model 1 and model 3 in $\Omega_2$, respectively.  

![](images/a3143dbb2abb26a6c88719a41c3b0dc9a3fce39f7763f7f4e2d20c80c0cb9b77_70.jpg){width=70%}  
Fig. 3. The structure of the main components for solving TDF problems. The solid boxes indicate the components to be developed in this paper; the dotted boxes tell the actions of the corresponding components.  

Algorithm 1: A relation-centric algorithm for solving TDF problems

![](images/Yu_2022_TDF_Algorithm1.png)



# 6. The application of Algorithm 1  

This section first uses an example to illustrate how the proposed algorithm works and then it shows that the proposed algorithm is tutorable.  

# 6.1. Solving a TDF problem by Algorithm 1  

Fig. 4 gives the process that how Algorithm I solves an example. The entire solving process includes three steps.  

Step 1: Understanding text and diagram.  

The given problem has a text portion and a diagram. The problem text was parsed and annotated with key words and POS and then the algorithm uses the models in $\Omega_0$ and $\Omega_1$ to extract relations. Thus, the procedure of understanding text acquires relations: $\mathbf{r}_1$, $\mathbf{r}_2$, $\mathbf{r}_3$, $\mathbf{r}_4$, and $\mathbf{r}_5$. We explain how it acquires $\mathbf{r}_1$ as an example. When confirming that "n m q" appears in both $\Omega_0$ and the annotation of the first sentence, we conclude that the model "n m q" in $\Omega_0$ is matched with the first sentence. In consequence, the relation, $\mathbf{r}_1 : \text{volume} = 6 * \text{liters}$, is acquired. A special case deserves to be  

noted, both one model in $\Omega_{0}$ and another model in $\Omega_{1}$ matched with "1.2 liters per minute". Hence, this phrase leads a universal relation $\mathbf{r}_{6}$ and a function element relation $\mathbf{r}_{7}$.  

In diagram understanding, the procedure of diagram analysis finds two pieces. For piece 1, it is matched with the first model and instantiated its relations by the labelled numbers. Thus, it acquires $\mathbf{r}_8$, $\mathbf{r}_9$, $\mathbf{r}_{10}$, $\mathbf{r}_{11}$, $\mathbf{r}_{12}$. For piece 2, it acquires $\mathbf{r}_{13}$ and $\mathbf{r}_{14}$.  

All the relations acquired from text and diagram are the universal relations $\mathbf{r}_1, \mathbf{r}_2, \mathbf{r}_3, \mathbf{r}_4, \mathbf{r}_6$ and the period relations $\mathbf{r}_5, \mathbf{r}_7, \mathbf{r}_8, \mathbf{r}_9, \mathbf{r}_{10}, \mathbf{r}_{11}, \mathbf{r}_{12}, \mathbf{r}_{13}, \mathbf{r}_{14}$.  

Step 2: Symbolic solver.  

The function variables, their entities and units are updated, getting $\mathbf{r}_8$. Accordingly, it instantiated all relations by assigning variables, updating $\mathbf{r}_1$ to $\mathbf{r}_{13}$, such as $\mathbf{r}_1 : a = 6 * \text{liters}; \mathbf{r}_3 : b = 7 * \text{minutes}; \mathbf{r}_5 : X = f(7 * \text{minutes})$; $\mathbf{r}_7 : k_1 = 1.2 * \text{liters/minute}$.  

Then $f$ is acquired by assembling the two function pieces. For Piece 1, relations of function elements are $\mathbf{r}_7, \mathbf{r}_9, \mathbf{r}_{10}, \mathbf{r}_{11}, \mathbf{r}_{12}$. Similarly, as for piece 2, it has $\mathbf{r}_{13}$ and $\mathbf{r}_{14}$.  

When solving the mixture relation group, it derives the parameters of $f$ by solving the linear group part and update $f$, expressing as $\mathbf{r}_{11}: y = 1.2 * x \ \& \ x \in [0,5]; \mathbf{r}_{14}: y = 6 \ \& \ x \in [5,9]$. The relation of $X$ was from a function point in $f, \mathbf{r}_{5}: X = f(7 * \text{minutes})$. Then it performs interacting with $f$. After comparing the domains of function pieces, it determines that $(7,X)$ belonging to Piece 2 and the answer $\mathbf{r}_{15}$ is acquired.  

Step 3: Generating a solution.  

Finally, a tutorable solution is generated by organizing the mentioned actions and their results of two steps above. For example, during the text understanding, it generates the following actions and the results of updating states.  

>Action → match models $\Omega_{0}$ and $\Omega_{1}$ with sentences, Result → the acquired relations $\mathbf{r}_{1}$ from sentence 1, ..., $\mathbf{r}_{6}$ from sentence 2), after diagram understanding  

>Action → match function pieces with models in $\Omega_{2}$, Result → acquire the relations of Piece 1, $\mathbf{r}_{8}, \mathbf{r}_{9}, \mathbf{r}_{10}, \mathbf{r}_{11}, \mathbf{r}_{12}$, and the relations of Piece 2, $\mathbf{r}_{13}$ and $\mathbf{r}_{14}$). after function building  

>Action → group relations by different function pieces, Result → Piece 1: $\mathbf{r}_7$, $\mathbf{r}_9$, $\mathbf{r}_{10}$, $\mathbf{r}_{11}$, $\mathbf{r}_{12}$, and Piece 2: $\mathbf{r}_{13}$ and $\mathbf{r}_{14}$)during solving mixture relations  

>Action → solve the linear part of the mixture relation group, Result → "x₁ = 5");  

>Action $\rightarrow$ use $f$, Result $\rightarrow$ "ans = 6 * liters").  

![](images/6b0334b68b9a32a908151612cfbc3fe09cb98c55b174d5f3c0ef41989267ed99_70.jpg){width=70%}  
Fig. 4. The process of solving a TDF problem by Algorithm I.  



# 6.2. Tunorable solution of the proposed algorithm  

Proposition 2. Algorithm 1 gives a tutorable solution for TDF problems.  

We first discuss the criteria that a solution is tutorable and then we prove Proposition 2 by showing the solution produced by the proposed algorithm meet the criteria.  

The paper in Murray et al. (2004) believes that the main task of a tutor can be regarded as deciding what action to take in turn and the state changed by the action. In Faldu et al. (2021), it states that the interpretability of mathematical reasoning are the key factor of solving. Based on the above discussion, a tutorial algorithm have to meet two conditions. The first condition is a series of continuous actions and generated states. The second condition is that all the solving steps and their reasoning are understandable to learners.  

Here we show that Algorithm I is tutorial by showing that it meets the above-listed two conditions.  

(1) The proposed problem understanding method leads learners to focus on only a few signals of all the information described in the problem text or the diagram. $S^{2}P$ model method is used to extract relations between sentences by identifying matching models based on relevant facts (i.e., syntax and semantic information). In diagram understanding, it emphasizes on how to obtain function pieces one by one. The task of getting a function piece simply matches two or three function elements using $L^{2}$ models. Therefore, one can see that, text understanding and diagram understanding are fact-identification steps, because they contain information that learners can collect directly from the problem, which is easy for learners to follow.

(2) By eliciting causal explanations from Definition 5 and Definition 6, building a function is to assemble function pieces, that make it possible for one to learn. In this study, it is a clear process to reorganize the function pieces from the relations derived from text and diagram.

(3) Solving mixed relation group is a process of relation transformation. It starts with solving linear equations, then selects the action to work on the current state of the input problem, and ends with a transformed state. These transformations follow the principle of equivalent relation. The pattern of (Action,State) supports causal reasoning. On this basis, Algorithm I can generate an interpretable reasoning path for solving the mixture relation group.  
