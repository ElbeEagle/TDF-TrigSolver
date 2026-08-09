
# A Scene-Attention Relation-Centric Algorithm for Solving Arithmetic Word Problems  


# ABSTRACT  

Keywords: Problem Solving Arithmetic Word Problems Relation-Centric Algorithm Scene-Syntax-Semantic Method Scene-Guided Symbolic Solver  

This paper presents the Scene-Attention Relation-Centric Algorithm (SARC), a novel approach to solving Arithmetic Word Problems (AWPs). Building on a decade of advancements in relation-centric methodologies, this study integrates scene knowledge to enhance both relation acquisition and inference, resulting in a high-performance algorithm that excels in accuracy and generating didactic solutions. For relation acquisition, the paper introduces the Scene-Syntax-Semantic ($S^{3}$) method, which extracts explicit and implicit relations from scene-labeled text. This is achieved using two dedicated $S^{3}$ model pools: one for acquiring intra-scene relations and another for bridging relations between scenes. In relation inference, a Scene-Guided Symbolic Solver is developed to categorize the acquired relations by their associated scenes or scene pairs, enabling the inference process to operate in two modes: intra-scene and inter-scene. This scene-guided strategy enhances both the accuracy and efficiency of relation inference by increasing the certainty of inference operations. Experimental evaluations on five authoritative datasets demonstrate that the proposed algorithm surpasses all baseline models. It achieves an overall accuracy improvement of 1.7% and a 4.1% increase on problems involving multiple scenes. Additionally, qualitative analyses of illustrative cases reveal that the algorithm generates more didactic solutions compared to baseline methods. These findings underscore the effectiveness of incorporating scene knowledge into relation-centric approaches, significantly advancing both problem-solving accuracy and explanatory quality.  


# 3. Scene-attention relation-centric approach  

The algorithm proposed in this paper is developed by adopting the three-phase scheme proposed by Yu et al. (2023). This section implements the first phase to explain the scene-attention relation-centric approach to solving AWPs. It begins by outlining the structure of the approach and defining its core components.  

# 3.1. State transform graph of the solving approach  

The state transform graph is a valuable tool for illustrating both the Scene-Attention Relation-Centric Approach proposed in this paper and the traditional Relation-Centric Approach. In such graphs, "state" and "transform" are two foundational concepts, all of which are formally defined by Yu et al. (2024). Here, we provide brief descriptions: a "state" refers to the key representation sharing models that can represent intermediate results produced by various solving algorithms, while a "transform" denotes a method that converts instances from one state to instances in the next state.  

Fig. 1(a) presents the state transform graph of the proposed Scene-Attention Relation-Centric (SARC) algorithm. This graph introduces two new states. The first state, "Scene and POS Annotated Text", involves labeling each sentence in the problem text with its respective types of scenes. Here, POS (part-of-speech) refers to the grammatical category of words (e.g., nouns, verbs, adjectives), which provides essential syntactic information. The second state, "Scene Relation Set", tags the source of each relation with a scene or a scene pair (an unordered  

![](images/3758852d51aa52938fc72424182f25e07b1c472b628e2212efa6cf54834d9fe1_75.jpg){width=75%}  
Fig. 1. The state transition graph of the proposed scene-attention relation-centric approach is shown in the upper half (a), contrasted with the state transition graph of the existing relation-centric approach (Yu et al., 2023) in the lower half (b).  

scene pair). These states are used to replace the states of "Annotated Text" and "Relation Set" in the relation-centric approach (Fig. 1(b)) presented by Yu et al. (2023), thereby forming the scene-attention relation-centric approach.  

# 3.2. Concepts for developing the problem-solving approach  

The concepts are presented to describe the relation-centric approach for solving AWPs. The main concepts are AW, relation, scene, relation set, etc.  

Definition 1 (AWP). An arithmetic word problem (AWP) is a mathematical problem expressed in natural language, usually involving real-life situations, requiring the application of arithmetic operations to find a solution.  

Solving these AWPs requires interpreting the text to identify relevant numerical data and operations (such as addition, subtraction, multiplication, or division) in order to formulate and solve an underlying arithmetic equation.  

Definition 2 (Relation). A relation is an equation that includes numbers, variables, and quantitative phrases. A relation is called an explicit relation if it is explicitly stated in the problem description. In contrast, it is called an implicit relation if it is required for the solving process but is not explicitly stated in the problem narration.  

