# TDF-TrigSolver pilot

A constrained neuro-symbolic pilot for five families of Chinese text-only trigonometric-function problems:

`Formula preprocessor -> Qwen grounded parser -> Trig-URM -> TMM/DIS -> controlled SymPy -> periodic completion -> exact validator`

The LLM maps explicit semantics only. It never receives source `answer`, `analysis`, or `solution` fields and cannot emit a solver answer in its schema. Unsupported, ungrounded, timed-out, or unverifiable inputs return a stable abstention code.

## Install and validate

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pytest -q
RUN_LLM_INTEGRATION=1 .venv/bin/python -m pytest -q -m integration
```

## Solve

```bash
.venv/bin/python -m trig_solver.cli --mode raw --question '计算 $\sin 30^{\circ}$。'
.venv/bin/python -m trig_solver.cli --mode oracle --input path/to/oracle_input.json
```

## Experiments

```bash
.venv/bin/python scripts/build_trig_pilot_benchmark.py
.venv/bin/python -m trig_solver.experiments.run --split dev --mode oracle
.venv/bin/python -m trig_solver.experiments.run --split dev --mode raw
.venv/bin/python -m trig_solver.experiments.run --split dev --mode oracle --variant cas-only
.venv/bin/python -m trig_solver.experiments.run --split dev --mode oracle --variant no-periodic
.venv/bin/python -m trig_solver.experiments.run --split dev --mode oracle --variant no-validator
.venv/bin/python -m trig_solver.experiments.run --split test --mode both --freeze-check
.venv/bin/python -m trig_solver.experiments.summarize --latest
```

The 50 test questions are selection-locked and now have a machine-prepared Silver seed, but the test command remains intentionally blocked while `manifest.json` has `frozen=false`. It must not be enabled until two isolated human reviewers have checked and adjudicated every Oracle-URM and Gold schema v0.2 answer.

See [the implementation and experiment note](docs/trig_solver_pilot.md) and [benchmark protocol](data/benchmarks/trig_pilot_v1/README.md).

## Assisted Gold review UI

The optional local UI is kept outside `src/trig_solver/`. It loads only the
sealed empty test template, a hash-locked machine Silver seed, and one
annotator's private session directory. It does not call the solver or expose
source answers, solver predictions, or the other annotator's work. The desktop
layout keeps the question in a sticky left-hand card while the form scrolls on
the right.

```bash
.venv/bin/python -m pip install -e '.[annotation,dev]'
.venv/bin/python annotation_app/run.py --annotator annotator_a --port 8501
```

Open `http://127.0.0.1:8501`. See
[the annotation UI guide](annotation_app/README.md) for the two-annotator setup,
field conventions, and output files.
