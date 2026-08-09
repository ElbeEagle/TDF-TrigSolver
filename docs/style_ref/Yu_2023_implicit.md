# Solving arithmetic word problems by synergizing syntax-semantics extractor for explicit relations and neural network miner for implicit relations  

# Abstract  

This paper presents a relation-centric algorithm for solving arithmetic word problems (AWPs) by synergizing a syntax-semantics extractor for extracting explicit relations, and a neural network miner for mining implicit relations. This is the first algorithm that has a specific component to acquire implicit knowledge items for solving AWPs. This paper proposes a three-phase scheme to decompose the challenging task of designing an algorithm for solving AWPs into three smaller tasks. The first phase proposes a state-action paradigm; the second phase instantiates the paradigm into a relation-centric approach; and the third phase implements a relation-centric algorithm for solving AWPs. There are two main steps in the proposed algorithm: problem understanding and symbolic solver. By adopting the relation-centric approach, problem understanding becomes a task of relation acquisition. For conducting the task of relation acquisition, a relaxed syntax-semantics method first extracts a group of explicit relation candidates. In parallel, a neural network miner acquires implicit relation candidates. The miner computes the vectors encoded by BERT to determine which implicit relations should be added. Thus, problem understanding can acquire both explicit relations and implicit relations, which addresses the challenge of building a problem understanding method that can acquire all the knowledge items to find the solution. In the subsequent step of symbolic solver, a fusion procedure forms a distilled set of relations from all the candidates by discarding unnecessary relations. Experimentation on nine benchmark datasets validates the superiority of the proposed algorithm that outperforms the state-of-the-art algorithms.  

Keywords Problem solving · State-action paradigm · Relation-centric · Explicit relation · Implicit relation · Syntax-semantics model  


# State-action paradigm and relation-centric approach  

This paper proposes a three-phase scheme to develop algorithms for solving AWPs, which is a scheme to design algorithms from abstract to concreteness. This section presents the first two phases. The first phase is to design a solving paradigm. Concretely, it proposes a state-action paradigm for solving AWPs as solving paradigm. The second phase is to define the states of the state-action paradigm to form a relation-centric approach to solving AWPs.  

The goal of this paper is to design high performance algorithms for solving AWPs. Through analyzing the algorithms in the literature, the loop of states and actions can explain the process of solving AWPs by algorithms. Hence, this paper proposes a state-action paradigm as depicted in Fig. 2 and uses it as the algorithm paradigm of solving AWPs. In this paradigm, the states are different states of knowledge expression and actions are the algorithm actions to transform from a state to another. This abstract solving paradigm is a simple diagram, but it can guide us to understand what the solving algorithms are doing and what the core issues of solving problems are. It also can explain how we design approaches and algorithms for solving AWPs. More importantly, the approach of solving AWPs can be defined based on the abstract solving paradigm.  

![](images/99b92c6afde7f9a5b01fa398e427d62aacc20115015abefe96524519feed650e_61.jpg){width=61%}  
Fig. 2 The state-action paradigm of solving AWPs  

Definition 1 (Approach) An approach is an instance of the state-action paradigm by determining the main states of the state-action paradigm and the links to change from a state to another.  

"The related work in solving approach" has classified the existing algorithms in the literature into five approaches. We take two approaches as examples to show that all the five approaches conform to Definition 1. The first approach is seq2seq. The algorithms in this approach have two related states: a vector sequence and the sequence of answer expression. Thus, they have three common links. The first link is the encoding step to encode the given problem into a vector sequence. The second link is to transform a vector sequence of problem text into a vector sequence of answer expression. The third link is to evaluate answer expression and output the answer. The second approach is relation-centric. The algorithms in this approach have one common state, which is a group of relations. Thus, they have two common links. The first link is to acquiring a group of relations, being another kind of problem understanding. The second link is to solve the group of relations.  

Building a link from one state to another means that researchers have found methods to accomplish this state transformation at least for a corpus of problems. Along this state-action solving paradigm, designing algorithms means to propose methods to implement the links of the adopted approach.  

