# IEIR 2026 Paper Restructure Blueprint

## Document purpose

This document defines the argument, section structure, paragraph responsibilities, evidence requirements, display plan, and rewrite boundaries for the IEIR 2026 conference paper. It is the planning layer to be confirmed before the targeted rewrite of paper_draft.txt.

- Target: IEIR 2026 algorithm/system paper.
- Format: IEEE two-column, 6--8 pages.
- Main-text target: approximately 3,400--3,700 English words, excluding references.
- Paper focus: symbolic reasoning through Trigonometric Meta-Models and TMM-guided Decoupled Inference.
- Evidence policy: no numerical result is inserted until the frozen evaluation supports it.
- Rewrite boundary: the English draft, Chinese draft, figures, and journal blueprint remain unchanged at this stage.

---

## 1. Locked research and writing decisions

1. The conference paper focuses on symbolic reasoning rather than uniform representation.
2. The principal method contributions are the formalization of Trigonometric Meta-Models (TMMs) and dynamic TMM-guided Decoupled Inference Strategy (DIS).
3. The paper does not introduce or use TrigSolver as the name of the complete method.
4. The paper does not introduce Trig-URM or claim a representation contribution.
5. The symbolic solver receives an understood state as its reasoning interface.
6. The understood state is formed from raw text by a lightweight problem-understanding front end. Its formation is explained briefly, but the front end receives no method name, is not listed as a contribution, and is not evaluated independently.
7. The front end may normalize formulas and map explicitly stated expressions, variables, angle conditions, constraints, and solving goals. It may not solve the problem, infer hidden mathematical facts, or determine the final answer.
8. The method is organized around four cross-task symbolic operations:
   - angle and expression normalization;
   - equivalence-preserving transformation;
   - constraint and branch reasoning; and
   - periodic completion and validation.
9. These four phrases are descriptive academic language, not newly branded modules.
10. The five problem categories are evaluation strata, not five independent algorithms.
11. DIS dynamically retrieves applicable TMMs and performs bounded search over validated state transitions. It is not described as a fixed family-to-handler table.
12. The paper uses a compressed DPEA structure: two necessary definitions, one process, one running example, and one high-level algorithm.
13. The empirical package contains:
   - one frozen 50-problem text benchmark, with 10 problems in each evaluation stratum;
   - Direct LLM and LLM + generic CAS baselines;
   - the full TMM-guided DIS method;
   - ablations without periodic completion and without exact validation.
14. No fixed-route or no-DIS ablation is required for this conference version.
15. Therefore, the paper may demonstrate the effectiveness of the complete method but may not claim that the experiment causally isolates the independent gain of dynamic DIS.
16. Problem-level accuracy is primary, with abstention counted as incorrect.
17. The paper does not claim multimodal solving, complete trigonometry coverage, arbitrary transcendental solving, formal-proof completeness, or demonstrated educational effectiveness.
18. TrigSolver and Trig-URM are reserved for a later journal paper that will cite and extend the conference TMM/DIS contribution.

---

## 2. Paper identity and argument anchor

### 2.1 Recommended working title

> **Meta-Model-Guided Symbolic Reasoning for Trigonometric Function Problems**

This title foregrounds the actual conference contribution, remains searchable, and avoids the self-evaluative word novel.

If a traditional method-title form is preferred:

> **A Meta-Model-Guided Symbolic Reasoning Method for Solving Trigonometric Function Problems**

The shorter first title is recommended.

### 2.2 One-sentence paper argument

> **Given an understood state derived from a raw text problem, the proposed method dynamically retrieves and composes Trigonometric Meta-Models to coordinate angle and expression normalization, equivalence-preserving transformation, constraint and branch reasoning, and periodic completion and validation across representative trigonometric function problems.**

### 2.3 Exact capability gap

> **Existing formal, language-model, and generic computer-algebra approaches can perform individual trigonometric operations, but they do not jointly specify when a domain-specific operation is applicable, how its verified result changes the current reasoning state, or when a locally correct result satisfies the requested global answer.**

The paper responds to a reasoning-control gap, not a representation gap.

### 2.4 Evidence-bounded performance statement

Use only after the frozen experiment:

> **On a frozen 50-problem pilot benchmark, TMM-guided DIS achieves [EVIDENCE NEEDED: correct/50 and percentage] problem-level accuracy, with abstentions counted as incorrect.**

If the score exceeds 60%, the threshold claim must still name the benchmark size and Raw setting.

### 2.5 Reader and reader-question order

- Relevance: trigonometric answers can be locally plausible yet globally wrong because of conditions, branches, and periodicity.
- Novelty: TMMs formalize bounded trigonometric actions, while DIS composes them through state-conditioned reasoning.
- Trust: frozen evaluation, two relevant baselines, targeted completion/validation ablations, exact answer evaluation, and failure accounting.
- Reuse: the TMM contract, operation grouping, dynamic inference process, and high-level algorithm are reproducible.
- Meaning and boundary: the study is a text-based pilot and does not establish universal coverage or educational effectiveness.

---

## 3. Terminology ledger