Relations appear similar to equations, but they play a different role in problem-solving. To create equations, one must first determine whether two entities should use the same variable in advance. In contrast, with relations, the entities themselves can initially be treated as variables, and whether two entities indicate the same quantity can be evaluated in a separate step. This makes relations more effective for gaining a deeper understanding of problems. Some methods propose using neural networks to generate equations and directly derive solutions, but this approach often bypasses a thorough problem-understanding process.  

The examples of explicit and implicit relations are given as follows. Provided that "His height is 178 cm" is the part of a problem narration, it states an explicit relation "his-height = 178xcm". From "find the speed of a car", the algorithm has to assume (and eventually list as part of the solution) an equation "the speed = distance+time" based on the knowledge beyond the problem direct statement, which is an implicit relation.  

Relations in this paper are quantitative relations because they involve solving AWPs. In the relation-centric algorithms, the step of problem understanding is to acquire both explicit and implicit relations and the output of problem understanding is a relation set. Hence, the relation set is the critical state of solving algorithms. Its definition is as follows.  

Definition 3 (Relation Set). Relation Set is an understood state, whose instance is a set of relations. A relation set calls an understood state of an AWP if this relation set equivalently represents the given problems in terms of solving the problem or a symbolic solver can produce the solution from the relation set.  

Definition 4 (Relation-Centric Approach). A relation-centric approach is an approach that solves problems based on acquiring a relation set as the understood state and using a symbolic solver to infer the relation set to produce the solution.  

AWPs involve a wide range of situations and mathematical structures, which contributes to their complexity as a research challenge of problem solving. When students tackle these problems, they must translate situations into appropriate mathematical relations. To develop effective solving algorithms, a set of mathematical scenes (or scenes) is desired to capture as many situations in AWPs as possible.  

In this context, a "scene" serves as an overarching concept that encompasses a set of mathematical various situations. Each scene contains inherent relations among its entities. This scene knowledge can facilitate relation acquisition within a relation-centric approach, effectively evolving it into a scene-attention relation-centric approach. To explain this approach, the key concepts, such as "scene" and "scene relation set", are defined as follows:  

Definition 5 (Scene). A scene is a representation model that encapsulates a set of various scenarios appeared in AWPs. It is defined as a quadruple $(S, L, \mathcal{K}, T)$, where:  

- $S$ denotes the type of scene;
- $L$ represents the roles involved in the scene;
- $\mathcal{K}$ refers to the knowledge relevant to the scene;
- $T$ is the text that contains a group of sentences from the AWP that $\mathbf{e}$ in the same scene instance.  

This paper focuses on three scenes in primary education: Part-Whole, Change, and Rate. These scenes have been repeatedly studied in previous research (Hosseini et al., 2014; Kintsch & Greeno, 1985;  

![](images/dba26f526ad105486ca4b2d1e8fdaed08d88c9eec9fabe2d178e6ddfd29900ba_38.jpg){width=38%}  
Fig. 2. Representation models of the three scenes defined and used in this paper.  

Mitra & Baral, 2016; Roy & Roth, 2018), making them well-understood and applicable. Specifically, "Part-Whole" describes the quantity of entities being decomposed into the quantity of multiple entities; "Change" describes the increase or decrease in the quantity of an entity during the change process; "Rate" describes the quantity of an entity converted between different units through rate. This paper aims to demonstrate that a small number of scenes can significantly improve the performance of existing solving algorithms. Therefore, it focuses on three scenes for two key reasons. First, these scenes are the most commonly occurring in AWPs. Second, they have been repeatedly studied in related works, enabling the application of well-established knowledge. The representation models of the above scenes are illustrated in Fig. 2.  

In Fig. 2, the term "Type" refers to the name of a scene and also serves as a label in this paper. The term "Role" represents the abstract concept that an entity from the problem text assumes within a scene. For instance, in the "Part-Whole" scene, the "banana" takes on the role of "Part". The term "Knowledge" describes the relation between all the roles in a scene, which can be used to solve any problem associated with that scene. The term "Text" refers to the problem texts related to a scene, where "related" means that the entities in the problem text can be mapped to the roles in the scene, enabling the algorithm to apply scene-specific knowledge. The definitions of these terms are primarily derived from several related studies (Hosseini et al., 2014; Mitra & Baral, 2016; Roy & Roth, 2018), which highlight their effectiveness in algorithmic problem solving".  

