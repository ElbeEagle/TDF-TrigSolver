"""Validated wire types used between parsing, reasoning, and evaluation."""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

import sympy as sp
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class TaskFamily(StrEnum):
    EVAL = "EVAL"
    IDENTITY = "IDENTITY"
    SINUSOID_PROPERTY = "SINUSOID_PROPERTY"
    EQUATION = "EQUATION"
    DOMAIN_RANGE_INEQUALITY = "DOMAIN_RANGE_INEQUALITY"


class AbstainCode(StrEnum):
    UNSUPPORTED_INPUT = "UNSUPPORTED_INPUT"
    FORMULA_PARSE = "FORMULA_PARSE"
    RAW_SCHEMA = "RAW_SCHEMA"
    GROUNDING = "GROUNDING"
    NO_ROUTE = "NO_ROUTE"
    TMM_PRECONDITION = "TMM_PRECONDITION"
    CAS_TIMEOUT = "CAS_TIMEOUT"
    CAS_UNSOLVED = "CAS_UNSOLVED"
    PERIODIC_FAILURE = "PERIODIC_FAILURE"
    VALIDATION_NO_MATCH = "VALIDATION_NO_MATCH"
    VALIDATION_AMBIGUOUS = "VALIDATION_AMBIGUOUS"
    WRONG_ANSWER = "WRONG_ANSWER"


ALLOWED_AST_OPS = {
    "integer",
    "rational",
    "symbol",
    "pi",
    "add",
    "mul",
    "pow",
    "sin",
    "cos",
    "tan",
    "asin",
    "acos",
    "atan",
    "abs",
    "eq",
    "lt",
    "le",
    "gt",
    "ge",
}


class ExprAST(BaseModel):
    """Small, executable expression tree with no general evaluation surface."""

    op: str
    value: str | int | None = None
    args: list["ExprAST"] = Field(default_factory=list)

    @field_validator("op")
    @classmethod
    def validate_op(cls, value: str) -> str:
        if value not in ALLOWED_AST_OPS:
            raise ValueError(f"unsupported AST operation: {value}")
        return value

    @model_validator(mode="after")
    def validate_shape(self) -> "ExprAST":
        arity = {
            "integer": 0,
            "rational": 0,
            "symbol": 0,
            "pi": 0,
            "pow": 2,
            "sin": 1,
            "cos": 1,
            "tan": 1,
            "asin": 1,
            "acos": 1,
            "atan": 1,
            "abs": 1,
            "eq": 2,
            "lt": 2,
            "le": 2,
            "gt": 2,
            "ge": 2,
        }
        if self.op in arity and len(self.args) != arity[self.op]:
            raise ValueError(f"{self.op} expects {arity[self.op]} arguments")
        if self.op in {"add", "mul"} and len(self.args) < 2:
            raise ValueError(f"{self.op} expects at least two arguments")
        if self.node_count() > 256:
            raise ValueError("expression exceeds the 256-node safety limit")
        return self

    def node_count(self) -> int:
        return 1 + sum(arg.node_count() for arg in self.args)

    def to_sympy(self) -> sp.Basic:
        if self.op == "integer":
            return sp.Integer(int(self.value))
        if self.op == "rational":
            numerator, denominator = str(self.value).split("/", 1)
            return sp.Rational(int(numerator), int(denominator))
        if self.op == "symbol":
            name = str(self.value)
            if not name.replace("_", "").isalnum() or name[0].isdigit():
                raise ValueError(f"unsafe symbol: {name}")
            return sp.Symbol(name, real=True)
        if self.op == "pi":
            return sp.pi
        args = [arg.to_sympy() for arg in self.args]
        constructors: dict[str, Any] = {
            "add": sp.Add,
            "mul": sp.Mul,
            "pow": sp.Pow,
            "sin": sp.sin,
            "cos": sp.cos,
            "tan": sp.tan,
            "asin": sp.asin,
            "acos": sp.acos,
            "atan": sp.atan,
            "abs": sp.Abs,
            "eq": sp.Eq,
            "lt": sp.StrictLessThan,
            "le": sp.LessThan,
            "gt": sp.StrictGreaterThan,
            "ge": sp.GreaterThan,
        }
        return constructors[self.op](*args)

    @classmethod
    def from_sympy(cls, expr: sp.Basic) -> "ExprAST":
        if expr == sp.pi:
            return cls(op="pi")
        if isinstance(expr, sp.Integer):
            return cls(op="integer", value=int(expr))
        if isinstance(expr, sp.Rational):
            return cls(op="rational", value=f"{expr.p}/{expr.q}")
        if isinstance(expr, sp.Symbol):
            if str(expr) == "pi":
                return cls(op="pi")
            return cls(op="symbol", value=str(expr))
        mapping = {
            sp.Add: "add",
            sp.Mul: "mul",
            sp.Pow: "pow",
            sp.sin: "sin",
            sp.cos: "cos",
            sp.tan: "tan",
            sp.asin: "asin",
            sp.acos: "acos",
            sp.atan: "atan",
            sp.Abs: "abs",
            sp.Equality: "eq",
            sp.StrictLessThan: "lt",
            sp.LessThan: "le",
            sp.StrictGreaterThan: "gt",
            sp.GreaterThan: "ge",
        }
        for kind, op in mapping.items():
            if isinstance(expr, kind):
                return cls(op=op, args=[cls.from_sympy(arg) for arg in expr.args])
        raise ValueError(f"unsupported SymPy node: {type(expr).__name__}")