| Canonical term | First-use definition | Avoid or restrict | Locked decision |
| --- | --- | --- | --- |
| trigonometric function problem | a direct problem whose principal object is a trigonometric function or expression | five-family problem in the title or central claim | The five categories appear only as evaluation strata. |
| understood state | an intermediate symbolic state sufficient for the solver to continue without revisiting the original problem | calling it a new representation model | Use \(U^{(0)}\) for the initial understood state. |
| candidate understood state | the front-end output before structural and grounding checks | claiming semantic infallibility | Use \(\widehat U^{(0)}\) only when needed. |
| problem understanding | the supporting process that converts raw text into a candidate understood state | a branded parser, model, or contribution | Describe briefly in Problem Formulation and Method Overview. |
| reasoning state | a state produced after TMM execution | shifting among understood/problem/reasoning state | Use \(U^{(j)}\), \(j\geq1\), during inference. |
| Trigonometric Meta-Model (TMM) | a bounded action with prerequisites, operation, state update, and validation | handler, rule, and module as synonyms | Expand once, then use TMM. |
| TMM library | the set \(\mathcal L\) of available TMMs | solver families or task handlers | Organize by the four operation groups. |
| Decoupled Inference Strategy (DIS) | the controller that retrieves and composes TMM transitions | generic or fixed routing | Use TMM-guided DIS after first expansion. |
| controlled symbolic executor | the allowlisted CAS interface invoked inside TMM operations | describing the CAS as the solver | Report CAS and version in settings. |
| periodic completion and validation | construction and checking of the requested global periodic answer | periodicity as answer formatting only | Strongest trigonometric mechanism. |
| exact validation | symbolic expression, set, periodic, and option equivalence checks | numerical agreement as proof | Sampling may reject but not accept a symbolic claim. |
| explicit abstention | an unresolved outcome with a stable reason | inconsistent failure terminology | Abstention counts as incorrect. |
| proposed method | the Raw-input pipeline whose reasoning core is TMM-guided DIS | TrigSolver | Use TMM-guided DIS (ours) in tables. |
| problem-level accuracy | correct frozen problems divided by all frozen problems | conditional accuracy as headline | Report correct/50 and percentage. |

Terms excluded from the IEIR manuscript and reserved for the journal paper:

- TrigSolver;
- Trigonometric Uniform Representation Model;
- Trig-URM;
- uniform trigonometric representation;
- representation-quality contribution claims.

---

## 4. Full-paper argument chain

Reliable mathematical solving requires valid global answers

→ trigonometric problems combine exact transformations, constraints, branches, and repeated periodic structures

→ existing approaches can execute local operations but do not consistently control applicability, state effects, completion, and validation

→ the unresolved gap is a domain-specific symbolic process that composes bounded operations across different trigonometric goals

→ an understood state supplies the non-contributory reasoning interface

→ TMMs formalize bounded trigonometric actions

→ TMM-guided DIS dynamically retrieves, executes, validates, and composes these actions until the goal is satisfied or the method abstains

→ a frozen pilot evaluation tests end-to-end accuracy, periodic completion, exact validation, and realistic failure boundaries

→ the result establishes a bounded reasoning method for representative text-based trigonometric function problems.

### Claim hierarchy

- **Central claim:** TMM-guided DIS provides a structured and verifiable symbolic reasoning process for representative text-based trigonometric function problems.
- **Knowledge-unit claim:** a TMM packages applicability, operation, state update, and local validation in one bounded action.
- **Reasoning-process claim:** DIS dynamically composes applicable TMMs over the current state and goal.
- **Cross-task claim:** the same TMM library supports four recurring operation groups without defining five independent solvers.
- **Mechanism claim:** periodic completion prevents base-period results from being reported as complete global answers.
- **Reliability claim:** exact validation rejects non-equivalent, incomplete, or ambiguous outputs rather than forcing coverage.
- **Empirical claim:** the full method exceeds 60% on the frozen 50-problem benchmark only if the evidence supports the threshold.

### Contribution wording

1. **Trigonometric Meta-Models**

   > We formulate Trigonometric Meta-Models as bounded symbolic actions that associate structural prerequisites with a trigonometric operation, a state update, and a local validation condition.

2. **TMM-guided symbolic reasoning**

   > We develop a TMM-guided decoupled inference process that dynamically retrieves applicable meta-models, explores validated state transitions, and terminates with either a verified answer or an explicit abstention.

3. **Pilot validation**

   > We evaluate the proposed method on a frozen 50-problem benchmark against Direct LLM and LLM + generic CAS baselines, together with targeted ablations of periodic completion and exact validation.

The third item validates the method; it is not a dataset or representation contribution.

---

## 5. Proposed paper structure and display budget

| Section | Main responsibility | Target words | Main display |
| --- | --- | ---: | --- |
| Abstract | problem--gap--method--evidence--boundary | 180--200 | none |
| 1. Introduction | relevance, four requirements, exact gap, contributions | 540--610 | first reference to Fig. 1 |
| 2. Related Work | formal reasoning, LLM/CAS, state-action and DIS lineage | 300--370 | none |
| 3. Problem Formulation | task boundary, understood state, brief state formation, evaluation strata | 380--450 | none |
| 4. Meta-Model-Guided Symbolic Reasoning | TMM, dynamic DIS, four operations, example, execution boundary | 1,000--1,100 | Fig. 1, Table 1, Algorithm 1, Fig. 2 |
| 5. Experiments | protocol, baselines, metrics, main result, two ablations, errors | 850--950 | Tables 2 and 3 |
| 6. Discussion and Conclusion | interpretation, limitations, bounded implication | 260--330 | none |
| **Total** |  | **3,510--4,010** | 2 figures, 1 algorithm, 3 tables |