All the states in the state-action solving paradigm are the states equivalent to the given problem in terms of solving AWPs. Among these states, researchers want to acquire an understood state, which is defined as follows.  

Definition 2 (Understood State) A state is called an understood state of a given AWP if a symbolic solver can produce the solution from this state without revisiting the given problem.  

From Definition 2, all the states except the input state and the vector sequence of problem text in the five approaches are understood states.  

Definition 3 (Problem Understanding) Problem understanding is to produce an understood state of AWPs.  

Definition 4 (Relation) A relation is an equation expression of quantifiable entity, where a quantifiable entity can be a number, a variable, or a phrase that describes a quantity.  

A relation differs from an equation in that its items may be phrases except variables and numbers. In this paper, a relation is actually a quantity relation because all its elements are about quantity.  

Proposition 1 Assume that $\mathcal{C}$ is a corpus of AWPs. Let $\mathcal{P}$ be an AWP in $\mathcal{C}$. Then there is a group of relations denoted as $\mathcal{E}=\{r_i : i=1\text{ to }k\}$ such that it is an understood state of $\mathcal{P}$.  

A theoretical proof for Proposition 1 is not available so far, but the experimental results in "Experiments" will testify its correctness. Actually, Proposition 1 is the assumption of many existing algorithms for solving AWPs.  

We define the relation-centric approach formally because it is a central term of this paper.  

Definition 5 (Relation-Centric Approach) A relation-centric approach is an instance of the state-action paradigm such that: 1) it has two links of problem understanding and symbolic solver; 2) the link of problem understanding is to produce a group of relations that is an understood state of a problem; 3) the link of the symbolic solver is to find values of the unknowns in the given problem through transforming the group of relations.  

Definition 5 shows that relation acquisition and relation transformation are the main operations of the relation-centric approach. This approach benefit from the fact that relation extraction from text is more tractable than equation extraction.  

# A relation-centric algorithm for solving AWPs  

This section presents a relation-centric algorithm for solving AWPs by implementing the relation-centric approach.  

# Algorithm outline  

This section instantiates the relation-centric approach into a three-step algorithm to solve AWPs. The first step is to acquire a group of relations. The second step is a symbolic solver, which solves the group of relations. The last step is to output the unknowns with found values and an algorithmic solution, which is a series of actions of acquiring and transforming relations, recorded along the algorithm execution. These three steps constitute the proposed algorithm, which is shown in Algorithm 1. The proposed algorithm uses five procedures, namely Procedure I to V, to implement the five tasks of the algorithm. The process of solving problems by Algorithm 1 is explainable because people can understand all the actions of acquiring and transforming relations. More importantly, this series of actions can instruct students how the algorithm solves the problem. Figure 1(b) shows the process that Algorithm 1 solves a given AWP to demonstrate how Algorithm 1 works.  

Algorithm I:  The Algorithm for Solving AWPs.

![](images/Yu_2023_explicit_implicit_Algorithm1.png)

Procedure I: Extracting Explicit Relations from Problem Text.

![](images/Yu_2023_explicit_implicit_Procedure1.png)

# Acquiring relations of AWPs  

This section presents the method details of acquiring relations from AWPs. It comprises two aspects: (1) extracting explicit relations, and (2) acquiring implicit relations.  

Definition 6 (Explicit and Implicit Relation) Let $\mathbb{R}$ be a set of relations that is an understood state of a given AWP. A relation in $\mathbb{R}$ is an explicit relation if it explicitly states in problem text; otherwise, it is an implicit relation.  

# Extracting explicit relations using relaxed S$^{2}$ method  

This section designs a relaxed S$^{2}$ method by enhancing the S$^{2}$ method. Compared with the original S$^{2}$ method, the relaxed S$^{2}$ method relaxes the requirement that each piece of text can match only one S$^{2}$ model and delays the action of judging whether an extracted relation is used by the coming symbolic solver. Procedure 1 uses the proposed relaxed S$^{2}$ method to extract explicit relations. The syntax portions of S$^{2}$ models are comprised of patterns of POS (part-of-speech) and punctuation while the semantic portions are keyword structures. Procedure 1 can work only after a pool of S$^{2}$ models are prepared appropriately for a natural language.  