class RawProblem(BaseModel):
    question: str
    options: list[str] | str | None = None
    source_id: str | None = None
    images: list[str] = Field(default_factory=list)


class AngleState(BaseModel):
    symbol: str
    unit: Literal["radian", "degree", "unspecified"] = "unspecified"
    domain: str = "Reals"
    quadrant: int | None = Field(default=None, ge=1, le=4)
    principal_range: str | None = None
    modulus: str | None = None


class ExpressionSpec(BaseModel):
    id: str
    source_latex: str
    ast: ExprAST


class ConstraintSpec(BaseModel):
    kind: Literal["equation", "inequality", "membership", "property"]
    expression: ExprAST | None = None
    name: str | None = None
    value: str | None = None


class GoalSpec(BaseModel):
    task_family: TaskFamily
    operator: str
    target_refs: list[str]
    property_names: list[str] = Field(default_factory=list)
    completeness: Literal["all_real", "restricted", "not_applicable"] = "not_applicable"


class TrigURM(BaseModel):
    schema_version: Literal["0.1"] = "0.1"
    angles: list[AngleState] = Field(default_factory=list)
    expressions: list[ExpressionSpec]
    constraints: list[ConstraintSpec] = Field(default_factory=list)
    goal: GoalSpec
    derived_facts: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_references(self) -> "TrigURM":
        ids = {item.id for item in self.expressions}
        missing = set(self.goal.target_refs) - ids
        if missing:
            raise ValueError(f"goal references unknown expressions: {sorted(missing)}")
        return self


class IntervalCell(BaseModel):
    start: ExprAST
    end: ExprAST
    left_open: bool = False
    right_open: bool = False


class PeriodicSet(BaseModel):
    period: ExprAST
    points: list[ExprAST] = Field(default_factory=list)
    intervals: list[IntervalCell] = Field(default_factory=list)
    excluded_points: list[ExprAST] = Field(default_factory=list)
    full_period: bool = False
    variable: str = "x"