For building the new solving algorithm, the "Type" of each scene is given as a label at sentence level, establishing Scene and POS Annotation as a crucial intermediate representation (or state). The definition is as follows:  

Definition 6 (Scene and POS Annotation). A processed text is referred to as an instance of Scene and POS Annotation when each sentence is labeled with the type of a scene or a pair of types corresponding to a pair of scenes and every phrase within the sentence is tagged with Part-Of-Speech (POS) labels.  

In AWPs, some sentences can be labeled with two scenes (a scene pair) because they serve as "linking sentences" connecting two scenes,  

although most sentences are associated with a single scene. Fig. 3 illustrates example texts that involve two scenes, along with their corresponding "Scene and POS Annotation". In such cases, a "linking sentence" that spans across two scenes, like "All fruits are divided into 5 boxes", would be labeled with the type of unordered scene pair, such as "[Part-Whole, Rate]".  

In Fig. 3, several notations represent POS labels, defined as follows: "n" denotes a noun, "v" a verb, "m" a numeral, "q" a quantifier, "dt" a determiner, "ax" an auxiliary verb, "ap" an adposition, "sconj" a subordinating conjunction, "adj" an adjective, and "adv" an adverb.  

To acquire various relations through different methods, both intra-scene and inter-scene relations are formally defined as follows:  

Definition 7 (Intra- and Inter-Scene Relation). In acquiring relations from an AWP, a relation is defined as an intra-scene relation if it is extracted from text within the same scene. Otherwise, it is termed an inter-scene relation if it is derived from text labeled with a pair of types.  

An intra-scene relation inherits the type of scene from its source text, while an inter-scene relation involves two different types, which is reflected in its labeling of the paired scenes. Intra-scene relation can be an explicit or implicit relation. For example, an explicit relation "chickens = 50 + ducks" and an implicit relation "Whole(poultry) = Part(chicken) + Part(duck)" can be acquired from a "Part-Whole" scene labeled text "chickens are 50 more than ducks. How many poultry are there in total?".  

The Mechanism of Acquiring Intra-Scene Implicit Relations from Scenes: Each scene inherently contains intrinsic relations among its entities. If certain inherent relations are not included in the set of acquired explicit relations, they are added to the relation set as implicit relations, following the $S^{3}$ method defined in the next section.  

Inter-scene relations represent a specific type of explicit relation between two scenes, identified by a scene pair and described through linking sentences. These relations can typically only be determined once a link between the two scenes has been established. For example, "Left(Ken)=Left(Leo)+?" cannot be acquired from "how many more candies does Ken have than Leo now?" before the two scenes about "Ken" and "Leo" are determined.  

Definition 8 (Scene Relation Set). A relation set is termed a Scene Relation Set if it satisfies the following conditions:

1. It is an understood state of an AWP.

2. Each relation within the set is labeled with either a scene type or a pair of scene types.  

With Scene and POS Annotation and Scene Relation Set, the Scene-Attention Relation-Centric approach is defined as follows:  

Definition 9 (Scene-Attention Relation-Centric Approach). A Scene-Attention Relation-Centric Approach enhances the traditional relation-centric approach by replacing Annotated Text and Relation Set with Scene and POS Annotation, as well as Scene Relation Set.  

# 4. Methods of transforming states  

This section discusses the second phase of the three-phase scheme of developing solving algorithms. In other words, it develops the methods for each link of the state transform graph of the algorithm presented in Fig. 1. First, a method is proposed to transform Problem Text to Scene and POS Annotation. Then, a $S^3$ method is proposed to transform Scene and POS Annotation to Scene Relation Set, in which the $S^3$ method evolves from the $S^2$ method presented in Yu et al. (2023). Third, a Scene-Guided Symbolic Solver is developed to infer Scene Relation Set and produce an algorithmic solution.  

![](images/bb0c5b1bc049ba45f91d7f74544e7e4c999d3cffb11a23877a0601b3ec97545e_40.jpg){width=40%}  
Fig. 3. Two examples demonstrating the conversion of "Problem Text" into instances of state referred to as "Scene and POS Annotation". (For the multi-label classifier, the numbers "1, 2, 3" represent different scene instances; for the concat-binary classifier, "true/false" indicate whether a pair of sentences belongs to the same scene instance.)  

