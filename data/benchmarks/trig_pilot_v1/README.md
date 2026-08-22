# Trig Pilot v1 benchmark protocol

This directory is derived only from the CMM-Math main and existing atomized files. Source files are never rewritten.

- `dev.jsonl`: 25 development records migrated to Gold schema v0.2. Each family has two multiple-choice and three open records. These remain machine-prepared development data, not frozen-test evidence.
- `test_candidates.jsonl`: 150 source-only, non-image high-recall candidates, 30 per family.
- `test_selection_audit.jsonl`: one screening decision for every candidate. Selection uses research scope, output balance, and template balance; solver predictions are explicitly excluded.
- `test_selection.jsonl`: the selection-locked 50 questions, ten per family and five multiple-choice plus five open per family. All ten `EQUATION` records ask for complete real periodic solution sets.
- `test_annotation_template.jsonl`: a blank copy of the locked selection for each independent annotator.
- `gold_answer.schema.json`: the frozen mathematical Gold schema generated from `GoldAnswer`.
- `ANNOTATION_GUIDE.md`: independent annotation, normalization, adjudication, and final-freeze rules.
- `manifest.json`: hashes for every generated artifact. `selection_frozen=true` locks question composition; `frozen=false` still blocks test experiments.

Gold schema v0.2 never scores presentation strings. It stores expressions as `ExprAST`, ordinary real sets as `SetSpec`, and infinite periodic sets as `PeriodicSet`. Multiple-choice records retain `gold_option`, but the option must be derived only after an independent mathematical `gold_answer` is produced.

To create `test.jsonl`, two humans must independently solve and annotate all 50 locked questions, including `oracle_urm`, structured mathematical Gold, and `gold_option` where applicable. Disagreements must be adjudicated. Only after every record is double-verified may `test_sha256` be written and `frozen=true` be set. The experiment runner enforces this gate, and abstentions count as incorrect.
