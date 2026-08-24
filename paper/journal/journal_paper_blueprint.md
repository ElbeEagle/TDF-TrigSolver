# IEIR 2026 TrigSolver Paper Restructure Blueprint

## Document purpose

This document is the approved planning layer between the overall research narrative and the next rewrite of `paper_draft.txt`. It fixes the paper argument, paragraph responsibilities, evidence requirements, DPEA placement, and compression decisions before any prose is rewritten.

- Target: IEIR 2026 algorithm/system paper.
- Format: IEEE two-column, 6--8 pages.
- Main-text target: approximately 3,400--3,700 English words, excluding references.
- Status: structure for author confirmation; not a rewritten manuscript.
- Evidence policy: no experimental number is inserted until the frozen evaluation supports it.
- Rewrite boundary: the existing English draft, Chinese draft, and figures remain unchanged at this stage.

---

## 1. Locked research and writing decisions

The following decisions are fixed for the restructuring work.

1. The long-term TDF research line remains organized around two questions:
   - how mathematical problems should be represented; and
   - how reasoning should operate over that representation.
2. In this paper, Trig-URM answers the representation question and TMM-guided DIS answers the reasoning question.
3. Periodicity is the strongest trigonometric structure connecting the two contributions, but it is not the only long-term TDF research theme.
4. The method is organized around four cross-task operations:
   - angle and expression normalization;
   - equivalence-preserving transformation;
   - constraint and branch reasoning; and
   - periodic completion and validation.
5. These four phrases are descriptive academic language, not four newly branded modules.
6. The five benchmark categories are evaluation strata, not five independent end-to-end algorithms. They should appear only where task scope, dataset composition, and per-category results must be made reproducible.
7. DIS is a dynamic retrieval and bounded search process over validated TMM state transitions, not a fixed family-to-handler table.
8. The paper uses a compressed DPEA structure: formal definitions, one process description, one running example, and one high-level algorithm.
9. The main empirical package is intentionally small:
   - one frozen 50-problem test set, with 10 problems in each evaluation category;
   - Direct LLM and LLM + generic CAS baselines;
   - the full TrigSolver system;
   - ablations without periodic completion and without exact validation.
10. The canonical representation name is **Trigonometric Uniform Representation Model (Trig-URM)**.
11. Qwen or another LLM is a grounded semantic mapper, not the mathematical solver. The CAS is a controlled symbolic executor, not the overall solver.
12. The paper does not claim multimodal solving, complete trigonometry coverage, arbitrary transcendental solving, formal-proof completeness, or demonstrated educational effectiveness.

---

## 2. Paper identity and argument anchor

### 2.1 Recommended working title

> **TrigSolver: Uniform Representation and Meta-Model-Guided Decoupled Inference for Text-Based Trigonometric Function Problems** 

This is the most defensible working title because it foregrounds the two lasting method contributions and uses `Text-Based` to preserve space for later multimodal work. `Periodicity-aware` remains central in the abstract and method but does not need to constrain the title.

### 2.2 One-sentence paper argument

> **We show that explicitly representing angle semantics, symbolic transformations, constraints, and periodic-set structures in Trig-URM, and dynamically composing validated trigonometric operations through TMM-guided DIS, enables reliable symbolic solving across representative text-based trigonometric function problems.**

### 2.3 Evidence-bounded performance statement

Use the following form only after the frozen experiment is complete:

> **On a frozen 50-problem pilot benchmark, TrigSolver achieves [EVIDENCE NEEDED: correct/50 and percentage] problem-level accuracy, with abstentions counted as incorrect.**

The paper must not generalize this result to all trigonometric problems.

### 2.4 Reader and reader-question order

- Primary reader: researchers in intelligent mathematical problem solving, neuro-symbolic reasoning, and intelligent education.
- Relevance: direct trigonometric function problems require exact symbolic and set-valued reasoning.
- Novelty: Trig-URM and dynamic TMM-guided DIS make the relevant state and operations explicit.
- Trust: frozen evaluation, fair baselines, two targeted ablations, exact validation, and failure accounting.
- Reuse: formal representation, TMM transition contract, high-level algorithm, and released implementation details.
- Meaning and boundary: the method is a text-only pilot and does not establish broad trigonometry or educational-effect claims.

---

## 3. Terminology ledger