The final manuscript should remain near 3,500--3,700 words by using the lower end of each range and routing implementation detail to the artifact.

---

## 6. Paragraph-level outline

Each paragraph has one primary rhetorical job. Evidence placeholders remain visible until verified.

### Title and Abstract

| ID | Job | Paragraph content | Evidence or boundary | Target |
| --- | --- | --- | --- | ---: |
| A0 | title | Name meta-model-guided symbolic reasoning and trigonometric function problems. | Do not use novel, TrigSolver, Trig-URM, unified representation, or a score. | one title |
| A1 | problem | State that trigonometric solving requires more than local calculation because correctness depends on conditions, branches, and periodicity. | No literature list. | 30--40 words |
| A2 | gap | State that existing formal, LLM, and CAS routes do not jointly control operation applicability, state update, completion, and validation. | Keep the gap bounded. | 35--45 words |
| A3 | approach | Introduce TMMs and TMM-guided DIS, including the TMM contract and dynamic composition process. | Mention understood state only as the input interface. | 45--55 words |
| A4 | operational coverage | Name the four cross-task symbolic operations in one sentence. | Do not list five evaluation strata. | 30--40 words |
| A5 | evaluation | State the frozen 50-problem benchmark, two baselines, and two ablations. | All systems receive the same Raw problems. | 30--40 words |
| A6 | evidence | Report correct/50, percentage, baseline differences, and one decisive ablation effect. | [EVIDENCE NEEDED: frozen results]. | 35--50 words |
| A7 | implication | State the bounded implication for text-based trigonometric symbolic reasoning. | No universal coverage or learning-effect claim. | 20--30 words |

Draft the Abstract only after Experiments and Discussion are stable.

### 1. Introduction

| ID | Job | Topic sentence and movement | Support and exclusions | Target |
| --- | --- | --- | --- | ---: |
| I1 | context/relevance | Automatic mathematical solving for intelligent education requires valid and inspectable answers. Narrow immediately to direct trigonometric function problems. | Educational relevance is motivation, not an evaluated outcome. | 115--135 words |
| I2 | technical bottleneck | Explain angle/expression normalization, equivalence preservation, constraint/branch reasoning, and periodic completion/validation. | Explain why local correctness may still produce a globally incomplete answer. | 135--155 words |
| I3 | exact gap | Synthesize restricted formal systems, free-form LLM reasoning, and generic CAS/tool pipelines. End with state-conditioned composition of bounded operations as the missing capability. | Do not claim that no prior trigonometric solver exists. | 145--165 words |
| I4 | approach/contributions | Mention the understood-state interface briefly, then foreground TMMs and dynamic TMM-guided DIS. State two method contributions and one validation point. | First reference to Fig. 1. State formation is not a contribution. | 145--165 words |

The Introduction must not open with the five evaluation categories or with a representation problem.

### 2. Related Work

Use three compact paragraphs without subsection headings if page pressure is high.

| ID | Job | Paragraph content | Closing distinction | Target |
| --- | --- | --- | --- | ---: |
| R1 | comparison | Trigonometric identity proving, formal reduction, and process-oriented reasoning. | Restricted proof tasks validate local transformations but do not cover all problem-level goals and global answer contracts. | 95--115 words |
| R2 | comparison | LLM mathematical reasoning, tool use, and computer algebra. | LLM fluency and CAS exactness are complementary, but neither specifies the complete domain-specific control process. | 105--125 words |
| R3 | intellectual lineage | State-action solving, understood states, relation-centric algorithms, function meta-models, and decoupled inference in prior TDF work. | This paper specializes the reasoning layer through trigonometric meta-models, branch handling, periodic completion, and exact validation. | 100--120 words |

The paper must acknowledge that understood-state and general DIS ideas precede this study. The conference novelty is their trigonometric specialization and operationalization.

### 3. Problem Formulation

#### 3.1 Task and scope

| ID | Job | Paragraph content | Evidence or boundary | Target |
| --- | --- | --- | --- | ---: |
| T1 | task definition | Define Raw input \(P=(t,\mathcal O)\) and output \(Y=(a,\mathcal S,\mathcal H,z)\). Explain mathematical-answer-first option matching and explicit abstention. | Keep only fields used later. | 90--110 words |
| T2 | scope | Define direct text-based trigonometric function problems and exclude triangle-dominant geometry, multimodal graphs, arbitrary transcendental systems, and unsupported proofs. | State the exact-validation boundary. | 75--90 words |

#### 3.2 Understood-state interface