# 4.1. Scene parsing and annotating method  

The "scene parsing and annotation" method is proposed to transform problem text into the form required for relation acquisition. The pipeline of this method is shown in Fig. 3, with two typical examples. Two key steps are used to parse the problem text into scene-labeled text. The first step labels the type of scene for each sentence in the problem text. In this step, a pre-trained encoder is first employed to obtain the vector sequence of the problem text, and then a multi-label classifier is used to predict the scene types for each sentence.  

The second step involves grouping sentences into clusters, where each cluster represents text from a distinct scene instance. Differentiating between a scene and a scene instance is crucial, as a single scene type may appear multiple instances within the same AWP. For each pair of sentences labeled with the same scene type, a concatenated binary classification network determines whether the two sentences belong in the same cluster. This binary classification is essential in multi-scene scenarios, as certain scenes may need to appear multiple instances to account for different entities in the problem text. For example, in Fig. 3, the sentences "Ken later bought 5 more candies" and "Leo ate (1/3)" are labeled with the same scene type "Change". However, they should belong to separate clusters due to the distinct entities involved (each  

sentence involves different subjects experiencing quantitative changes within the "Change" scene).  

After scene parsing, this paper uses Part-Of-Speech (POS) tagging tools (details shown in Section 5.2) to annotate sentences. This annotation tool can generate a POS sequence for each sentence, which can be used to match the different parts of the model structure in subsequent relation acquisition. Note that in Fig. 3, the POS tagging tool and the classification networks for scene parsing are used independently. The annotations generated by the POS tagging tool adhere to the corresponding text during the entire solving process.  

# 4.2. Scene-syntax-semantic method  

The $S^{3}$ (Scene-Syntax-Semantic) method is the evolved version of the $S^{2}$ method presented in Yu et al. (2017), which targets to transform Scene and POS Annotation into Scene Relation Set in the state transform graph of the approach presented in Fig. 1(a). The $S^{3}$ method mainly involves $S^{3}$ models and model-based matching. Hence, the $S^{3}$ models are first defined and discussed as follow.  

The $S^{3}$ models are divided into the intra-scene $S^{3}$ models and the inter-scene $S^{3}$ models. The intra-scene $S^{3}$ models are designed for acquiring relations from a single scene, and the definition is as follows:  

Definition 10 (Intra-Scene $S^{3}$ Model). An intra-scene $S^{3}$ model is a six-tuple $\delta = (S; P, K, L; Q; R)$, with $S$ denoting a type of scene, $P$ denoting structure of POS, $K$ representing keywords, $L$ representing roles in the scene, $Q$ representing the matching rules, and $R$ is the relation template. Given a dataset $\mathcal{D}$, $\Delta_{\mathcal{D}} = \{\delta_{i} = (S; P, K, L; Q; R) \mid i = 1,2,3, \ldots\}$ is called a pool of intra-scene $S^{3}$ models.  

The term "L" mentioned here refers to the process of partially or fully associating the roles from a scene of type "S" in the model. This allows the model to identify and establish correspondence between the entities described in the problem text and the roles within the scene. Associating the elements of the model with the concrete content aids the algorithm in capturing both explicit and implicit relations (as discussed in Section 5.3.1).  

The inter-scene $S^{3}$ models are designed to capture relations from sentences labeled with a pair of scene types. The concept of an inter-scene $S^{3}$ model is defined as follows:  

Definition 11 (Inter-Scene $S^3$ Model). An inter-scene $S^3$ model is a six-tuple $\psi = (C; P, K, L; Q; R)$, with $C$ denoting a pair of scene types, $P$ denoting structure of POS, $K$ representing keywords, and $L$ denoting the roles in the scene pair, $Q$ representing the matching rules, and $R$ is the relation template. Given a datasets $D$, $\Psi_D = \{\psi_i = (C; P, K, L; Q; R) \mid i = 1,2,3, \ldots\}$ is called a pool of inter-scene $S^3$ models.  

In this paper, the scene pair involved in inter-scene $S^{3}$ models do not adhere a specific order. The process involves matching the entities in linking sentences with those in the previously acquired intra-scene relations (as detailed in Section 5.3.2).  

