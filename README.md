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

The test command is intentionally blocked while `manifest.json` has `frozen=false`. It must not be enabled until 50 records have independently reviewed Oracle-URM and structured gold annotations.

See [the implementation and experiment note](docs/trig_solver_pilot.md) and [benchmark protocol](data/benchmarks/trig_pilot_v1/README.md).