| ID | Job | Paragraph content | DPEA role | Target |
| --- | --- | --- | --- | ---: |
| T3 | definition | **Definition 1 (Understood State).** Define \(U^{(0)}\) as an intermediate state containing the expressions, angle conditions, explicit constraints, and goal required by the solver without revisiting the original statement. | Inherited interface, not a representation claim. | 90--105 words |
| T4 | supporting process | Explain that formula preprocessing and constrained semantic mapping produce \(\widehat U^{(0)}\), followed by reference, schema, and grounding checks. The front end extracts explicit information only and abstains when no operational understood state can be formed. | One paragraph; no name, acronym, tuple, separate figure, contribution, or metric. | 95--115 words |
| T5 | evaluation scope | State that five common problem categories are used only to stratify the 50-problem evaluation. Describe their answer forms compactly in prose. | Do not create five method branches. | 65--80 words |

### 4. Meta-Model-Guided Symbolic Reasoning

#### 4.1 Overview

| ID | Job | Paragraph content | Display | Target |
| --- | --- | --- | --- | ---: |
| M1 | method overview | Trace Raw problem, supporting problem understanding, \(U^{(0)}\), TMM-guided DIS, controlled symbolic execution, validated answer, and abstention. | Place Fig. 1 here; the reasoning core occupies the center. | 100--120 words |
| M2 | boundary | Clarify that the front end does not solve and the CAS does not control the route. TMM-guided DIS owns operation selection, state progression, completion, and acceptance. | Prevent an LLM-wrapper or CAS-wrapper interpretation. | 80--95 words |

#### 4.2 Trigonometric Meta-Models

| ID | Job | Paragraph content | DPEA role | Target |
| --- | --- | --- | --- | ---: |
| M3 | definition | **Definition 2 (Trigonometric Meta-Model).** Define \(M_i=\langle I_i,P_i,O_i,U_i,V_i\rangle\): identifier, prerequisite, operation, update, and validation. | Primary knowledge-unit contribution. | 105--125 words |
| M4 | rationale | Explain that a TMM is smaller than a task solver and larger than a raw CAS call. It performs one reusable, bounded, checkable transition. | Motivate reuse across evaluation strata. | 80--95 words |
| M5 | organization | Introduce the four operation groups and representative TMMs. | Place compact Table 1 here; avoid a nine-row task inventory. | 70--85 words |

**Table 1 responsibility:** connect the four operation groups to representative TMMs, prerequisites, state effects, and validation duties. Its rows are operation groups, not benchmark categories.

#### 4.3 Dynamic TMM-guided DIS

| ID | Job | Paragraph content | DPEA role | Target |
| --- | --- | --- | --- | ---: |
| M6 | candidate retrieval | Define \(\mathcal M^{(j)}=\{M_i\in\mathcal L\mid P_i(U^{(j)})=\mathrm{true}\}\). Candidates are retrieved from the current state and unsatisfied goal rather than a family route. | Process. | 90--110 words |
| M7 | bounded search | Describe the candidate-state queue, goal-progress priority, transition budget, signatures, duplicate suppression, validation before commitment, and alternative expansion. | [AUTHOR DECISION: finalize priority and tie-breaking before prose rewrite]. | 120--145 words |
| M8 | termination | Define success as satisfying the requested answer conditions followed by final validation. Define stable abstention conditions. | Place Algorithm 1 after M8. | 80--95 words |

**Algorithm 1 responsibility:** summarize supporting state formation, dynamic retrieval, bounded exploration, validation, state update, success, and abstention. It must not contain category-specific handlers.

#### 4.4 Cross-task symbolic operations

| ID | Job | Paragraph content | Running-example duty | Target |
| --- | --- | --- | --- | ---: |
| M9 | mechanism | **Angle and expression normalization:** normalize angle conventions, variables, executable expressions, and compatible forms while retaining conditions. | Establish an executable state without solving. | 65--80 words |
| M10 | mechanism | **Equivalence-preserving transformation:** apply bounded identities and canonicalization only when prerequisites hold and equivalence can be validated. | \(U^{(1)}:\sin x+\cos x>1\rightarrow\sqrt2\sin(x+\pi/4)>1\). | 70--85 words |
| M11 | mechanism | **Constraint and branch reasoning:** reason within the active domain, preserve valid branches, and retain endpoints and exclusions. | \(U^{(2)}:\mathcal S_0=(0,\pi/2)\) within a base period. | 70--85 words |
| M12 | mechanism | **Periodic completion and validation:** lift base-period units, intersect the domain, remove exclusions, and verify equivalence and completeness. | \(U^{(3)}\) is the periodic set and \(U^{(4)}\) is terminal. | 80--95 words |

#### 4.5 Worked trace and execution boundary

| ID | Job | Paragraph content | Display | Target |
| --- | --- | --- | --- | ---: |
| M13 | example synthesis | Trace \(U^{(0)}\rightarrow U^{(1)}\rightarrow U^{(2)}\rightarrow U^{(3)}\rightarrow U^{(4)}\). Explain that these are transitions in one process, not separate solvers. | Place Fig. 2 here. | 90--105 words |
| M14 | reproducibility/boundary | State the expression grammar, allowlisted CAS operations, time/search budgets, unresolved-output policy, exact checks, and numerical-sampling boundary. | Versions and hashes belong in settings or artifact. | 90--110 words |

### 5. Experiments

The Results use the shortest evidence chain sufficient for the conference claims. Problem understanding and representation quality are not independently evaluated.