Definition 12 ($S^{3}$ Method). The $S^{3}$ method is a model-matching technique designed to extract quantitative relations from AWPs leveraging $S^{3}$ models.  

When applying the $S^{3}$ method to extract quantitative relations from AWPs, two distinct pools of $S^{3}$ models must be prepared. For example, the intra-scene pool of $S^{3}$ models is manually designed based on the five datasets used in this study (Table 3). The design process begins by calculating the vector similarity between sentences from different scenes within the datasets, with vectors generated using BERT (Bidirectional Encoder Representations from Transformers, a widely used language representation model designed to understand the context of words in sentences, proposed by Devlin et al. (2019)). Sentences with  

Table 1 Demonstrating the superiority of the $S^{3}$ method through a comparison of relation acquisition samples obtained using $S^{3}$ and $S^{2}$ methods.   

![](images/Peng_2025_Table1.png)


| Model name | Scene label | Patterns of “P,K,L”; Q; R | Matched text | Acquired relation |
| --- | --- | --- | --- | --- |
| S 2 | – | “n v m [more] n [than] n”; n→a, m→b, n→c, n→d; a=°b°c+d | Miya has 18 more peanuts than Jose | Miya=18×peanut+Jose |
| Intra-Scene S 3 | Part-Whole | “{part} v m n “ {part}→a, m→b, n→c; Part(a)=°bxc | Apples weigh 100 kilograms | Part(Apple)=50×kg |
| Intra-Scene S 3 | Change | “n [gain] m n”; n→a, m→b, n→c; Gain(a)=bxc | Ken later bought 5 more candies | Gain(Ken)=5×candy |
|  | Rate | “[how many] [un] [of] n [each] [ud]”; {ud}→a, n→b, [ud]→c; Rate(b)=?xUN(a)/UD(c) | how many kilograms of fruits are in each box | Rate(fruit)=?xUN(kg)/UD箱 |
| Inter-Scene S 3 | Part-Whole &amp; Rate | “{whole} v m [uni]”; {whole}→a, m→b; Whole(a)=Rate(a)×b | All fruits are divided into 5 boxes | Whole(fruit)=Rate(fruit)×5 |
|  | Change &amp; Change | “[how many more] n [lef1] [than] [lef1] * [now]”; n→a, [lef1] * b, [lef1] * c; Left(b)=Left(c)+?xa | How many more candies does Ken have than Leo now | Left(Ren)=Left(Leo)+?×candy |

Note: In this table, the pattern "P, K, L" refers to the sequential pattern of POS (Part-Of-Speech), keywords, and scene roles. For the pattern instances, "n v m ..." represents the 'OS pattern, "$|k|$" indicates the presence of a keyword, and "$|l|$" refers to a role in scene. (In the last model, "$|left|$" and "$|left|$" refer to the "left" roles originating from two "Change" scenes.)  

high similarity are then analyzed, and patterns of (P, K, L) are manually extracted to summarize the models.  

These two pools are specifically used to identify relations within a single scene (intra-scene) and from a pair of scenes (inter-scene). Consequently, the relations extracted by the intra-scene and inter-scene $S^{3}$ models pertain either to an individual scene or to a pair of scenes (a scene pair), respectively.  

To illustrate the evolution of the models in detail, Table 1 presents examples that compare the $S^{2}$ and $S^{3}$ models. The $S^{2}$ model acquires relations from the entire problem text, whereas the $S^{3}$ model engages in relation acquisition only when the model and the cluster of sentences do match their types of scenes. Additionally, while the $S^{2}$ model focuses on matching POS and keywords, the $S^{3}$ model extends this by also considering the matching of roles in scene. For example, in the last sentence "How many more candies does Ken have than Leo now" in Table 1, the $S^{2}$ model acquires the relation "Ken=Leo+?×Candy", while $S^{3}$ model acquires the relation "Left(Ken)=Left(Leo)+?×candy", where "Roletbody") indicates that the "Entity" plays the "Role" in that particular scene. This advancement enables the $S^{3}$ model to simultaneously acquire both explicit and implicit relations.  

# 4.3. Scene-guided symbolic solver  