Definition 7 ($S^2$ Model) A syntax-semantics model, shorted as S$^2$ model, is defined as a quadruple $M = (K, P, Q; R)$, where $K$ represents semantics keyword structures, $P$ represents POS, $Q$ represents the punctuation, and $R$ is the relation as model output. Let $\Sigma = \{M_I = (K_i, P_i, Q_i; R_i) \mid i = 1, 2, ..., m\}$ denote the set of all the prepared S$^2$ models, called as a pool of S$^2$ models for AWPs.  

![](images/0be4fc0ef449d13f9ebfa76d0abc11b1f2d78442532c2083c0a21bdbf6c0e7a4_60.jpg){width=60%}  
Fig. 3 The process of using S$^{2}$ method to extract explicit relations from a sample AWP  

Definition 8 (Matching Action) A matching action is an action which matches the structure of $K$, $P$, $Q$ from a quadruple $M = (K, P, Q; R)$ to a portion of problem text.  

After loaded with a pool of S$^{2}$ models, Procedure 1 can extract explicit relations from a given input text. To acquire all explicit relations, it is necessary to match all the models in the pool with all potential portions of text. The crucial point of the procedure is to judge whether a model matches a portion of problem text. The outcome of this procedure is a set of explicit relations. Figure 3 uses an example to illustrate how Procedure 1 extracts explicit relations from AWPs. This whole process is called as an S$^{2}$ method.  

When using the S$^{2}$ method, the main job of model matching is to match the POS change pattern with a portion of text. There are eight types of frequently used POS in S$^{2}$ models in English: n (nouns), v (verbs), a (adjectives), p (pronouns), m (numerals), c (conjunctions), r (particles), and w (punctuation marks). Each POS type corresponds to one of the twelve universal POS tags from natural languages.  

This paper prepares pools of S$^{2}$ models for Chinese and English respectively. The pools of S$^{2}$ models for Chinese and for English consists of 220 and 360 S$^{2}$ models respectively. Table 1 lists eight frequently used S$^{2}$ models for solving problems in English.  

# Neural network miner for acquiring implicit relations  

This section develops a procedure to acquire the implicit relations from problems. There are two cases of the implicit relations considered in this paper: unit conversion and arithmetic formula. Unit conversion is to add the relations that  

convert the different units of the same measurement appearing in the same problem. Arithmetic formula targets to add appropriate formula about corresponding scenarios. For example, when a problem appears to a scenario of calculating the area of a rectangular object, the component adds the formula of the rectangle area.  

For the unit conversion, Dewappriya et al. [34] considered it as an issue of unit conflict and proposed a procedure to solve it. This paper adopts this procedure and uses it as a prior process to obtain the entire unit conversion relations for each measurement system involved in a given problem without giving the detail of this process.  

For the arithmetic formula, the neural network miner can be a useful tool for such types of tasks since it can acquire the hints from the problem text. As it is known, the implicit relation belonging to the arithmetic scenario is highly related with quantity words. Hence, this paper proposes a neural network miner based on $quantity$ to $relation$ $attention$ $neural$ $network$ (QRAN) to mine implicit relations (Procedure II). The procedure consists of three steps:  

The first step is to encode the given problem into a sequence of vectors. A given problem can be tokenized as $\mathcal{P}=\{w_i\}_{i=1}^n$, each token $w_i$ can be represented as a word-context feature vector $v_i$ by BERT [50]. Thus, $\mathcal{P}$ can be denoted by a sequence of vectors as $\mathcal{V}=\{v_i\}_{i=1}^n$. The next process is to select the vectors related to quantity, including the numeric words like "100", "1/2" and the descriptive words like "double", "half". Let $\mathcal{N}$ denote the set of the quantity vectors in the problem, and place $v_i$ into $\mathcal{N}$ if $w_i$ is a quantity word. Thus, $\mathcal{N}=\{q_i\}_{i=1}^k$ contains all the quantity  