| Canonical term | First-use definition | Avoid or restrict | Locked decision |
| --- | --- | --- | --- |
| TrigSolver | the complete solving framework | multiple names for the full method | Use one system name throughout. |
| text-based trigonometric function problem | a direct trigonometric problem whose required input is textual | `five-family problem` in the title, abstract, or main method claim | The five categories are evaluation strata only. |
| Trigonometric Uniform Representation Model (Trig-URM) | the structured problem and reasoning state | `TRM`, `UFR`, `Trig representation`, or `Trig-URM model` used interchangeably | Expand once, then use `Trig-URM`. |
| Trigonometric Meta-Model (TMM) | a bounded trigonometric operation with prerequisites, an update, and validation | `handler`, `rule`, and `module` as synonyms for the same formal object | Use `TMM` for the formal operation; use `identity rule` only for a rule inside a TMM. |
| TMM-guided Decoupled Inference Strategy (DIS) | the dynamic retrieval and bounded search process over TMM transitions | `generic routing`, `fixed route`, `decoupled meta-model inference` | Use `TMM-guided DIS` after first expansion. |
| dynamic TMM retrieval and bounded state-space search | the operational mechanism of DIS | a new acronym or branded search name | Keep as descriptive technical language. |
| grounded semantic mapping | mapping explicit problem information into Trig-URM | `LLM reasoning`, `LLM solving` | State that the mapper cannot generate mathematical answers. |
| controlled symbolic executor | the allowlisted CAS interface called by TMMs | describing SymPy/CAS as TrigSolver itself | Mention the concrete CAS and version in implementation settings. |
| angle and expression normalization | normalization of angle conventions and executable expressions | capitalizing it as a named contribution | Descriptive cross-task operation. |
| equivalence-preserving transformation | transformation that retains mathematical equivalence under the recorded conditions | `identity solving` | Descriptive cross-task operation. |
| constraint and branch reasoning | reasoning over domains, intervals, branches, endpoints, and exclusions | `interval module` as an isolated solver | Descriptive cross-task operation. |
| periodic completion and validation | construction and checking of the requested global periodic result | `periodicity-aware` repeated in every paragraph | Descriptive cross-task operation and the strongest paper-specific mechanism. |
| complete periodic solution set | a set whose base units, period, domain, endpoints, and exclusions have been represented and checked | `complete solution` without a stated scope | `Complete` applies only to supported periodic-answer contracts. |
| exact validation | symbolic expression, set, periodic, and option equivalence checks | numerical agreement as proof | Numerical sampling may reject, but not accept, a symbolic claim. |
| explicit abstention | a structured unresolved outcome with a stable reason | refusal/failure/rejection used inconsistently | Abstention counts as incorrect in the primary metric. |
| Raw setting | original question to final answer | treating Raw and Oracle as equivalent end-to-end settings | Main end-to-end result. |
| Oracle setting | independently corrected Trig-URM to the same solver | calling Oracle an end-to-end result | Diagnostic result only. |
| problem-level accuracy | correct problems divided by all frozen test problems | conditional accuracy as the headline | Report both count and percentage; abstention is incorrect. |

---

## 4. Full-paper argument chain

```text
Intelligent mathematical solvers require valid and inspectable answers
    -> direct trigonometric problems combine angle conventions, symbolic
       equivalence, domain/branch constraints, and repeated periodic sets
    -> specialized proof systems, free-form LLM reasoning, and generic CAS
       pipelines each preserve only part of this problem-level structure
    -> the unresolved gap is an executable representation plus a reasoning
       process that can preserve and operate over these structures jointly
    -> Trig-URM represents the state, while TMM-guided DIS dynamically retrieves,
       explores, validates, and composes bounded symbolic transitions
    -> a frozen pilot evaluation tests end-to-end accuracy, baseline advantage,
       periodic completeness, validation behavior, and failure boundaries
    -> the result supports a bounded text-based trigonometric solver and provides
       a reusable basis for later multimodal and broader-coverage research
```

### Claim hierarchy

- **Central claim:** Trig-URM plus dynamic TMM-guided DIS provides a structured and verifiable basis for solving representative text-based trigonometric function problems.
- **Representation claim:** Trig-URM preserves the state needed for angle semantics, transformations, constraints, branches, goals, and periodic-set answers.
- **Reasoning claim:** TMM-guided DIS dynamically composes only applicable and locally validated trigonometric transitions.
- **Mechanism claim:** periodic completion prevents locally correct base-period results from being reported as complete global solutions.
- **Reliability claim:** exact validation prevents unresolved or non-equivalent outputs from being accepted merely to increase coverage.
- **Empirical claim:** the full system achieves more than 60% accuracy on the defined frozen 50-problem pilot benchmark, if and only if the final evidence supports this threshold.

---

## 5. Proposed paper structure and display budget

| Section | Main responsibility | Target words | Main display |
| --- | --- | ---: | --- |
| Abstract | shortest problem--method--evidence--boundary chain | 180--200 | none |
| 1. Introduction | relevance, structural bottleneck, exact gap, solution and contributions | 550--620 | first textual reference to Fig. 1 |
| 2. Related Work | mechanism-based positioning without a literature list | 300--380 | none |
| 3. Problem Formulation and Trig-URM | task boundary, evaluation strata, formal representation, periodic-set semantics | 480--560 | compact Table 1 |
| 4. TMM-Guided Decoupled Inference | DPEA process, dynamic search, four cross-task operations, execution boundary | 900--1,000 | Fig. 1, Algorithm 1, Fig. 2 |
| 5. Experiments | frozen protocol, baselines, metrics, main comparison, two ablations, errors | 850--950 | Tables 2 and 3 |
| 6. Discussion and Conclusion | interpretation, internal limitations, bounded implication | 260--330 | none |
| **Total** |  | **3,520--4,040** | 2 figures, 1 algorithm, 3 tables |

Compression target: keep the final manuscript near the lower half of the range. If the two figures and Algorithm 1 occupy substantial page area, prioritize approximately 3,500--3,700 words.

---

## 6. Paragraph-level outline

Each paragraph below has one primary rhetorical job. Evidence placeholders must remain visible until the corresponding experiment or source is verified.

### Title and Abstract