The methods for acquiring relations described above can collectively be called problem understanding, aimed at obtaining a relation set. The results constitute intra- and inter-scene relations acquired by the $S^3$ method, forming the instance of Scene Relation Set. To transform a Scene Relation Set into a Solution, a Scene-Guided Symbolic Solver is proposed, which integrates scene knowledge into the symbolic solver introduced in Yu et al. (2023). This solver operates through two primary modes: intra-scene inference and inter-scene inference. The inference process alternates between these modes iteratively, using a buffer to exchange results between them.  

The intra-scene inference mode focuses on each set of intra-scene relations to deduce unknown quantities. This process involves the following steps:  

(1) Update the unknown quantities in the intra-scene relation set using the results stored into the buffer. This ensures that all known values are incorporated into the current inference step.

(2) Symbolize all explicit and implicit relations within the set to form a system of equations.

(3) Solve the acquired system of equations to determine the unknown quantities within the scene.  

(4) Store the found quantities in the buffer for future use and log the inference actions in the sequence of operations. An "inference action" refers to the specific combination of relations used to infer a new quantity, with each equation corresponding to a particular relation.  

The inter-scene inference mode operates as follows:  

(1) Update the unknown quantities in the inter-scene relation set with values from the buffer.

(2) Symbolize all relations in the inter-scene relation set to form a system of equations.

(3) Solve the system to determine the unknown quantities.

(4) Store any newly inferred quantities in the buffer and log the inference action.  

The alternating process between intra-scene and inter-scene inference continues iteratively, with the buffer enabling the transfer of inference results, until all unknowns in the problem are resolved.  

# 5. Scene-attention relation-centric algorithm  

This section presents the Scene-Attention Relation-Centric (SARC) algorithm for solving AWPs by adopting the state transform graph designed in Section 3 and implementing the methods presented in Section 4, which executes the third phase of the three-phase scheme.  

# 5.1. The algorithm overview  

The proposed Algorithm 1 has four steps. The first step is to transform the problem text into the Scene and POS Annotation, including scene parsing and POS annotation. The second step is to acquire the Scene Relation Set by the $S^3$ method. The first and second step together finishes the problem understanding. The third step is the symbolic solver, which aims to infer the Scene Relation Set and record the algorithmic actions. The last step, solution generation, can be achieved by converting the algorithmic action through the fixed solution template.  

# 5.2. Acquiring scene and POS annotation  

BERT is selected to convert problem text into a sequence of vectors, based on its effectiveness for this task in related studies (Liang et al., 2022; Iyu et al., 2023; Yu et al., 2023). The text of any problem can be segmented into a sequence of words $P = \{w_i\}_{i=1}^n$ on a word-by-word basis, or it can also be divided into multiple sentences $P = \{s_i\}_{i=1}^m$ by punctuation. BERT then encodes the word sequence $P$ to a  

Algorithm I: A Scene-Attention Relation-Centric Algorithm for Solving AWPs.   

![](images/Peng_2025_Algorithm1.png)

vector sequence $H$, and then acquire the hidden $h(s_i)$ for each sentence $s_i$ (Reimers & Gurevych, 2019):  

$$
H = \mathrm { B E R T } ( P ) = \{ h ( w _ { i } ) \} _ { i = 1 } ^{n}
$$

$$
h ( s _ { i } ) = a v g ( \{ h ( w _ { j } ) \} _ { w _ { j } \in s _ { i } } )
$$

A two-layer neural network is used to perform multi-label classification, predicting for each sentence $s_i$ the probability $\hat{c}_i(s_j)$ of its scene type being $t$. Each scene type is treated as an independent label, with the sigmoid activation function applied to the output:  

$$
u ( s _ { i } ) = \mathrm { R e L U } ( W _ { u } \cdot h ( s _ { i } ) + \beta _ { u } )
$$

$$
\hat { c } _ { t } ( s _ { i } ) = \sigma ( W _ { t } \cdot u ( s _ { i } ) + \beta _ { t } )
$$

The use of multi-label classification over multi-class classification enables a sentence to be associated with multiple scene labels when applicable. This approach allows sentences that pertain to more than one scene to be identified, effectively capturing overlaps and shared contexts across scenes. For example, in Fig. 3, the sentence "All fruits are divided into 5 boxes" relates to two scenes: "fruits" corresponds to the role "Whole" in the "Part-Whole" scene, while "boxes" corresponds to the role "Unit-Denominator" in the "Rate" scene. Such sentence is labeled with multiple labels in the classifier. In this paper, we refer to such sentences as "linking sentences", which serve as the source of inter-scene relations, facilitating the transfer of quantities between different scenes.  