class SetSpec(BaseModel):
    """Structured one-dimensional real set used by frozen gold labels."""

    kind: Literal["empty", "reals", "finite", "interval", "union", "difference"]
    elements: list[ExprAST] = Field(default_factory=list)
    start: ExprAST | None = None
    end: ExprAST | None = None
    left_open: bool = False
    right_open: bool = False
    children: list["SetSpec"] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_shape(self) -> "SetSpec":
        if self.kind == "finite" and not self.elements:
            raise ValueError("finite set requires at least one element")
        if self.kind == "interval" and self.start is None and not self.left_open:
            raise ValueError("an interval unbounded below must be left-open")
        if self.kind == "interval" and self.end is None and not self.right_open:
            raise ValueError("an interval unbounded above must be right-open")
        if self.kind == "union" and len(self.children) < 2:
            raise ValueError("union requires at least two child sets")
        if self.kind == "difference" and len(self.children) != 2:
            raise ValueError("difference requires exactly two child sets")
        return self

    def to_sympy(self) -> sp.Set:
        if self.kind == "empty":
            return sp.EmptySet
        if self.kind == "reals":
            return sp.S.Reals
        if self.kind == "finite":
            return sp.FiniteSet(*(item.to_sympy() for item in self.elements))
        if self.kind == "interval":
            start = -sp.oo if self.start is None else self.start.to_sympy()
            end = sp.oo if self.end is None else self.end.to_sympy()
            return sp.Interval(start, end, left_open=self.left_open, right_open=self.right_open)
        children = [item.to_sympy() for item in self.children]
        if self.kind == "union":
            return sp.Union(*children)
        return sp.Complement(children[0], children[1])

    @classmethod
    def from_sympy(cls, value: sp.Set) -> "SetSpec":
        if value == sp.EmptySet:
            return cls(kind="empty")
        if value == sp.S.Reals:
            return cls(kind="reals")
        if isinstance(value, sp.FiniteSet):
            return cls(kind="finite", elements=[ExprAST.from_sympy(item) for item in sorted(value, key=sp.default_sort_key)])
        if isinstance(value, sp.Interval):
            return cls(
                kind="interval",
                start=None if value.start == sp.S.NegativeInfinity else ExprAST.from_sympy(value.start),
                end=None if value.end == sp.S.Infinity else ExprAST.from_sympy(value.end),
                left_open=bool(value.left_open),
                right_open=bool(value.right_open),
            )
        if isinstance(value, sp.Union):
            return cls(kind="union", children=[cls.from_sympy(item) for item in value.args])
        if isinstance(value, sp.Complement):
            return cls(kind="difference", children=[cls.from_sympy(item) for item in value.args])
        raise ValueError(f"unsupported set node: {type(value).__name__}")


class GoldAnswer(BaseModel):
    """Discriminated mathematical gold; never a presentation string."""

    kind: Literal["expression", "set", "periodic_set"]
    expression: ExprAST | None = None
    set_value: SetSpec | None = None
    periodic_set: PeriodicSet | None = None

    @model_validator(mode="after")
    def validate_payload(self) -> "GoldAnswer":
        payloads = {
            "expression": self.expression,
            "set": self.set_value,
            "periodic_set": self.periodic_set,
        }
        if payloads[self.kind] is None:
            raise ValueError(f"{self.kind} gold requires its matching payload")
        if sum(value is not None for value in payloads.values()) != 1:
            raise ValueError("gold answer must contain exactly one mathematical payload")
        return self

    @classmethod
    def from_value(cls, value: Any) -> "GoldAnswer":
        if isinstance(value, PeriodicSet):
            return cls(kind="periodic_set", periodic_set=value)
        if isinstance(value, sp.Set):
            return cls(kind="set", set_value=SetSpec.from_sympy(value))
        if isinstance(value, sp.Basic):
            return cls(kind="expression", expression=ExprAST.from_sympy(value))
        raise ValueError(f"unsupported gold value: {type(value).__name__}")


class TraceStep(BaseModel):
    tmm_id: str
    operation: str
    input_summary: str
    output_summary: str
    verified: bool = False


class SolveResult(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    status: Literal["solved", "abstained"]
    answer_kind: str | None = None
    answer: str | None = None
    option: str | None = None
    value: Any = None
    expression: ExprAST | None = None
    set_value: SetSpec | None = None
    periodic_set: PeriodicSet | None = None
    trace: list[TraceStep] = Field(default_factory=list)
    abstain_code: AbstainCode | None = None
    message: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def abstain(cls, code: AbstainCode, message: str, trace: list[TraceStep] | None = None) -> "SolveResult":
        return cls(status="abstained", abstain_code=code, message=message, trace=trace or [])


class SolverConfig(BaseModel):
    model_name: str = "qwen3.7-flash-2026-07-15"
    temperature: float = 0.01
    cas_timeout_seconds: float = 2.0
    max_tmm_steps: int = 8
    identity_max_depth: int = 4
    identity_beam_width: int = 12
    enable_periodic_completion: bool = True
    enable_validator: bool = True
