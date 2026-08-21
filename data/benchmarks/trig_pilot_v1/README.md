# Trig Pilot v1 benchmark protocol

This directory is derived from `data/CMM-Math/data.jsonl`; the source file is never rewritten.

- `dev.jsonl`: 25 single-goal atomized development records, five per task family and exactly two multiple-choice plus three open records per family. These records are machine-prepared and still require author review before paper reporting.
- `test_candidates.jsonl`: automatically recalled, non-image candidate records. Candidate family labels are not gold labels.
- `manifest.json`: hashes and the freeze state. `frozen=false` deliberately blocks every test run.

To create `test.jsonl`, a first annotator must select exactly 50 records (ten per family; five multiple-choice and five open), add a complete `oracle_urm`, structured gold answer, and template group. A second person must independently check both the Oracle-URM and answer. After adjudication, set every review status to `double_verified`, record the independent reviewer, calculate `test_sha256`, and only then set `frozen=true`.

The experiment runner enforces this gate even if `--freeze-check` is omitted. Abstentions count as incorrect.