A concat-binary classification network, based on sentence-BERT (Reimers & Gurevych, 2019), is used to determine whether pairs of sentences should be grouped into the same text cluster, the same instance of a scene. This process generates a continuous value $\delta(i,j)$ for a sentence pair $(s_i, s_j)$ in the range [0, 1], representing the probability that the two sentences belong to the same cluster:  

$$
h ( i , j ) = \mathrm { C o n c a t } [ h ( s _ { i } ) : h ( s _ { j } ) : ( h ( s _ { i } ) - h ( s _ { j } ) ) ]
$$

$$
v ( i , j ) = \operatorname { R e L U } ( W _ { v } \cdot h ( i , j ) + \beta _ { v } )
$$

$$
\hat { \sigma } ( i , j ) = \sigma ( W _ { o } \cdot v ( i , j ) + \beta _ { o } )
$$

Two cross-entropy loss functions are used to train the above two neural networks, where $C$ refers to the number of types of scenes and $i$ refers to the $i$th type of scenes:  

$$
L o s s ( c , \hat { c } ) = - \frac { 1 } { C } \sum _ { i = 1 } ^{C} ( c _ { i } \log \left( \hat { c } _ { i } \right) + \left( 1 - c _ { i } \right) \log \left( 1 - \hat { c } _ { i } \right) )
$$

$$
L o s s ( o , \hat { o } ) = - ( o \log ( \hat { o } ) + ( 1 - o ) \log ( 1 - \hat { o } ) )
$$

Procedure I:Scene Parsing and Annotation   

![](images/Peng_2025_Procedure1.png)

The two loss functions are designed for single sentences or a sentence pair. During training, all sentences within a single AWP are grouped into one batch for loss calculation and back-propagation. Details of the training process and the results for these two networks are provided in Appendix.  

After classifying the sentences, they are grouped into clusters according to the scene type, as determined by the neural network's output. Each cluster contains multiple sentences along with a corresponding scene type. It is important to note that the sentences within each cluster are arranged in the same sequence as they appear in the original text.  

For POS annotation, N-LTP (Che et al., 2021) is used for Chinese texts and spaCy (Honnibal et al., 2020) is used for English texts. Both tools leverage the latest Transformer-based models.  

All sentences labeled with types of scenes and their POS tagging sequence form the text with scene and POS annotation. The details of the procedure are presented in Procedure 1, where $FFN_{mc}$ (Eq. (4)) and $FFN_{bc}$ (Eq. (7)) represent multi-label classification and concat-binary classification neural networks respectively.  

# 5.3. Acquiring scene relation set  

The instance of Scene Relation Set is acquired using the $S^{3}$ method for a given AWP. A pool of intra-scene $S^{3}$ models is used to obtain the relations within a single scene, while a pool of inter-scene $S^{3}$ models is used to derive the relations from sentences labeled with pairs of scenes.  

In the implementation, a double-pointer approach is used to align the (P, K, L) components of the $S^3$ model with the annotated sentence. The pointer in the sentence advances word by word, while the pointer in the model only advances when the word in the sentence matches the item indicated by the model's pointer: When the model's pointer is on a POS tag (e.g., "n" for noun, "v" for verb), it matches the corresponding  

Procedure II: Acquiring Intra-Scene Relations   

![](images/Peng_2025_Procedure2.png)

POS of the word in the sentence; when the pointer is on a keyword (e.g., "[each]"), it matches the word itself in the sentence; and when the pointer is on a role (e.g., "Part"), the algorithm first assigns roles to the words in the sentence using different strategies based on the scene type, and then matches the assigned role with the role in the model. The matching process for POS and keywords is the same for intra-scene and inter-scene models, while the role matching process differs, as discussed in the next Section 5.3.1 and Section 5.3.2, respectively.  

# 5.3.1. Intra-scene relation acquisition  

The intra-scene $S^{3}$ model acquires intra-scene explicit relations by matching sentences in Scene and POS Annotation. Following the completion of explicit relation acquisition, it instantiates an implicit relation by matching the scene-related implicit knowledge to the entities in the explicit relations through the roles. This process is delineated by Procedure II.  

