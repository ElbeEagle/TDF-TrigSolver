# Figure 1 — layout refinement v3

Date: 2026-08-28
Mode: built-in Image-2 targeted editing; no CLI/API fallback.

## Changes

- Removed the head-and-brain icon from the understood-state card; centered its text and formula.
- Moved the four legend entries to the upper-right white margin, vertically arranged above Final solution.
- Removed the bottom legend.
- Preserved the model chains, exploratory paths, node meanings, and S = (A, E) output.
- The manuscript and earlier image versions were not modified.

## Exports

- `figure1_tmm_drs_graph_v3.png`: native 1779 × 884 PNG.
- `figure1_tmm_drs_graph_v3_4k.png`: 3840 × 1908 proportional resampled PNG. Not native 4K and not editable vector artwork.

```latex
\includegraphics[width=0.96\textwidth]{figures/figure1_tmm_drs_graph_v3_4k.png}
```

## QA

Visually checked the absence of the brain icon and bottom legend; the four legend entries, symbol styles, and output formula; the predefined-chain subscripts; and the solid/dashed exploration connections. This is a conceptual method illustration, not experimental evidence. Final physical-size PDF and author publication-policy checks remain separate from this layout review.

## Exact edit prompt

Use case: precise-object-edit of an existing scientific paper figure.
Make only these two targeted layout edits to the supplied complete Figure 1, preserving its scientific content and central diagram exactly.

1. In the LEFT bottom "Understood state" card, REMOVE the entire head-and-brain outline icon. Leave no replacement icon. Center the existing two-line "Understood state" text and the formula U^(0), G horizontally within that card. Preserve the card border, size, color, all other left-panel cards, the document icon, parse-tree icon, and all arrows.

2. MOVE the four existing legend entries from the bottom horizontal row to a vertical list in the UPPER-RIGHT CORNER OF THE WHOLE FIGURE, in the WHITE right-hand margin OUTSIDE the DRS container and ABOVE the Final solution card. Use exactly four evenly spaced rows in this order:
medium-blue filled circle  "Applied TMM"
pale-blue filled circle  "Tried TMM"
solid curved black arrow  "Reasoning path"
dashed curved black arrow  "Exploration path"
Keep each symbol to the left of its text, align the text starts, match the original font and symbol styles, and use readable consistent font size. The vertical legend must not overlap the central DRS container, the output arrow, or the Final solution card. Do not add a legend title or explanatory prose. It may use a little additional right-side white margin if needed, but do not shrink the main diagram.

DELETE the old bottom legend completely. Trim the now-unused bottom white strip so the final canvas ends with a modest even white margin beneath the DRS panel. Keep all other geometry, labels, equations, subscripts, node fills, solid/dashed path choices, arrow directions, headings and final solution S=(A,E) UNCHANGED. No T should be added to the output. Do not redraw or rearrange the central predefined chains or exploration graph. Keep white background, thin navy outlines, the same pale blue palette, and crisp publication typography. Return the complete edited figure at the highest available native resolution.