Table 1 The list of eight frequently used models from the pool of $S^2$ models for solving AWPs in English and examples of these eight models extracting explicit relations from problem text   

![](images/Yu_2023_explicit_implicit_Table1.png)


| No | $S$^2$ Model$ | Examples of extracting explicit relations Problem text | Matching | Explicit relation |
| --- | --- | --- | --- | --- |
| 1 | $There m,n: $a=b$, a:=m, b:=n$$ | There are 14 poplar trees in the school | $\xrightarrow{model1}$ | $\xrightarrow{poplar\_tree=14}$ |
| 2 | $n m times n: $a=b \times c$;$ | Poplar trees are 2 times that of pine trees | $\xrightarrow{model2}$ | $\xrightarrow{poplar\_tree=2 \times pine\_tree}$ |
| 3 | $n m more than n: $a=b+c$;$ | Willow trees are 4 more than pine trees | $\xrightarrow{model3}$ | $\xrightarrow{willow\_tree=4 + pine\_tree}$ |
| 4 | $n m is m q: $a=b*c$;$ | The walking time to school is 1.5 hours | $\xrightarrow{model4}$ | $\xrightarrow{time=1.5 \times hour}$ |
| 5 | $a:=n, b:=m, c:=q$ | The sum of the upper and lower base of a trapezoid is 7 meters | $\xrightarrow{model5}$ | $\xrightarrow{upper\_base+lower\_base=7 \times meter}$ |
| 6 | $sum of n is m q: $a+b=c*d$;$ | The difference of the fifth and fourth grades is 41 | $\xrightarrow{model6}$ | $\xrightarrow{fifth\_grade - fourth\_grade=41}$ |
| 7 | $n m q per q: $a=b*c/d$;$ | The average harvest of potatoes is 1.5kg per square meter | $\xrightarrow{model7}$ | $\xrightarrow{potato=1.5 \times kg/square\_meter}$ |
| 8 | $n m times less than n: $a=(1-b)^{*}c$;$ | The number of roses is 0.2 times less than that of daffodils | $\xrightarrow{model8}$ | $\xrightarrow{rose=(1-0.2) \times daffoil}$ |  

vectors, where $k$ is the total number of the quantity words in a problem.  

The second step is to obtain the goal vector $v_g$ representing implicit relations by adopting the quantity-relation attention mechanism. The concrete computing process is as follows:  

$$
\mu _ { i } = \alpha \cdot t a n h ( W _ { r } \cdot [ \bar { v } , q _ { i } ] )  f o r \; i = 1 , 2 , . . . , k .
$$

$$
a _ { i } = \frac { e x p ( \mu _ { i } ) } { \sum _ { j = 1 } ^{k} e x p ( \mu _ { j } ) }
$$

$$
v _ { g } = \sum _ { i = 1 } ^{k} a _ { i } \cdot q _ { i }
$$

where $\bar{v}$ is the average vector of the sequence $\mathcal{V}$, $\mu_i$ is the relevance score between the whole problem and a quantity related word, $a_i$ is the attention score of each quantity in a softmax manner, $\alpha$ and $W_r$ are parameters trained for each specific implicit mathematical relation.  

The goal vector $v_{g}$ can be transformed to a indicator $\hat{y}$ through a dense layer, judging whether an implicit relation needs to be added. The $\hat{y}$ is defined as Eq. (4). As $\hat{y}$ is the predicted value of the implicit relation category, we can get the corresponding relation from the prepared implicit relation knowledge base.  

$$
\hat { y } = \sigma ( W _ { c } \cdot v _ { g } + \beta _ { c } )
$$

where $\sigma$ is the sigmoid function, $W_{c}$ and $\beta_{c}$ are trainable parameters.  

A knowledge base $\mathbb{D}$ consisting of pairs of implicit category with a corresponding formula (abstract relation) is constructed. We assume that the ground truth label of a problem is $y \in \mathbb{D}^{\mathbb{C}}$, where $y_i = \{0, 1\}$ denotes whether label $i$ appears in the problem or not. The whole network is trained using the multi-label classification loss as follow  