| ID | Job | Paragraph content | Evidence or boundary | Target |
| --- | --- | --- | --- | ---: |
| A0 | title | Name TrigSolver, uniform representation, meta-model-guided decoupled inference, and text-based trigonometric problems. | Do not include `complete`, `general`, `unified solving`, or an accuracy value in the title. | one title |
| A1 | problem/gap | State that trigonometric solving requires coordinated treatment of angle semantics, equivalence, constraints, branches, and periodic answers; local calculation alone is insufficient. | One or two sentences; no literature inventory. | 35--45 words |
| A2 | approach | Introduce TrigSolver and state the different responsibilities of Trig-URM and TMM-guided DIS. | Mention grounded semantic mapping and CAS only as support components. | 45--55 words |
| A3 | mechanism | Explain that DIS dynamically retrieves applicable TMMs, explores bounded validated transitions, and either satisfies the answer contract or abstains. | Do not list all TMM names. | 35--45 words |
| A4 | evaluation | State the frozen 50-problem scope, Direct LLM and LLM + generic CAS baselines, and Raw main setting. | Add Oracle only as a diagnostic setting. | 30--40 words |
| A5 | main evidence | Report full-system accuracy and the two decisive comparisons. | `[EVIDENCE NEEDED: correct/50, percentage, baseline deltas]`. | 30--45 words |
| A6 | mechanism evidence | Report the main effect of periodic-completion and validator ablations. | `[EVIDENCE NEEDED: periodic completeness, false acceptance/accuracy effects]`. | 25--35 words |
| A7 | implication/boundary | State the bounded implication for structured text-based trigonometric solving. | Do not claim full trigonometry coverage or learning gains. | 20--30 words |

Draft the abstract only after Sections 5 and 6 are stable.

### 1. Introduction

| ID | Job | Topic sentence and required movement | Support and exclusions | Target |
| --- | --- | --- | --- | ---: |
| I1 | context/relevance | Automatic mathematical solving for intelligent education requires mathematically valid and inspectable answers, not only fluent final responses. Narrow immediately to direct trigonometric function problems. | Avoid a broad history of intelligent tutoring. Educational relevance is motivation, not an evaluated outcome. | 120--140 words |
| I2 | technical bottleneck | Explain the four cross-task requirements in ordinary academic language: angle/expression normalization, equivalence preservation, constraint/branch reasoning, and periodic completion/validation. | Explain why a locally plausible answer can still be globally wrong. Do not introduce four new acronyms. | 130--150 words |
| I3 | exact gap | Synthesize three existing routes: specialized identity/formal systems, LLM reasoning, and generic CAS/neuro-symbolic pipelines. End with the unresolved capability gap: no shared executable state plus dynamic validated reasoning process across these requirements. | Treat prior work fairly. Avoid `no prior solver exists` unless the literature audit directly supports the bounded wording. | 150--170 words |
| I4 | approach/contributions | Introduce TrigSolver, give the representation-versus-reasoning division, state periodicity's paper-specific role, and list two method contributions plus one empirical validation point. | First reference to Fig. 1. Do not include detailed result numbers here. | 150--170 words |

The Introduction uses the `technical-challenge -> representation -> reasoning process` variant. It should not open with the five evaluation categories.

### 2. Related Work

Use three compact paragraphs without subsection headings unless the final IEEE layout has sufficient space.

| ID | Job | Paragraph content | Closing distinction | Target |
| --- | --- | --- | --- | ---: |
| R1 | comparison | Trigonometric identity proving and formal reduction: AutoTrig, TRIGO, and process-oriented trigonometric reasoning. | These works validate transformations in restricted formal settings but do not preserve the complete problem state needed by the paper's broader text-based scope. | 100--120 words |
| R2 | comparison | LLM mathematical reasoning, LLM + tool use, and CAS execution. | LLM fluency and CAS exactness are complementary, but direct composition does not by itself specify the state, operation applicability, global answer contract, or completion checks. | 110--130 words |
| R3 | intellectual lineage | Relation-centric TDF solving, uniform representation, and decoupled inference in earlier function-problem work. | TrigSolver inherits the representation/inference division while extending the state and operations to angle, branch, interval, and periodic-set structures. | 100--120 words |

Every cited claim must be verified against the original paper or official artifact before the prose rewrite is finalized.

### 3. Problem Formulation and Trig-URM

#### 3.1 Task and evaluation scope

| ID | Job | Paragraph content | Display/evidence | Target |
| --- | --- | --- | --- | ---: |
| T1 | task definition | Define input \(x=(t,\mathcal O)\) and output \(y=(a,\mathcal S,\mathcal H,z)\). Explain mathematical-answer-first option matching and explicit abstention. | Keep the tuple only if every output field is used later. | 100--120 words |
| T2 | scope/boundary | Define direct text-based trigonometric function problems and distinguish them from geometry problems using trigonometric ratios. State single-target and exact-validation boundaries. | Place compact Table 1 after this paragraph. | 90--110 words |

**Table 1 responsibility:** disclose the five evaluation strata, representative required operations, and answer forms. The caption must state that these categories stratify evaluation and do not define five independent algorithms.

#### 3.2 Formal representation

| ID | Job | Paragraph content | DPEA role | Target |
| --- | --- | --- | --- | ---: |
| T3 | definition | **Definition 1 (Trig-URM).** Define \(\mathcal U_{\mathrm{trig}}=\langle F,A,E,C,G,D\rangle\). Explain each component with one precise clause. | Definition | 130--150 words |
| T4 | design rationale | Explain why explicit problem information and derived mathematical facts must be separated. The mapper instantiates \((F,A,E,C,G)\); validated TMM transitions extend \(D\). The answer contract belongs to \(G\). | Connect the representation to dynamic TMM prerequisites and stopping conditions. | 90--110 words |
| T5 | formal substructure | Define the complete periodic-set semantics \(\mathcal S=\left(\bigcup_{k\in\mathbb Z}(\mathcal S_0+kT)\right)\cap\Omega\setminus\mathcal X\). Explain points, intervals, endpoints, domains, and exclusions. | This is a substructure of Trig-URM, not a third main contribution. | 100--120 words |
| T6 | example snapshot | Introduce the running inequality example and show its initial state \(D_0\): angle/domain information, target inequality, and complete-set goal. | Example preview; full transition trace appears in Section 4 and Fig. 2. | 55--70 words |

