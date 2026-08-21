"""Raw and Oracle entry points."""

from __future__ import annotations

from .models import AbstainCode, RawProblem, SolveResult, SolverConfig, TrigURM
from .preprocessing import FormulaParseError, preprocess_problem, split_options
from .qwen import QwenRawParser, RawSchemaError, semantic_map_to_urm
from .solver import DISSolver


def solve_oracle(urm: TrigURM, options: list[str] | str | None = None, config: SolverConfig | None = None) -> SolveResult:
    return DISSolver(config).solve(urm, split_options(options))


def solve_raw(problem: RawProblem, config: SolverConfig | None = None) -> SolveResult:
    config = config or SolverConfig()
    try:
        preprocessed = preprocess_problem(problem)
    except FormulaParseError as exc:
        return SolveResult.abstain(AbstainCode.FORMULA_PARSE, str(exc))
    if preprocessed.needs_image:
        return SolveResult.abstain(AbstainCode.UNSUPPORTED_INPUT, "image- or table-dependent problem")
    try:
        mapped, api_metadata = QwenRawParser(config.model_name, config.temperature).parse(preprocessed)
        if mapped.needs_image:
            return SolveResult.abstain(AbstainCode.UNSUPPORTED_INPUT, "semantic mapper detected visual dependency")
        urm = semantic_map_to_urm(mapped, preprocessed)
    except RawSchemaError as exc:
        code = AbstainCode.GROUNDING if "reference" in str(exc) else AbstainCode.RAW_SCHEMA
        return SolveResult.abstain(code, str(exc))
    result = DISSolver(config).solve(urm, preprocessed.options)
    result.metadata.update(api_metadata)
    return result