Procedure II: Discovering and Adding Implicit Relations.

![](images/Yu_2023_explicit_implicit_Procedure2.png)

![](images/ca6bf61ec90fa2f7b01c985c345da14ffd29f1615d21b904ba5f2267299efbe0_39.jpg){width=39%}  
Fig. 4 The architecture of the main part of Procedure II  

$$
L o s s ( y , \hat { y } ) = - \frac { 1 } { C } \sum _ { i = 1 } ^{C} [ y _ { i } l o g ( \hat { y } _ { i } ) + ( 1 - y _ { i } ) l o g ( 1 - \hat { y } _ { i } )
$$

where $C$ denotes the number of categories of formula (implicit relations).  

The third step is to instantiate the variables in the formula by connecting the entities in problem text. Each variable in implicit relation are transformed to word vectors through BERT, represented as a vector $I_i$. And each entity in the problem text obtained in extraction of explicit relation can be represented as a word vector $E_j = \{\bar{v}\}^l$, where $l$ is the token length of the word. The cosine similarity $cos(I_i, E_j)$ is adopted to calculate the semantic similarity between variable in implicit relation and the entity in text. Once the similarity $cos(I_i, E_j)$ get the max value, the $i$-th variable in abstract relation would be substituted by the $j$-th entity in problem text. A instantiated implicit relation would be obtained after all the variables connecting to the corresponding entity. For a problem, all the instantiated implicit relations would be added to the output collection $\Delta$ finally.  

Procedure II adds implicit relations to complement the problem understanding relying on the trained QRAN to discover the requiring abstract relations. Figure 4 illustrates an architecture of the main part of Procedure II. The implementation details of QRAN are presented in Appendix A.  

# Symbolic solver  

Symbolic solver takes three steps to transform the group of relations to find the values of unknowns. The first step is to acquire the group of distilled relations (Procedure III). The second step is to build a system of equations (Procedure IV)  

Procedure III: Acquiring the Fused Set of Relations.

![](images/Yu_2023_explicit_implicit_Procedure3.png)

and the third step solves the system of equations (Procedure V).  

# Distillation of explicit and implicit relations  

Procedure I and II together produce a set of candidate relations from a given problem text. These candidate relations might contain relations that symbolic solver does not use and they might lead the solver to produce wrong results. Hence, a procedure needs to discard as many as possible these unnecessary relations. Procedure III proposes to perform the selection from the set of candidate relations based on global and connection characteristics. The main idea lies in identifying the necessary relations according to their link with problem unknowns. The detailed process is as follows: First, it builds a relation graph, whose nodes are all the candidate relations and whose links indicate whether two relations are relevant. We start to build this graph from the relations that contain the unknowns; add a node for a relation and add links if it has the sharing quantity objects with the built nodes in the graph and it is consistent with nodes in terms of arithmetic formulas. In other words, whether two relations are relevant is equivalent to whether two relations have the sharing quantity objects and they are involved in the same arithmetic formula. Then it identifies the solution graph, which is a partial graph, contains all problem unknowns and all nodes connecting to any unknown, and all the links among these nodes. The relations in the solution graph forms a set of distilled relations.  

# Forming a system of equations  

To obtain the system of equations for a given problem, we need to list all entities that appear in the distilled relations. Then we assign a variable to each entity. The assigned variables replace all the entities in the distilled relations. Each  

relation thus turns into an equation and all the relations form a system of equations. The system of equations and the entity-variable table represent the given problem together. The detailed process is given in Procedure IV.  

Procedure IV: Forming a System of Equations.

![](images/Yu_2023_explicit_implicit_Procedure4.png)

# Solving the equation system  

The system of equations always contain some linear equations, though the whole system may not be a linear system. Gaussian elimination can solve these linear equations. The new linear equations forms when the solution of the linear equations replaces variables. This recurring manner will solve the whole system of equations. The detailed process is shown in Procedure V.  