### 4. TMM-Guided Decoupled Inference

#### 4.1 Overview

| ID | Job | Paragraph content | Display | Target |
| --- | --- | --- | --- | ---: |
| M1 | approach overview | Trace the full pipeline from preprocessing and grounded semantic mapping to Trig-URM, dynamic DIS, controlled symbolic execution, completion, validation, and solved/abstained output. | Place Fig. 1 immediately after or at the top of this subsection. | 100--120 words |
| M2 | component boundary | Clarify that the semantic mapper extracts only explicit task information and references; all mathematical decisions begin from Trig-URM. The CAS executes allowlisted operations but cannot bypass DIS or validation. | Prevent reviewers from reading the contribution as an LLM wrapper or SymPy wrapper. | 80--100 words |

#### 4.2 Trigonometric Meta-Models

| ID | Job | Paragraph content | DPEA role | Target |
| --- | --- | --- | --- | ---: |
| M3 | definition | **Definition 2 (Trigonometric Meta-Model).** Define \(M_i=\langle id_i,P_i,O_i,U_i,V_i\rangle\), covering identity, prerequisite, operation, update, and validation. | Definition | 100--120 words |
| M4 | mechanism/rationale | Explain that a TMM is smaller than a task solver: it performs one bounded, checkable transformation and may be reused in different problem contexts. | Replace the current long nine-row TMM inventory table with compact prose and Fig. 1 labels. | 80--100 words |

#### 4.3 Dynamic retrieval and bounded search

| ID | Job | Paragraph content | DPEA role | Target |
| --- | --- | --- | --- | ---: |
| M5 | process | Define the candidate set \(\mathcal M^{(j)}=\{M_i\in\mathcal L\mid P_i(\mathcal U^{(j)}_{\mathrm{trig}})=\mathrm{true}\}\). State that DIS retrieves candidates from the current state rather than from a fixed problem-family route. | Process | 100--120 words |
| M6 | search mechanism | Describe the bounded state queue, goal-progress ranking, transition validation, state signatures, duplicate removal, transition budget, and alternative expansion after rejected transitions. | `[AUTHOR DECISION: finalize the exact queue priority and tie-breaking policy before prose rewrite.]` | 120--145 words |
| M7 | termination | Define success as satisfying the output predicates in \(G\) followed by final validation. Define stable abstention conditions for no route, budget exhaustion, unsupported structure, CAS timeout, periodic failure, or validation failure. | Place Algorithm 1 after M7. | 75--95 words |

**Algorithm 1 responsibility:** summarize dynamic TMM retrieval, bounded exploration, validation, state update, success, and abstention. It must not contain family-specific handlers.

#### 4.4 Cross-task symbolic operations

This subsection uses the four confirmed descriptions as explanatory categories, not named components.

| ID | Job | Paragraph content | Running-example state | Target |
| --- | --- | --- | --- | ---: |
| M8 | mechanism | **Angle and expression normalization:** normalize angle conventions, variable surfaces, executable ASTs, and task-compatible forms while retaining recorded conditions. | For the running example, identify radians and normalize the expression reference without solving it. | 70--85 words |
| M9 | mechanism | **Equivalence-preserving transformation:** apply bounded identities or canonicalization only when preconditions hold and equivalence can be validated. | \(D_1: \sin x+\cos x>1\rightarrow\sqrt2\sin(x+\pi/4)>1\). | 75--90 words |
| M10 | mechanism | **Constraint and branch reasoning:** solve within the applicable domain, preserve all branches, and retain interval endpoints and exclusions. | \(D_2: \mathcal S_0=(0,\pi/2)\) in one base period. | 75--90 words |
| M11 | mechanism | **Periodic completion and validation:** lift base units by the detected period, intersect the domain, remove exclusions, and verify equivalence and completeness. | \(D_3\) is the complete periodic set; \(D_4\) is the validated answer. | 80--95 words |

#### 4.5 Worked trace and execution boundary

| ID | Job | Paragraph content | Display | Target |
| --- | --- | --- | --- | ---: |
| M12 | example synthesis | Walk through \(D_0\rightarrow D_1\rightarrow D_2\rightarrow D_3\rightarrow D_4\) and explain that the operations share one state rather than forming independent solvers. | Place Fig. 2 here. | 90--110 words |
| M13 | reproducibility/boundary | State the supported expression grammar, allowlisted CAS operations, timeout, unresolved-output policy, exact equivalence checks, and numerical-sampling boundary. | Detailed versions and hashes belong in implementation settings or the repository. | 90--110 words |

### 5. Experiments

The experiment section uses the shortest evidence chain needed to support the claims. It should not repeat the full development history.

#### 5.1 Dataset and protocol