#### 5.1 Dataset and protocol

| ID | Job | Paragraph content | Evidence needed | Target |
| --- | --- | --- | --- | ---: |
| E1 | protocol | State source corpus, scope filter, text-only/single-target criteria, deduplication/grouping, development use, final freeze, and identical test inputs. | [EVIDENCE NEEDED: counts, hashes, freeze state]. | 110--130 words |
| E2 | composition/gold | State 50 problems, 10 per evaluation stratum, multiple-choice/open counts, structured exact Gold, and mathematical-answer-first option mapping. | Categories are evaluation strata only. | 90--105 words |

#### 5.2 Baselines, settings, and metrics

| ID | Job | Paragraph content | Evidence needed | Target |
| --- | --- | --- | --- | ---: |
| E3 | baselines | Define Direct LLM, LLM + generic CAS, and TMM-guided DIS (ours) under the same Raw inputs and evaluator. | [AUTHOR DECISION: model snapshots, prompts, retries, extraction policy]. | 100--120 words |
| E4 | implementation | Report front-end model, decoding, parser, CAS/version, TMM library, time/search budgets, identity depth, validation policy, and hashes. | No unspecified standard settings. | 90--110 words |
| E5 | metrics | Make problem-level accuracy primary, with abstention incorrect. Add per-stratum correct/10, coverage, applicable periodic completeness, and false-acceptance rate. | Latency and cost are secondary. | 80--95 words |

#### 5.3 Main comparison

| ID | Job | Paragraph content | Display/evidence | Target |
| --- | --- | --- | --- | ---: |
| E6 | core result | Open with full-method correct/50 and percentage, then compare with Direct LLM and LLM + generic CAS using absolute differences. | Table 2. [EVIDENCE NEEDED: frozen results]. | 95--115 words |
| E7 | heterogeneity/boundary | Report compact per-stratum correct/10 results and identify where branches or periodic answers remain difficult. | Avoid inference unsupported by 10 examples per stratum. | 75--90 words |

#### 5.4 Targeted ablations

| ID | Job | Paragraph content | Display/evidence | Target |
| --- | --- | --- | --- | ---: |
| E8 | completion mechanism | Compare Full with **without periodic completion**; distinguish base-period correctness from global completeness. | Table 3. [EVIDENCE NEEDED: overall and applicable-subset effects]. | 75--90 words |
| E9 | reliability mechanism | Compare Full with **without exact validation**; report accuracy, coverage, and false acceptance. | Table 3. [EVIDENCE NEEDED: effects]. | 75--90 words |

These ablations support periodic completion and exact validation only. They do not causally isolate dynamic DIS.

#### 5.5 Error and trace analysis

| ID | Job | Paragraph content | Evidence needed | Target |
| --- | --- | --- | --- | ---: |
| E10 | failure boundary | Group failures into state formation, unmet TMM prerequisites, exhausted search/no route, unresolved CAS output, completion failure, and validation failure. | [EVIDENCE NEEDED: failure counts]. | 85--105 words |
| E11 | concrete trace | Give one concise successful TMM trace and one conclusion-changing failure or abstention; identify the responsible stage. | Do not add a third qualitative figure. | 65--80 words |

### 6. Discussion and Conclusion

| ID | Job | Paragraph content | Boundary | Target |
| --- | --- | --- | --- | ---: |
| D1 | synthesis | Interpret evidence through the knowledge-unit/control division: TMMs specify local actions and DIS organizes them into a goal-directed process. | Do not repeat Table 2. | 95--115 words |
| D2 | trigonometric meaning | Explain that periodicity affects selection, branch construction, completion, and validation rather than final formatting alone. | Refer once to E8. | 75--95 words |
| D3 | limitations | Name pilot size, text-only input, front-end dependence, supported grammar/TMM library, and no pedagogical-effect evidence. | Reserve representation, multimodal solving, and wider coverage for future work. | 80--100 words |
| C1 | conclusion | Restate TMM and DIS, name decisive evidence, give a bounded implication, and close with scope. | No new mechanism, citation, or result. | 80--100 words |

If page space is tight, D3 and C1 may be combined, but the limitation sentence must remain.

---

## 7. Compressed DPEA closed loop

The paper uses one coherent DPEA loop rather than repeating it for every operation.

| DPEA element | Placement | Required content | Must not become |
| --- | --- | --- | --- |
| Definition | T3 and M3 | understood state as inherited interface; TMM as the new formal knowledge unit | a representation model or many decorative definitions |
| Process | T4 and M6--M8 | brief state formation; dynamic retrieval, bounded search, validation, update, termination | a parser paper or fixed five-category routing table |
| Example | M9--M13 | one state trace for \(\sin x+\cos x>1\) | several unrelated examples |
| Algorithm | after M8 | high-level state formation and TMM-guided DIS | low-level parsing, handlers, or CAS internals |

### Running-example state trace

