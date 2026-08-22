# TrigSolver pilot: implementation and experiment note

## Scope and interfaces

The package exposes:

```python
solve_raw(problem: RawProblem, config: SolverConfig) -> SolveResult
solve_oracle(urm: TrigURM, options: list[str] | None) -> SolveResult
```

It supports `EVAL`, `IDENTITY`, `SINUSOID_PROPERTY`, `EQUATION`, and `DOMAIN_RANGE_INEQUALITY`. Images, multiple subquestions, geometric/vector mixtures, parameterized root counts, arbitrary transcendental equations, and teaching-style generated solutions are out of scope and explicitly abstain.

Trig-URM stores allowlisted expression ASTs, angle states, explicit constraints, a single grounded goal, and derived facts. Gold schema v0.2 uses `ExprAST` for scalar expressions, `SetSpec` for ordinary real sets, and `PeriodicSet` for point or interval cells lifted by an integer multiple of one period. Each TMM transition records a compact verified trace.

## Execution policy

- Qwen is fixed to `qwen3.7-flash-2026-07-15`, temperature `0.01`, non-thinking JSON mode, with one retry after schema failure. Its output contract has no answer or derivation field.
- Expressions can contain only rational numbers, symbols, pi, arithmetic, powers, absolute values, `sin/cos/tan`, `asin/acos/atan`, and scalar relations. Inverse functions are included so exact non-special equation roots remain structured. Unknown nodes and trees above 256 nodes fail.
- SymPy operations are allowlisted and receive a two-second wall-clock limit. `ConditionSet` is an abstention.
- Equation and inequality base cells are lifted by custom periodic completion. Exact substitution or symbolic equivalence is required before acceptance.
- Numeric sampling is not used to accept an answer.

### Parser adapter decision

The project pins Lark `1.2.2`, but SymPy 1.14's experimental Lark LaTeX backend cannot reliably parse the pilot grammar: it rejects `\pi` and returns ambiguous Lark trees for common forms such as `\sin^2x+\cos^2x`. The executable adapter therefore uses SymPy's ANTLR 4.11 backend in strict mode, followed by the independent AST allowlist and node budget. This is a deliberate, regression-tested deviation from the initial Lark-backend proposal; replacing it with a project-owned Lark grammar is future work.

## Development experiment (2026-08-20, legacy string protocol)

The current 25-record development set is balanced across the five families and contains two multiple-choice plus three open records per family. It is composed of transparent CMM-Math atomizations, marked `machine_prepared`; it is an engineering development result, not a publishable frozen-test claim.

| Mode / ablation | Correct | Accuracy | Coverage | Periodic completeness |
|---|---:|---:|---:|---:|
| Oracle full | 24/25 | 96% | 100% | 100% |
| Raw full | 24/25 | 96% | 100% | 100% |
| Oracle CAS-only | 10/25 | 40% | 68% | 0% |
| Oracle without periodic completion | 17/25 | 68% | 72% | 0% |
| Oracle without validator | 14/25 | 56% | 100% | 71.4% |

Raw full used 19,664 tokens in total and averaged 1.85 seconds per record. The one full-system failure is CMM source `18045`: SymPy preserves an exact 10-degree/20-degree/70-degree expression instead of proving its equivalence to `sqrt(3)`. The result is not accepted through numeric coincidence.

After migrating all 25 records to Gold schema v0.2 on 2026-08-21, an Oracle full diagnostic scored 25/25. The formerly reported `18045` failure disappeared because structured symbolic comparison proves the two expressions equivalent; the solver path itself was unchanged. Raw and ablation runs have not yet been repeated under v0.2, so the legacy table must not be mixed with future v0.2 results.

The five-family live parser integration test passed 5/5 after the exact nested JSON schema was added to the prompt.

## Frozen-test status

The source-only candidate pool now contains 150 records. A scope-only audit locks 50 questions in `test_selection.jsonl`: ten per family, five multiple-choice and five open, with all ten equation questions requesting complete real periodic solution sets. Question composition is selection-frozen, but `test.jsonl` does not yet exist and the manifest remains `frozen=false`. Two humans must independently annotate and adjudicate every Oracle-URM and structured Gold, calculate `test_sha256`, and only then freeze the split. The experiment runner enforces this gate even without the CLI flag.

## Next priorities

1. Complete two-person annotation of the locked 50 questions without inspecting system predictions.
2. Add an exact rule for complementary-angle and sum/difference reductions such as source `18045`.
3. Adjudicate periodic-set endpoints, excluded points, and inverse-trigonometric principal values under Gold schema v0.2.
4. Repeat Raw and ablation development runs under the v0.2 scoring protocol.
5. Implement a project-owned strict Lark grammar if Lark is required as the production parser backend.