| ID | Job | Paragraph content | Evidence needed | Target |
| --- | --- | --- | --- | ---: |
| E1 | protocol | State the source corpus, direct-trigonometry scope filter, text-only/single-target criteria, deduplication and template grouping, development use, and final test freeze. | `[EVIDENCE NEEDED: final source counts, split hashes, frozen date/state]`. | 110--130 words |
| E2 | composition | State that the frozen test contains 50 problems, 10 in each evaluation stratum, and report multiple-choice/open composition. Explain that the strata measure coverage rather than define the method. | Report exact counts, not only percentages. | 85--100 words |
| E3 | annotation integrity | Describe independent Oracle-URM and mathematical Gold construction, structured expression/set/PeriodicSet answers, option mapping after mathematical Gold, and prediction-blind annotation. | Keep procedural detail concise; point to the artifact for the full protocol. | 90--110 words |

#### 5.2 Systems, settings, and metrics

| ID | Job | Paragraph content | Evidence needed | Target |
| --- | --- | --- | --- | ---: |
| E4 | comparison | Define Direct LLM, LLM + generic CAS, and TrigSolver-Raw under the same frozen inputs and answer evaluator. | `[AUTHOR DECISION: fix the baseline model snapshot, prompting budget, retries, and answer extraction policy.]` | 100--120 words |
| E5 | diagnostic | Define TrigSolver-Oracle as a diagnostic setting using the same downstream solver, not as an end-to-end baseline. | Retain one Oracle row or one compact sentence if page pressure is severe. | 55--70 words |
| E6 | implementation | Report semantic model snapshot, decoding, parser schema, CAS/version, time budget, search budget, identity depth, validation policy, and recorded hashes. | Use exact values; do not write `standard settings`. | 85--105 words |
| E7 | metrics | Make problem-level accuracy the primary metric, with abstention incorrect. Add per-stratum correct/total, coverage, periodic completeness on applicable problems, and false-acceptance rate. | Conditional accuracy, token cost, and latency are secondary and may be one sentence or artifact-only. | 80--100 words |

#### 5.3 Main comparison

| ID | Job | Paragraph content | Display/evidence | Target |
| --- | --- | --- | --- | ---: |
| E8 | core result | Open with the full Raw result, then compare against Direct LLM and LLM + generic CAS. Report correct/50, percentage, and absolute differences. | Table 2. `[EVIDENCE NEEDED: frozen Raw and baseline results]`. | 95--115 words |
| E9 | diagnostic result | Report the Raw--Oracle gap and use it only to locate the remaining semantic-mapping bottleneck. Include concise per-stratum correct/10 results. | Table 2 or one compact grouped block. Avoid inferential claims unsupported by 10 examples per stratum. | 80--100 words |

#### 5.4 Targeted ablations

| ID | Job | Paragraph content | Display/evidence | Target |
| --- | --- | --- | --- | ---: |
| E10 | mechanism result | Compare the full system with `without periodic completion`. State whether base-period correctness remains while global periodic completeness decreases. | Table 3. `[EVIDENCE NEEDED: overall and applicable-subset effects]`. | 75--90 words |
| E11 | reliability result | Compare the full system with `without exact validation`. Report accuracy, coverage, and false acceptance without treating increased coverage as improvement. | Table 3. `[EVIDENCE NEEDED: accuracy/coverage/false-acceptance effects]`. | 75--90 words |

Do not write that the two ablations causally prove the necessity of dynamic DIS. They isolate periodic completion and exact validation only.

#### 5.5 Error and boundary analysis

| ID | Job | Paragraph content | Evidence needed | Target |
| --- | --- | --- | --- | ---: |
| E12 | qualification | Group errors by semantic mapping, formula parsing, unmet TMM prerequisites, exhausted search/no route, unresolved CAS, periodic completion, and final validation. Report the dominant Raw and Oracle categories. | `[EVIDENCE NEEDED: frozen failure counts]`. | 90--110 words |
| E13 | concrete boundary | Give one concise success trace and one conclusion-changing failure or abstention. Explain whether the remedy belongs to mapping, representation, TMM coverage, search policy, or validation. | Do not add a third qualitative figure. | 65--85 words |

### 6. Discussion and Conclusion

| ID | Job | Paragraph content | Boundary | Target |
| --- | --- | --- | --- | ---: |
| D1 | synthesis | Interpret the evidence through the representation/reasoning division: Trig-URM retains the distinctions needed by the goal, and TMM-guided DIS operates over them without delegating control to free-form generation or generic CAS. | Do not repeat the full main-result table. | 100--120 words |
| D2 | mechanism meaning | Explain the strongest paper-specific insight: periodicity must affect representation, search, branch construction, and validation rather than be appended as answer formatting. | Refer to the periodic-completion ablation once, without restating every number. | 80--100 words |
| D3 | limitations/future boundary | Name the internal limitations: 50-problem pilot size, text-only input, supported grammar/TMM library, and no claim of pedagogical optimality. State multimodal input and broader operations as future extensions without pre-claiming their results. | Keep the later-paper space explicit. | 80--100 words |
| C1 | conclusion | Restate the two contributions, name the decisive frozen evidence, give a bounded implication, and close with the applicability boundary. | No new citation, mechanism, or result. | 80--100 words |

If page space is tight, D3 and C1 may be combined, but the boundary sentence must remain.

---

## 7. Compressed DPEA closed loop

The Method section should contain one coherent DPEA loop rather than repeating the pattern for every TMM.