| State | New verified content | Rhetorical duty |
| --- | --- | --- |
| Raw \(P\) | solve \(\sin x+\cos x>1\) over the stated real domain | show the original task without elaborating the parser |
| \(U^{(0)}\) | target relation, domain condition, and complete-set goal | show the understood-state interface |
| \(U^{(1)}\) | \(\sqrt2\sin(x+\pi/4)>1\) | show equivalence-preserving transformation |
| \(U^{(2)}\) | \(\mathcal S_0=(0,\pi/2)\) in a base period | show constraint and branch reasoning |
| \(U^{(3)}\) | \(\bigcup_{k\in\mathbb Z}(2k\pi,\pi/2+2k\pi)\) | show periodic completion |
| \(U^{(4)}\) | validated periodic answer satisfying the goal | show exact validation and termination |

### Algorithm 1 control-flow contract

1. Preprocess the Raw problem and construct a candidate understood state.
2. Apply reference, schema, and grounding checks, or abstain.
3. Initialize the candidate-state queue and visited signatures with \(U^{(0)}\).
4. Select the next state under the bounded search policy.
5. Return a verified answer if the solving goal is satisfied.
6. Retrieve all TMMs whose prerequisites hold.
7. Execute each admissible operation under the controlled CAS policy.
8. Validate the transition before adding the new state to the queue.
9. Record rejected transitions and stable failure causes.
10. Abstain if the queue is exhausted or the search budget is exceeded.

No evaluation-category branch should appear in Algorithm 1.

---

## 8. Figure, algorithm, and table placement

| Display | Placement | Single rhetorical responsibility | Required revision |
| --- | --- | --- | --- |
| Figure 1 | Section 4.1 after M1 | show the boundary between supporting front end, TMM/DIS core, controlled executor, and validated output | Remove TrigSolver and Trig-URM; render problem understanding as a small grey support block; place TMM library and DIS at the visual center; organize TMMs by four operations. |
| Table 1 | Section 4.2 after M5 | summarize how the four operations are realized by representative TMMs | Use four rows: operation group, representative TMMs, prerequisite/state effect, validation duty. |
| Algorithm 1 | Section 4.3 after M8 | show how DIS forms the initial state, retrieves, explores, validates, and terminates | Use a bounded state queue and visited signatures; no fixed routes or handlers. |
| Figure 2 | Section 4.5 after M13 | demonstrate a state-action trace from Raw problem to verified periodic answer | Replace Trig-URM labels with \(U^{(j)}\); show one DIS controller spanning the transitions. |
| Table 2 | Section 5.3 | report the frozen end-to-end comparison | Rows: Direct LLM, LLM + generic CAS, TMM-guided DIS (ours). Include correct/50, accuracy, coverage, and compact per-stratum counts. |
| Table 3 | Section 5.4 | isolate periodic completion and exact validation | Rows: Full, No periodic completion, No exact validation. Include accuracy, applicable periodic completeness, coverage, and false acceptance where defined. |

The current five-category scope table and nine-row TMM inventory table should not both remain. Table 1 replaces them with a four-group method summary, while the five strata appear compactly in E2 and Table 2.

---

## 9. Claim--evidence map

| ID | Claim wording allowed in the paper | Decisive evidence | Main-text location | Status and boundary |
| --- | --- | --- | --- | --- |
| CL0 | TMM-guided DIS provides a structured and verifiable symbolic reasoning process for representative text-based trigonometric function problems. | Frozen full-method result, baseline comparison, exact answer protocol, and bounded failures. | Abstract, I4, E6, D1, C1. | **Needs frozen evidence.** Do not generalize beyond the pilot. |
| CL1 | A TMM associates applicability, a bounded operation, state update, and local validation in one reusable knowledge unit. | Definition 2, Table 1 contracts, and worked trace. | M3--M5, M9--M13. | Formalization claim; a TMM is not a complete solver. |
| CL2 | DIS dynamically retrieves applicable TMMs and composes validated state transitions under a bounded search policy. | Process definition, Algorithm 1, logged traces, and example. | M6--M8, Algorithm 1, E11. | Mechanism claim. Without a no-DIS ablation, do not claim isolated causal improvement. |
| CL3 | The TMM library operationalizes four recurring symbolic requirements across the evaluation strata. | Table 1 mapping, representative cases, and per-stratum results. | I2, M5, M9--M12, E7. | Cross-task organization, not universal coverage. |
| CL4 | Periodic completion converts valid base-period units into complete periodic answers under the active domain and exclusions. | No-periodic ablation, applicable periodic completeness, and example. | M12--M13, E8, D2. | **Needs frozen ablation evidence.** Complete is bounded to supported contracts. |
| CL5 | Exact validation reduces acceptance of non-equivalent, incomplete, or ambiguous outputs. | Full versus No-validator accuracy, coverage, and false acceptance. | M14, E9, D1. | **Needs frozen ablation evidence.** No formal-proof completeness claim. |
| CL6 | The proposed method exceeds 60% problem-level accuracy on the frozen 50-problem benchmark. | Correct/50 with abstentions incorrect and both baseline comparisons. | A6, E6, C1. | **Publish only if achieved.** Always state benchmark size and Raw setting. |
| CL7 | Named and validated transitions provide a basis for solver diagnosis and future inspectable educational feedback. | TMM trace and stage-specific failure labels. | E10--E11, D3. | Use provides a basis for; no learning-effect claim. |

### Claims deliberately excluded