In Step II-2 (acquiring explicit relations) of Procedure II, three strategies are employed to assign roles in sentence: (a) for the sentence in scene "Part-Whole", it first extracts words annotated by noun "n" in the POS sequence, then uses WordNet (Miller, 1995) to detect hyponymy and hypernym relations among these words, and assigns roles to the words based on these relations; (b) for the sentence in scene "Change", it initially extracts words annotated by verb "v" in the POS sequence, then employs the verb classifier developed by Hosseini et al. (2014) to assign roles to the words that represent different types of action; (c) for the sentence in scene "Rate", it first extracts words annotated by noun "n" in the POS sequence, then uses the Unit-Dependency Graph developed by Roy and Roth (2017) to assign roles to the words that represent different units. Finally, the roles assigned to words in the sentence according to the above strategy would be matched with the role in intra-scene $S^3$ model.  

In Step II-3 (acquiring implicit relations) of Procedure II, the knowledge relevant to the scene (as mentioned in Fig. 2) are used to obtain the implicit relation. These knowledge model the relations between  roles within a scene and has been well-formalized in prior related research (Hosseini et al., 2014; Mitra & Baral, 2016; Roy & Roth, 2018) to ensure its applicability to problems in the dataset. Specifically, our algorithm acquires implicit relations through two main steps: First, the scene parsing procedure identifies the type of scene for text, which indicates the scope of use of scene knowledge; Second, while the $S^3$ model extracts explicit relations, it assigns different roles to entities in the problem text, which correspond to roles in scene knowledge. By mapping the entities in explicit relations to the roles in scene knowledge through these correspondences, the knowledge can be instantiated as implicit relations.  

![](images/Peng_2025_Procedure3.png)

# 5.3.2. Inter-scene relation acquisition  

As mentioned earlier, some sentences may simultaneously belong to two different scenes. These are referred to as "linking sentences" in this paper. Such sentences describe the transitional relation between the pair of scenes. For example, in Fig. 2, "How many more candies does Ken have than Leo now?" is a linking sentence, describing the relation "Left(Ken) = Left(Leo) + ?xCandy", where "Left(Ken)" and "Left(Leo)" are derived from two distinct scenes. Our algorithm uses the Inter-Scene $S^3$ model to capture these relations, with the specific processes outlined in Procedure III.  

In Step III-2 (model matching) of Procedure III, the method for assigning roles differs from that in intra-scene: the inter-scene model matches "linking sentences", which contain entities from a pair of scenes, and whose roles have already been identified in intra-scene relation acquisition (Procedure II). Therefore, the inter-scene model only needs to match L by determining the corresponding entities in intra-scene relation set, without using different methods based on the scene type. For example, in Table 2, the L of the last model "[how many more] n {left} [than] {left}*[now]" consists of "[left]!" and "[left]^{*}". The procedure determines two different entities associated with "Left" from the previously acquired intra-scene relation set and fills them into the inter-scene relation. Note that in the inter-scene models, "[left]" and "[left]^{*}"] simply distinguish that these entities come from different scenes.  

![](images/cd9a97d342e4c4713fbedd16e5f2896fe639caa6e1ad75dd947c5ac7404828cd_39.jpg){width=39%}  

# 5.4. Inferring scene relation set  

Procedure IV outlines the steps of the Scene-Guided Symbolic Solver follows to infer various sets of relations.  

Before the loop begins, our algorithm first identifies the target unknown quantity by locating the question token "?" in the relation set (the $S^{3}$ model has already converted interrogative pronouns in the sentence to "?" in the relation). In relation symbolization, an "entity-symbol" mapping dictionary is first constructed based on the entities appearing in the relation set. The entities in the relation set are then replaced with their corresponding symbols, producing a system of equations. This "entity-symbol" mapping dictionary can later be used to map the equation-solving process back to the relation inference actions. For example, the system of equations "a = 3*c, b = 5*c, a + b = d" can be solved to get "d = 8*c", and this process can be mapped back to the relation inference actions {Have(Ken) = 3×candy, Gain(Ken) = 5×candy, Have(Ken) + Gain(Ken) = Left(Ken)} → {Left(Ken)=8×candy}. In the equation-solving step, the paper uses the Python-based library "SymPy" (Meurer et al., 2017), which can solve systems of linear equations with single or multiple unknowns. Note that this paper focuses on AWPs in basic education, and the problems do not involve nonlinear equations.  