| DPEA element | Manuscript placement | Required content | What it must not become |
| --- | --- | --- | --- |
| Definition | T3 and M3 | Trig-URM and the TMM transition contract | a large collection of decorative definitions |
| Process | M5--M7 | dynamic retrieval, bounded state search, validation, update, termination, abstention | a fixed five-family routing table |
| Example | T6 and M8--M12 | one state trace for \(\sin x+\cos x>1\), from \(D_0\) to \(D_4\) | several unrelated toy examples |
| Algorithm | after M7 | high-level executable control flow for dynamic DIS | low-level handler or CAS pseudocode |

### Running-example state trace

| State | New verified content | Rhetorical duty |
| --- | --- | --- |
| \(D_0\) | original inequality, radians, real domain, complete-set goal | show the input state before solving |
| \(D_1\) | \(\sqrt2\sin(x+\pi/4)>1\) | show equivalence-preserving transformation |
| \(D_2\) | \(\mathcal S_0=(0,\pi/2)\) in a base period | show constraint and branch reasoning |
| \(D_3\) | \(\bigcup_{k\in\mathbb Z}(2k\pi,\pi/2+2k\pi)\) | show periodic completion |
| \(D_4\) | verified PeriodicSet and satisfied goal contract | show exact validation and termination |

### Algorithm 1 control-flow contract

Algorithm 1 should implement this sequence at a high level:

1. preprocess the Raw input or load an Oracle Trig-URM;
2. initialize the candidate-state queue and visited signatures;
3. select the next state under the bounded search policy;
4. return a verified answer if the goal contract is satisfied;
5. retrieve all TMMs whose prerequisites hold for the current state;
6. execute each admissible operation under the CAS policy;
7. validate the transition before adding the new state to the queue;
8. record rejected transitions and stable failure causes;
9. abstain if the queue is exhausted or the budget is exceeded.

No family-specific branch should appear in Algorithm 1.

---

## 8. Figure, algorithm, and table placement

| Display | Placement | Single rhetorical responsibility | Required revision before prose rewrite |
| --- | --- | --- | --- |
| Figure 1 | Section 4.1 after M1 | what TrigSolver is and where the two contributions sit | Replace Identity/Property/Equation/Interval/Periodic boxes with the four confirmed cross-task operation descriptions; keep LLM and CAS visibly supporting components. |
| Algorithm 1 | Section 4.3 after M7 | how dynamic TMM-guided DIS retrieves, explores, validates, and terminates | Replace the current linear candidate-selection loop with a bounded state-queue search. |
| Figure 2 | Section 4.5 after M12 | how the running example changes state from (D_0) to (D_4) | Show one DIS controller spanning the transition chain instead of repeating `TMM-Guided DIS` above every box. |
| Table 1 | Section 3.1 after T2 | what the evaluation covers and what outputs are required | Use a compact single-column table; explicitly call the categories evaluation strata. |
| Table 2 | Section 5.3 | frozen main comparison and compact Raw/Oracle diagnostic | Retain Direct LLM, LLM + generic CAS, TrigSolver-Raw, and optionally one diagnostic TrigSolver-Oracle row. |
| Table 3 | Section 5.4 | isolate periodic completion and exact validation | Keep only Full, No periodic completion, and No exact validation. |

The former nine-row TMM inventory table is deleted because Figure 1 and M3--M4 already perform its explanatory role.

---

## 9. Claim--evidence map

| ID | Claim wording allowed in the paper | Decisive evidence | Main-text location | Status and wording boundary |
| --- | --- | --- | --- | --- |
| CL0 | TrigSolver provides a structured and verifiable basis for representative text-based trigonometric problem solving. | Frozen full-system result, baseline comparison, exact answer protocol, and bounded failures. | Abstract, I4, E8, D1, C1. | **Needs frozen evidence.** Do not generalize beyond the defined pilot scope. |
| CL1 | Trig-URM represents angle semantics, expressions, constraints, goals, derived facts, and periodic-set answers in one executable state. | Formal schema; benchmark representation coverage; Raw goal-reference/schema results or mapped failure counts. | T3--T6, brief evidence in E9. | A design claim is supported by formalization and demonstrated coverage. Do not claim representation superiority without a flat-state comparison. |
| CL2 | TMM-guided DIS dynamically retrieves applicable TMMs and composes locally validated state transitions under a bounded search policy. | Algorithm 1; logged search traces; full system versus LLM + generic CAS; success/failure trace. | M3--M12, E8, E13. | Supports mechanism and system-level utility. Without a no-DIS ablation, do not claim that dynamic search alone causes the full accuracy gain. |
| CL3 | Periodic completion converts valid base-period units into complete periodic answers under the recorded domain and exclusions. | Applicable-subset periodic completeness; No-periodic ablation; worked example. | T5, M11--M12, E10, D2. | **Needs frozen ablation evidence.** `Complete` applies only to supported output contracts. |
| CL4 | Exact validation reduces the acceptance of non-equivalent, incomplete, or ambiguous outputs. | Full versus No-validator accuracy, coverage, and false-acceptance results. | M13, E11, D1. | **Needs frozen ablation evidence.** Do not claim formal proof completeness. |
| CL5 | TrigSolver exceeds 60% problem-level accuracy on the frozen 50-problem pilot benchmark. | Correct/50 with abstention incorrect; comparison with both Raw baselines. | A5, E8, C1. | **Threshold claim; publish only if achieved.** Always name the dataset size and setting. |
| CL6 | Raw and Oracle results separate semantic-mapping errors from downstream symbolic-reasoning errors. | Same downstream solver and evaluator; Raw--Oracle difference; failure-stage counts. | E5, E9, D1. | Diagnostic interpretation only. Do not call Oracle an end-to-end result or a deployable score. |
| CL7 | The method offers traceability useful for solver diagnosis and future educational feedback. | Named, locally validated transition traces and error-stage labels. | E13, D3. | State `provides a basis for`; do not claim improved student learning or pedagogical optimality. |

