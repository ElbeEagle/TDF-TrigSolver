"""Grounded Qwen semantic mapper. It is deliberately unable to return answers."""

from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
from pydantic import BaseModel, Field, ValidationError

from .models import AngleState, ConstraintSpec, GoalSpec, TaskFamily, TrigURM
from .preprocessing import PreprocessedProblem


class RawSchemaError(ValueError):
    pass


class SemanticAngle(BaseModel):
    symbol: str
    unit: Literal["radian", "degree", "unspecified"] = "unspecified"
    quadrant: int | None = Field(default=None, ge=1, le=4)
    domain: str = "Reals"


class SemanticGoal(BaseModel):
    task_family: TaskFamily
    operator: str
    target_refs: list[str]
    property_names: list[str] = Field(default_factory=list)
    completeness: Literal["all_real", "restricted", "not_applicable"] = "not_applicable"


class RawSemanticMap(BaseModel):
    goal: SemanticGoal
    angles: list[SemanticAngle] = Field(default_factory=list)
    constraint_refs: list[str] = Field(default_factory=list)
    needs_image: bool = False
    abstain: bool = False
    abstain_reason: str | None = None


SYSTEM_PROMPT = """You map Chinese trigonometric problem text to a grounded JSON schema.
You must never solve the problem, choose an option, emit a mathematical answer, or add a derivation.
Only refer to formulas by the supplied E-identifiers. Extract only explicit constraints from the text.
Choose exactly one task family:
- EVAL: evaluate a target value using supplied values or special angles;
- IDENTITY: simplify or prove an identity;
- SINUSOID_PROPERTY: period, amplitude, phase, monotonicity, symmetry, extrema, or range;
- EQUATION: solve a trigonometric equation;
- DOMAIN_RANGE_INEQUALITY: domain, range, or inequality.
Allowed operators: evaluate, simplify, property, solve_equation, domain, range, solve_inequality.
property_names may contain: period, amplitude, phase_shift, midline, monotonic_increasing,
monotonic_decreasing, symmetry_axis, symmetry_center, maximum, minimum, range.
If an image, table, multiple subquestions, geometry/vector context, arbitrary transcendental equation,
or parameterized root-count task is required, set abstain=true.
Return exactly this JSON object shape; `goal` MUST be an object, never a string:
{
  "goal": {
    "task_family": "EVAL",
    "operator": "evaluate",
    "target_refs": ["E1"],
    "property_names": [],
    "completeness": "not_applicable"
  },
  "angles": [{"symbol": "x", "unit": "radian", "quadrant": null, "domain": "Reals"}],
  "constraint_refs": [],
  "needs_image": false,
  "abstain": false,
  "abstain_reason": null
}
Use only supplied E-identifiers. Include every field, using empty arrays or null where appropriate. Return JSON only."""


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


class QwenRawParser:
    def __init__(self, model_name: str, temperature: float = 0.01) -> None:
        env_path = _repo_root() / ".env.local"
        load_dotenv(env_path, override=False)
        api_key = os.getenv("DASHSCOPE_API_KEY") or os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")
        if not api_key or not base_url:
            raise RawSchemaError("DASHSCOPE_API_KEY and OPENAI_BASE_URL must be configured")
        self.model_name = model_name
        self.temperature = temperature
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    @staticmethod
    def prompt_hash() -> str:
        return hashlib.sha256(SYSTEM_PROMPT.encode("utf-8")).hexdigest()

    def parse(self, problem: PreprocessedProblem) -> tuple[RawSemanticMap, dict[str, object]]:
        formula_table = [{"id": item.id, "latex": item.source_latex} for item in problem.expressions]
        payload = {
            "question": problem.question,
            "options": problem.options,
            "formula_table": formula_table,
        }
        last_error = "unknown schema failure"
        started = time.perf_counter()
        total_tokens = 0
        for attempt in range(2):
            correction = "" if attempt == 0 else f"\nPrevious JSON was invalid: {last_error}. Return every required field."
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    temperature=self.temperature,
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT + correction},
                        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
                    ],
                    extra_body={"enable_thinking": False},
                )
            except OpenAIError as exc:
                raise RawSchemaError(f"Qwen API request failed: {type(exc).__name__}") from exc
            if response.usage:
                total_tokens += response.usage.total_tokens
            content = response.choices[0].message.content or ""
            try:
                mapped = RawSemanticMap.model_validate_json(content)
                return mapped, {
                    "model": self.model_name,
                    "prompt_hash": self.prompt_hash(),
                    "latency_seconds": time.perf_counter() - started,
                    "total_tokens": total_tokens,
                    "attempts": attempt + 1,
                }
            except (ValidationError, ValueError, json.JSONDecodeError) as exc:
                last_error = str(exc)
        raise RawSchemaError(last_error)


def semantic_map_to_urm(mapped: RawSemanticMap, problem: PreprocessedProblem) -> TrigURM:
    if mapped.abstain:
        raise RawSchemaError(mapped.abstain_reason or "semantic mapper abstained")
    valid_refs = {item.id for item in problem.expressions}
    referenced = set(mapped.goal.target_refs) | set(mapped.constraint_refs)
    missing = referenced - valid_refs
    if missing:
        raise RawSchemaError(f"semantic map contains unknown references: {sorted(missing)}")
    constraints: list[ConstraintSpec] = []
    by_id = {item.id: item for item in problem.expressions}
    for ref in mapped.constraint_refs:
        ast = by_id[ref].ast
        kind = "equation" if ast.op == "eq" else "inequality" if ast.op in {"lt", "le", "gt", "ge"} else "property"
        constraints.append(ConstraintSpec(kind=kind, expression=ast))
    angles: list[AngleState] = []
    unicode_greek = {"α": "alpha", "β": "beta", "θ": "theta", "φ": "phi", "ω": "omega"}
    for item in mapped.angles:
        payload = item.model_dump()
        symbol = unicode_greek.get(item.symbol, item.symbol).strip().lstrip("\\")
        if not symbol.replace("_", "").isalnum() or symbol[0].isdigit():
            # Formula ASTs retain explicit degree constants; they are not
            # variable angle-state entries.
            continue
        payload["symbol"] = symbol
        angles.append(AngleState.model_validate(payload))
    return TrigURM(
        angles=angles,
        expressions=problem.expressions,
        constraints=constraints,
        goal=GoalSpec.model_validate(mapped.goal.model_dump()),
    )