- the problem-understanding front end is novel;
- the paper introduces a uniform representation;
- the understood-state structure is superior to alternatives;
- dynamic DIS independently causes an accuracy gain;
- the five strata are solved by a proven universal algorithm;
- the method is complete for all trigonometric problems;
- the traces improve student learning.

---

## 10. Main-text evidence allocation

| Result or analysis | Evidence class | Main-text decision | Reason |
| --- | --- | --- | --- |
| Frozen full-method accuracy | core discovery | Abstract, Table 2, E6 | Defines whether the empirical target is met. |
| Direct LLM comparison | necessary support | Table 2 and E6 | Tests against free-form reasoning. |
| LLM + generic CAS comparison | necessary support | Table 2 and E6 | Tests whether tool access alone is sufficient. |
| Per-stratum correct/10 | heterogeneity/qualification | Compact Table 2 block or E7 | Shows whether the score is concentrated in one category; avoid overinterpretation. |
| No-periodic ablation | mechanism support | Table 3 and E8 | Direct evidence for periodic completion. |
| No-validator ablation | reliability support | Table 3 and E9 | Shows accuracy/coverage/false-acceptance trade-off. |
| Failure-stage counts | qualification | E10, compact | Defines the method boundary. |
| One successful trace | explanatory support | Figure 2 and E11 | Grounds the TMM and DIS definitions. |
| One failure or abstention | edge case/qualification | E11 | Prevents a universal-solving interpretation. |
| Problem-understanding field accuracy | non-central representation detail | Omit | The front end is not a contribution. |
| Oracle understood-state results | optional diagnostic | Omit unless later necessary | Raw evaluation is the confirmed protocol. |
| Fixed-route/no-DIS ablation | future robustness | Omit | The author chose a lighter evidence package. |
| Full prompts, hashes, row outputs, parser audit | provenance detail | Artifact or appendix | Needed for reproducibility, not the main argument. |
| Development iteration history | provenance detail | Omit | Development diagnostics are not frozen evidence. |

### Shortest sufficient Results evidence chain

Frozen protocol and fair Raw comparison

→ full-method correct/50 and baseline differences

→ compact per-stratum boundary

→ periodic-completion ablation

→ exact-validation ablation

→ dominant failures and one boundary case.

---

## 11. Current-draft migration and compression map

This table governs the later targeted rewrite of paper_draft.txt.

| Current material | Decision | Destination or replacement | Reason |
| --- | --- | --- | --- |
| Current periodicity-centered title | Replace | Recommended title in Section 2.1 | TMM-guided symbolic reasoning is central. |
| TrigSolver system name | Remove from IEIR | TMM-guided DIS, proposed method, or ours | Reserve TrigSolver for the journal. |
| Trig-URM and its six-tuple | Remove from IEIR | Understood-state Definition 1 and minimal interface prose | Reserve uniform representation for the journal. |
| Current Abstract | Rewrite last | A1--A7 | It centers representation and unsupported Raw/Oracle claims. |
| Current Introduction | Compress to I1--I4 | requirements -> reasoning gap -> TMM/DIS | Remove repeated representation and system descriptions. |
| Related Work: trigonometric reasoning | Retain and tighten | R1 | Reframe around operation composition and global-answer control. |
| Related Work: LLM/CAS | Retain and tighten | R2 | Remove Trig-URM-dependent claims. |
| Related Work: structured function solving | Retain as lineage | R3 | Acknowledge understood states, meta-models, and DIS. |
| Current input/output formulation | Retain and tighten | T1 | Keep answer construction, trace, and abstention. |
| Full-width five-category task table | Delete | T5 and compact Table 2 strata | Prevent a case-by-case appearance. |
| Periodicity-Aware Trig-URM subsection | Delete | T3--T4 | Replace with inherited understood-state interface and brief formation. |
| Periodic-set equation | Retain only if space permits | M12 or M14 | Treat as an answer/construction contract, not representation. |
| TMM five-tuple | Retain and foreground | M3 | Primary formal contribution. |
| Nine-row TMM inventory | Replace | Four-row Table 1 | Organize by cross-task operations. |
| Current DIS paragraph | Substantially rewrite | M6--M8 | Define dynamic retrieval and bounded state search. |
| Current Algorithm 1 | Replace control flow | after M8 | Use queue, signatures, alternatives, and abstention. |
| Controlled symbolic execution | Retain and compress | M2 and M14 | CAS is an executor, not the method. |
| Figure 1 | Retain after major revision | Section 4.1 | Remove TrigSolver/Trig-URM and center TMM/DIS. |
| Figure 2 | Retain after revision | Section 4.5 | Replace Trig-URM with \(U^{(j)}\) and one DIS controller. |
| Five research questions | Remove | Implicit E1--E11 chain | Too large for the confirmed package. |
| Raw/Oracle two-track evaluation | Remove from main paper | Single Raw protocol | Problem understanding is not separately evaluated. |
| Representation metrics and flat-state baseline | Remove | none | No representation claim in IEIR. |
| CAS-only Oracle baseline | Remove | Two confirmed baselines | Match the lean comparison package. |
| Broad six-row ablation table | Reduce | Table 3 with three rows | Full, No periodic completion, No exact validation. |
| Capability inventory | Compress | E7 and E10--E11 | Keep counts and one trace; avoid a second inventory. |
| Current five-paragraph Analysis | Compress | D1--D3 | Interpret TMM/DIS, periodicity, and limitations. |
| Missing Conclusion | Add | C1 | Close with method, evidence, implication, and boundary. |
| Chinese draft | Preserve until English approval | Later synchronization | Avoid two moving drafts. |

