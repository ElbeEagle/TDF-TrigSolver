# TDF Journal Style Guide: The DPEA-Style Paradigm

This guide enforces the rigorous "Engineering-as-Math" writing style found in core references (Yu_2022_TDF; Peng_2025_Scene; Yu_2023_implicit). 
The goal is to elevate algorithmic engineering into mathematical theory using the **DPEA** (Definition-Process-Example-Algorithm) closed loop. Write every step of the algorithm process in detail and produce solid, in-depth, and spiritually high English journal articles that can reach Q1 level.

## 1. The DPEA Structure (Mandatory)

Every major module (Problem Recognizance, Symbolic Solving) must follow this strictly:

### 1.1 Definition (Formalization)
**Never** start with a description of a process. Start with a mathematical definition of the objects involved.
*   **Rule**: Convert all data structures (Classes, Lists, Dictionaries) into **Tuples**, **Sets**, or **Mappings**.
*   **Template**: "Definition $N$ (Name). A [Concept] is defined as a tuple $\mathcal{T} = (A, B, \Phi)$, where $A$ is..., $B$ is..., and $\Phi: A \to B$ denotes..."
*   **Example**: Instead of "We parse the text," write "We define the Semantic Primitive set $\Omega_t = \{ \omega_1, \omega_2, \dots \}$."

### 1.2 Process (Hierarchical Decomposition)
Decompose the method into precise logical units. Avoid flat narrative.
*   **Keywords**: *Phase, Procedure, Stage, Category.*
*   **Categorization Style**: When handling different cases, use explicit headers:
    *   "Category 1: Extraction of Explicit Relations..."
    *   "Category 2: Inference of Implicit Constraints..."
*   **Logic**: Use Propositional Logic to justify steps. "Proposition 1: The mapping $\psi$ is valid if and only if..."

### 1.3 Example (State Tracing)
Use the **Parabola Case** to ground the math. Show the **State Snapshot** at each step.
*   **Rule**: Every abstract definition must be immediately followed by "For instance, in Fig. 2, the initial state $\mathcal{S}_0$ is..."
*   **Visual**: Refer to specific parts of the diagram (e.g., "curve $c_1$," "intersection $P$").

### 1.4 Algorithm / Table (Summary)
*   **Tables**: Use tables to summarize rule sets (e.g., "Table 1: Mapping Rules for Visual Primitives").
*   **Algorithm**: Use high-level pseudocode wrapped in `\begin{algorithm}` to summarize the logic flow.

---

## 2. Vocabulary Bank (Yu-Style)

| Domain | Engineering Term (Avoid) | Academic Term (Use) |
| :--- | :--- | :--- |
| **Action** | get, find, parse | **Acquire, Extract, Derive, Instantiate** |
| **Logic** | use, combine, mix | **Leverage, Synergize, Couple, Integrate** |
| **Structure** | part, step, loop | **Phase, Procedure, Iteration, Stage** |
| **Object** | list, dict, object | **Set ($\Omega$), Tuple ($\mathcal{T}$), Vector ($\mathbf{v}$)** |
| **Relation** | link, connection | **Mapping ($\psi$), Alignment, Correlation** |

## 3. LaTeX Formatting
*   **Math Mode**: All variables ($x, y, \mathcal{S}$) must be in `$ $`.
*   **References**: Use `\cite{key}` and `\autoref{label}`.
*   **Text Styling**: Use `\textit{term}` for defining new terms.

## 4. Interaction Checklist (AI Self-Correction)
Before outputting, verify:
1.  Did I define the **Tuple/Set** before explaining the process?
2.  Did I include a **Proposition** or **Rationale**?
3.  Did I cite the **Parabola Example** to show the state change?
4.  Is the tone **formal & declarative** (Declarative for Definitions, Procedural for Solvers)?
