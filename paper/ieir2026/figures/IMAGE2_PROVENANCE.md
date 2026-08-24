# Image-2 Figure Provenance

- Generation date: 2026-08-24
- Mode: built-in Image-2 generation and targeted editing
- Intended use: non-quantitative methodological schematics for the IEIR2026 manuscript
- Style references: three author-supplied conference-paper workflow figures, used only for visual grammar (modular panels, directional flow, restrained palette, and hierarchy)
- Scientific evidence status: explanatory diagrams only; they do not encode measured results

## Figure 1: TMM-guided DIS architecture

Final asset: `figure1_tmm_guided_dis_architecture.png`

Prompt set:

1. Create a wide, publication-ready vector-like systems diagram on a white background. Separate a small supporting Problem Understanding front end from a dominant TMM-Guided Symbolic Reasoning core. In the core, show a TMM Library organized by Normalize, Transform, Branch Reason, and Complete & Validate; show Dynamic DIS as a closed Retrieve--Execute--Validate--Update loop with a priority queue, visited signatures, controlled CAS support, verified answer, and explicit abstention. Use navy structure lines, muted blue/lavender/green/amber accents, compact sans-serif typography, generous whitespace, and no branding unrelated to TMM/DIS.
2. Correct the validation routing so an accepted candidate is returned to the priority queue and a rejected candidate records a failure reason. Preserve all other composition and styling.

## Figure 2: validated state progression

Final asset: `figure2_tmm_state_reasoning_trace.png`

Prompt set:

Create a wide, publication-ready worked reasoning trace for the input $\sin x+\cos x>1$, $x\in\mathbb{R}$. Show five states from $U^{(0)}$ to $U^{(4)}$ connected by Transform, Branch Reason, Complete, and Validate transitions. Include the equivalent form $\sqrt{2}\sin(x+\pi/4)>1$, the base-period interval $(0,\pi/2)$, the periodic set $\bigcup_{k\in\mathbb{Z}}(2k\pi,\pi/2+2k\pi)$, and final checks for equivalence, branch coverage, open endpoints, and domain consistency. Add a compact lower ledger titled Validated State Progression. Match the same restrained palette and typography as Figure 1.

Accuracy corrections:

1. Redraw the periodic-set miniature to align repeated intervals with exact endpoint labels.
2. Correct the omitted negative sign in the $-3\pi/2$ endpoint label.
3. Because the generated endpoint typography remained unstable, retain the exact union formula as the authoritative mathematical content and replace the redundant tick labels with three equal open intervals connected by $+2\pi$ translation arrows.

## Author check before submission

- Confirm every formula, interval endpoint, and transition label against the manuscript source.
- Retain the figures as explanatory schematics rather than experimental evidence.
- Confirm the venue's current generative-AI disclosure policy and add an acknowledgment when required.