### Contribution wording to use

1. **Representation contribution**

   > We formulate Trig-URM, a uniform representation that preserves the angle conventions, executable expressions, constraints, solving goals, and periodic-set semantics required by text-based trigonometric function problems.

2. **Reasoning contribution**

   > We develop a TMM-guided decoupled inference strategy that dynamically retrieves applicable trigonometric meta-models, explores validated state transitions, and terminates with either a verified answer or an explicit abstention.

3. **Empirical validation**

   > We evaluate TrigSolver on a frozen 50-problem benchmark using Direct LLM and LLM + generic CAS baselines, together with targeted ablations of periodic completion and exact validation.

The third item is validation of the method, not a separate benchmark-method contribution.

---

## 10. Main-text evidence allocation

| Result or analysis | Evidence class | Main-text decision | Reason |
| --- | --- | --- | --- |
| Frozen TrigSolver-Raw accuracy | core discovery | Main text and Abstract | Defines whether the paper meets its principal empirical target. |
| Direct LLM and LLM + generic CAS comparison | necessary support | Main Table 2 and one paragraph | Establishes advantage over the two intended alternatives. |
| TrigSolver-Oracle result | necessary diagnostic support | One Table 2 row or one sentence | Separates semantic mapping and solver capability without expanding the baseline matrix. |
| Per-stratum correct/10 | qualification/heterogeneity | Compact grouped columns or one sentence | Shows that the headline is not produced by one easy category; avoid overinterpreting (n=10). |
| No-periodic ablation | necessary support | Main Table 3 and E10 | Direct evidence for the strongest paper-specific mechanism. |
| No-validator ablation | necessary support | Main Table 3 and E11 | Direct evidence for reliability/coverage trade-off. |
| Failure-stage counts | qualification | E12, compact | Defines the actual boundary and indicates whether future work belongs upstream or downstream. |
| One successful trace | necessary explanatory support | Figure 2 plus E13 | Grounds the formal definitions and dynamic process. |
| One failure or abstention | edge case/qualification | E13 | Prevents a misleading universal-solving interpretation. |
| Full prompt, API payload, hashes, row-level outputs | provenance detail | Repository or appendix if allowed | Necessary for auditability but not for the main argument chain. |
| Token use, CAS call count, and detailed latency distribution | provenance/efficiency detail | One sentence or repository | Secondary to correctness for this pilot. |
| Development-set iteration history | provenance detail | Omit from paper | Engineering history is not frozen evidence. |
| Additional no-TMM/no-DIS/flat-state variants | future robustness | Omit from this conference paper | Not part of the confirmed lean evidence package. |

### Shortest sufficient Results evidence chain

```text
Frozen protocol and fair comparison
    -> full Raw accuracy and baseline differences
    -> compact Oracle diagnostic and per-stratum counts
    -> periodic-completion ablation
    -> exact-validation ablation
    -> dominant failures and one boundary case
```

---

## 11. Current-draft migration and compression map

This table governs the later targeted rewrite of `paper_draft.txt`.

| Current material | Decision | Destination or replacement | Reason |
| --- | --- | --- | --- |
| Current title centered on periodicity-aware symbolic reasoning | Replace later | Working title in Section 2.1 | The dual representation/reasoning contribution should lead; periodicity remains the strongest mechanism. |
| Current Abstract | Rewrite last | A1--A7 | It currently inventories the full paper before frozen evidence is available and overstates several untested effects. |
| Five-paragraph Introduction | Compress to four paragraphs | I1--I4 | Remove repeated method explanation and lead from the exact gap to the two contributions. |
| Related Work with three subsections | Retain mechanism groups, compress headings if needed | R1--R3 | The mechanism grouping is sound, but the section must fit the conference budget. |
| Input/output formulation | Retain and tighten | T1 | Keep only fields used later in the method or evaluation. |
| Full-width five-category task table | Compress and reframe | Table 1 | Make the five categories evaluation strata, not the method architecture. |
| Trig-URM six-tuple definition | Retain and formalize as Definition 1 | T3--T5 | Central representation contribution. |
| TMM five-tuple definition | Retain and formalize as Definition 2 | M3 | Central reasoning object. |
| Nine-row TMM inventory table | Delete from main text | Replace with M4, M8--M11, and Fig. 1 | It makes the method look case-by-case and duplicates the pipeline figure. |
| Current DIS paragraph | Substantially replace | M5--M7 | Must define dynamic retrieval and bounded state-space search, not a single linear next-operation selection. |
| Current Algorithm 1 | Replace control flow | Algorithm after M7 | Must use a candidate-state queue, alternative exploration, and visited signatures. |
| Controlled symbolic execution and validation | Retain and compress | M2 and M13 | Important boundary, but should not repeat validation in several paragraphs. |
| Figure 1 | Retain after revision | Section 4.1 | Replace task-like boxes with the four cross-task operations. |
| Figure 2 | Retain after revision | Section 4.5 | Strong DPEA running example; unify the repeated DIS labels into one controller. |
| Five explicit research questions | Reduce to three implicit experimental questions | E1--E7 | The lean experiment does not need a large RQ inventory. |
| Broad baseline matrix including CAS-only and flat-state variants | Remove unconfirmed rows | E4--E5 and Table 2 | Keep only the user-confirmed baseline package plus a compact Oracle diagnostic. |
| Seven-metric main table | Simplify | Table 2 | Retain accuracy, coverage, periodic completeness where applicable, and false acceptance only if informative. |
| Six-row ablation table | Reduce to three rows | Table 3 | Full, No periodic completion, No exact validation. |
| Capability analysis repeating identity/interval/periodic results | Compress | E9--E13 | Keep per-stratum counts and one trace; avoid a second result inventory. |
| Five-paragraph Analysis | Compress to D1--D3 | Section 6 | Separate evidence interpretation from result repetition. |
| Missing Conclusion | Add | C1 | Close with contribution, decisive evidence, implication, and boundary. |
| Chinese draft | Preserve unchanged until English structure is approved | Later synchronization stage | Avoid maintaining two moving drafts before the argument is stable. |