---

## 12. Claim repetition control

| Claim | Introduce | Demonstrate | Interpret | Synthesize | Delete/compress elsewhere |
| --- | --- | --- | --- | --- | --- |
| TMM + DIS central contribution | I4 | M3--M8, E6/E11 | D1 | C1 | Do not restate it at every Method opening. |
| four cross-task operations | I2 | Table 1, M9--M12, E7 | D2 | short clause in C1 | Do not list five categories beside them. |
| periodic completion | I2 | M12, Fig. 2, E8 | D2 | optional in C1 | Avoid periodicity-aware in every heading. |
| exact validation and abstention | I2/I4 | M14, E9/E10 | D1/D3 | optional in C1 | Do not repeat all failure codes. |
| understood-state interface | T3 | T4/M1 | limitation in D3 | none | Do not make it a contribution, representation section, or metric. |
| five evaluation strata | T5 | E2/E7 | optional scope in D3 | none | Remove from title, abstract method list, and contributions. |
| educational relevance | I1 | none | D3 | bounded outlook | Delete learning-effect claims. |

---

## 13. Planned rewrite sequence and approval gates

### Stage A: approve this blueprint

Author confirms or redirects:

- working title;
- understood-state boundary;
- TMM five-tuple;
- dynamic DIS description;
- four-operation organization;
- single Raw evaluation and lean ablations.

### Stage B: revise displays before prose

- redesign Figure 1 around the supporting front end, TMM library, DIS controller, CAS boundary, and four operation groups;
- redesign Figure 2 around \(U^{(0)}\rightarrow\cdots\rightarrow U^{(4)}\);
- rewrite Algorithm 1 as bounded state-space search;
- design compact Table 1.

The display logic determines the Method subsection order.

### Stage C: rewrite Problem Formulation and Method

Rewrite T1--T5 and M1--M14 first because they define the technical truth. Run terminology and notation checks before other sections.

### Stage D: finalize result-table schemas

Create empty Table 2 and Table 3 schemas with exact rows and metrics. Insert frozen values only after verification.

### Stage E: rewrite Experiments from evidence outward

Write E1--E11 after the frozen result allocation is stable. Report observations before interpretation.

### Stage F: rewrite Introduction and Related Work backward from evidence

Every central question in I1--I4 must receive an answer in E6--E11. Remove background that prepares no tested question.

### Stage G: write Discussion, Conclusion, Abstract, and final Title

Draft in this order:

1. Discussion and limitations;
2. Conclusion;
3. Abstract;
4. final title.

### Stage H: synchronize the Chinese draft

Update paper_draft_CN.txt only after the English argument and evidence are stable.

---

## 14. Assumptions and missing inputs

1. The final intended DIS supports dynamic candidate retrieval and bounded state-space search.
2. Exact state priority and tie-breaking will be fixed before Method prose.
3. The supporting front end uses formula preprocessing, constrained semantic mapping, and grounding checks, but has no paper-specific name.
4. The front end extracts explicit information only and does not determine hidden mathematical answers.
5. The main result uses a frozen 50-problem Raw test set, with 10 problems in each stratum and abstention counted as incorrect.
6. Direct LLM and LLM + generic CAS are the only required external baselines.
7. The main ablations are No periodic completion and No exact validation.
8. No Oracle, representation-quality, flat-state, fixed-route, or no-DIS result is required in the main conference paper.
9. Dataset counts, model snapshots, prompts, hashes, runtime parameters, scores, and failure counts remain [EVIDENCE NEEDED] until verified.
10. Development diagnostics will not be reported as frozen-test evidence.

---

## 15. Blueprint acceptance test

Before beginning the targeted rewrite, confirm that every answer is yes.

- Does the title foreground meta-model-guided symbolic reasoning?
- Is the exact gap about control and composition rather than representation?
- Is understood state an inherited interface rather than a new model?
- Is state formation explained briefly without a name, contribution, expanded subsection, or metric?
- Are TrigSolver and Trig-URM absent from the IEIR contribution and terminology?
- Is the TMM five-tuple the principal formal Definition?
- Does dynamic DIS retrieve TMMs from the current state and goal rather than a category?
- Are the four cross-task operations used to organize the method?
- Are the five categories confined to evaluation composition and reporting?
- Is there one compressed DPEA loop with one example and one algorithm?
- Does Algorithm 1 describe bounded state search rather than family routing?
- Does the experiment use the frozen 50-problem Raw setting with two baselines?
- Are the two ablations interpreted only for completion and validation?
- Does the paper avoid an isolated causal claim for dynamic DIS?
- Does every performance statement name dataset, metric, comparison, and setting?
- Are educational relevance and traceability stated without claiming educational effectiveness?
- Is the evidence chain short enough for a 6--8 page paper?