---

## 12. Claim repetition control

| Claim | Introduce | Demonstrate | Interpret | Synthesize | Delete/compress elsewhere |
| --- | --- | --- | --- | --- | --- |
| representation + reasoning dual contribution | I4 | E8/E9 | D1 | C1 | Do not restate the full claim at every Method subsection opening. |
| periodicity as first-class structure | I2 | T5, M11, E10 | D2 | one short clause in C1 | Avoid repeating `periodicity-aware` in every title, heading, and caption. |
| dynamic TMM-guided DIS | I4 | M5--M7, Algorithm 1, E13 | D1 | C1 | Do not claim causal superiority without a no-DIS ablation. |
| exact validation and abstention | I2/I4 | M13, E11/E12 | D1/D3 | optional short clause in C1 | Do not repeat the full stable error-code list in the main text. |
| five evaluation strata | T2/Table 1 | E2/E9 | optional boundary clause in D3 | none | Remove from title, abstract method inventory, and contribution wording. |
| educational relevance | I1 | none in this study | D3 | bounded outlook only | Delete claims about tutorial quality or learning improvement. |

---

## 13. Planned rewrite sequence and approval gates

### Stage A: approve this blueprint

Author confirms or redirects:

- working title direction;
- paragraph architecture;
- dynamic search description;
- Oracle diagnostic placement;
- claim--evidence boundaries.

### Stage B: align figures and Algorithm 1

Before prose rewrite:

- revise Figure 1 around the four cross-task operations;
- revise Figure 2 to show one spanning DIS controller;
- rewrite Algorithm 1 as bounded state-space search.

These displays determine the Method subsection order.

### Stage C: rewrite Task Formulation and Method

Rewrite T1--T6 and M1--M13 first because they define the paper's technical truth. Run a terminology and notation consistency check before moving on.

### Stage D: finalize result-table schemas

Create empty Table 2 and Table 3 schemas with exact metrics and rows. Insert frozen numbers only after evaluation and verify every prose statement against the tables.

### Stage E: rewrite Experiments from evidence outward

Write E1--E13 only after the frozen result allocation is stable. Report observation before interpretation.

### Stage F: rewrite Introduction and Related Work backward from the evidence

Every central question introduced in I1--I4 must receive an answer in E8--E13. Remove background that does not prepare one of those questions.

### Stage G: write Discussion, Conclusion, Abstract, and final Title

Draft in this order:

1. Discussion and limitations;
2. Conclusion;
3. Abstract;
4. final title.

### Stage H: synchronize the Chinese draft

Update `paper_draft_CN.txt` only after the English argument and evidence are stable.

---

## 14. Assumptions and missing inputs

The blueprint proceeds with the following explicit assumptions.

1. The intended final DIS implementation supports dynamic candidate retrieval and bounded state-space search, even though the exact priority and tie-breaking policy still require an author decision before the Method rewrite.
2. The main result will use the frozen 50-problem test set, with 10 problems in each evaluation stratum and abstention counted as incorrect.
3. Direct LLM and LLM + generic CAS are the only required external baseline families for the conference version.
4. The Oracle setting is retained as one compact diagnostic row or sentence; it is not expanded into a separate baseline matrix.
5. The two main ablations are No periodic completion and No exact validation.
6. Final benchmark counts, model snapshots, baseline prompts, hashes, runtime parameters, results, and failures remain `[EVIDENCE NEEDED]` until verified.
7. The paper will not use development-set diagnostics as frozen-test evidence.

---

## 15. Blueprint acceptance test

Before beginning the targeted rewrite, confirm that the answer to every item is `yes`.

- Does the title foreground representation and reasoning rather than only periodicity?
- Is the exact gap a missing executable state plus dynamic validated reasoning process, rather than merely the absence of TrigSolver?
- Are the five categories confined to task scope, dataset composition, and per-category evaluation?
- Are the four cross-task operations described without inventing new branded terminology?
- Does Trig-URM formally answer how the problem is represented?
- Does dynamic TMM-guided DIS formally answer how reasoning proceeds?
- Is there one compressed DPEA loop with one running example and one algorithm?
- Does Algorithm 1 describe dynamic bounded search rather than fixed task routing?
- Does every performance statement have a dataset, metric, baseline, and setting?
- Are the two ablations interpreted only for periodic completion and exact validation?
- Are periodic completeness and explicit abstention bounded to the supported scope?
- Is educational relevance stated without claiming educational effectiveness?
- Is the complete evidence chain short enough for a 6--8 page paper?
