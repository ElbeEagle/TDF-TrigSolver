#!/usr/bin/env python3
"""Explainable deterministic rules for TDF trigonometry extraction."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from typing import Any, Iterable

from . import RULE_VERSION
from .dataset_adapters import NormalizedRecord

LABELS = ("A", "B", "C", "MIXED", "UNCERTAIN")
DECISIVE = 4
STRONG = 2
SUPPORTING = 1

TRIG = re.compile(
    r"(?:\\(?:sin|cos|tan|cot|sec|csc|arcsin|arccos|arctan)\b|"
    r"(?<![A-Za-z])(?:sin|cos|tan|cot|sec|csc|arcsin|arccos|arctan)(?![A-Za-z])|"
    r"三角函数|正弦|余弦|正切|余切|反正弦|反余弦|反正切|trigonometric|sine|cosine|tangent)",
    re.IGNORECASE,
)
TRIANGLE = re.compile(
    r"(?:\\triangle|△|三角形|triangle|Rt\s*\\triangle|锐角△|钝角△)", re.IGNORECASE
)
FUNCTION_OBJECT = re.compile(
    r"(?:(?:函数|function)[^$\n]{0,50}?(?:f\s*\([^)]*\)\s*=|y\s*=)|"
    r"f\s*\([^)]*\)\s*=|y\s*=)[^$\n]{0,100}?"
    r"(?:\\(?:sin|cos|tan|cot)|\b(?:sin|cos|tan|cot)\b|正弦|余弦|正切)",
    re.IGNORECASE,
)
A_CONCEPT = re.compile(
    r"(?:三角函数|正弦函数|余弦函数|正切函数|反三角函数|反正弦|反余弦|反正切|"
    r"诱导公式|和差公式|倍角公式|半角公式|辅助角公式|万能公式|单位圆|弧度制|"
    r"正弦线|余弦线|正切线|"
    r"trigonometric\s+(?:function|identity|equation|inequality)|inverse\s+trig)",
    re.IGNORECASE,
)
A_PROPERTY = re.compile(
    r"(?:定义域|值域|周期|振幅|频率|相位|中线|单调|奇偶|对称|最大值|最小值|最值|"
    r"零点|图[像象]|平移|伸缩|变换|domain|range|period|amplitude|frequency|phase|"
    r"midline|monotoni|symmetr|maximum|minimum|zero|graph|transform|shift)",
    re.IGNORECASE,
)
A_DIRECT_TASK = re.compile(
    r"(?:求|计算|化简|证明|解(?:方程|不等式)?|(?:的)?值(?:为|是)|相等|相同|等于|成立|恒成立|取值范围|比较|"
    r"evaluate|simplif|prove|solve|find|determine|value|identity|equation|inequality)",
    re.IGNORECASE,
)
A_EQUATION = re.compile(
    r"(?:三角方程|三角不等式|(?:方程|不等式|equation|inequality)[\s\S]{0,100}?"
    r"(?:\\(?:sin|cos|tan)|\b(?:sin|cos|tan)\b)|"
    r"(?:\\(?:sin|cos|tan)|\b(?:sin|cos|tan)\b)[\s\S]{0,100}?(?:=|≤|≥|<|>))",
    re.IGNORECASE,
)
PERIODIC_MODEL = re.compile(
    r"(?:(?:匀速旋转|来回摆动|单摆|潮汐|港口.{0,30}水深|周期现象|绕.{0,20}旋转|"
    r"uniform(?:ly)?\s+rotat|pendulum|tide|periodic)[\s\S]{0,180}?"
    r"(?:函数|function|时间|time)|"
    r"(?:函数|function)[\s\S]{0,180}?(?:匀速旋转|来回摆动|单摆|潮汐|港口|periodic))",
    re.IGNORECASE,
)
B_LAW_OR_RATIO = re.compile(
    r"(?:正弦定理|余弦定理|锐角三角函数|解三角形|sine\s+law|cosine\s+law|"
    r"law\s+of\s+(?:sines|cosines)|trigonometric\s+ratio)",
    re.IGNORECASE,
)
B_MEASUREMENT = re.compile(
    r"(?:(?:测量|估算)[^，。；;]{0,24}?(?:高|距离|宽)|测高|测距|塔高|树高|大树|"
    r"影长|大坝|水库|河流|河宽|岛屿|"
    r"建筑物.{0,20}高|仰角|俯角|坡角|坡度|方位角|"
    r"ladder|tower|height|distance|angle\s+of\s+(?:elevation|depression))",
    re.IGNORECASE,
)
B_GEOMETRY_TARGET = re.compile(
    r"(?:求[^，。；;]{0,12}?(?:边|角|面积|周长|高度|距离)|"
    r"边长|三边|对边|内角|角度|面积|周长|弦长|高为|高度|距离|投影|"
    r"side\s+length|remaining\s+side|\bangle\b|area|perimeter|height|distance)",
    re.IGNORECASE,
)
B_NUMERIC_ANGLE = re.compile(r"(?:\d+(?:\.\d+)?\s*(?:\^\{?\\circ\}?|°)|\\frac\{?\\pi)")
B_SIDE_ASSIGNMENT = re.compile(
    r"(?<![A-Za-z])(?:a|b|c)\s*=\s*(?:[-+]?\d|\\sqrt|\\frac)"
)
B_ANGLE_ASSIGNMENT = re.compile(
    r"(?:(?:\\angle\s*)?[ABC]|[A-Z]{3})\s*=\s*[^,，。;；]{0,30}?"
    r"(?:\^\{?\\circ\}?|°|\\pi)",
    re.IGNORECASE,
)
B_POLAR_GEOMETRY = re.compile(
    r"(?:极坐标|柱坐标|球坐标|参数方程|圆[雉锥]曲线|polar\s+coordinate|"
    r"parametric\s+equation|conic|cylindrical\s+coordinate|"
    r"spherical\s+coordinate|\\rho\s*=)",
    re.IGNORECASE,
)
B_GENERAL_GEOMETRY = re.compile(
    r"(?:圆|圆心|半径|\\odot|矩形|正方形|菱形|多边形|屋顶|大坝|水库|"
    r"circle|chord|tangent|radius|rectangle|polygon)",
    re.IGNORECASE,
)
B_GEOMETRY_CONSTRAINT = re.compile(
    r"(?:等腰|直角三角形|锐角三角形|钝角三角形|重心|外接圆|内接|边长|面积|"
    r"isosceles|right\s+triangle|circumcircle|inscribed)",
    re.IGNORECASE,
)
C_CONTEXT = re.compile(
    r"(?:偏微分方程|PDE|finite\s+element|数值算法|优化算法|损失函数|残差|"
    r"机器人|逆运动学|robot|inverse\s+kinematics|信号处理|signal\s+processing|"
    r"Fourier|傅里叶|谐波|harmonic|controller|control\s+system|neural\s+network)",
    re.IGNORECASE,
)
MULTIPART = re.compile(r"(?:\(\s*[12IⅡ一二]\s*\)|（\s*[12一二]\s*）|\b(?:I|II)\.)")
MULTIPART_TASK = re.compile(
    r"(?:\(\s*(?:1|I)\s*\)|（\s*1\s*）)[\s\S]{0,400}?(?:求|证明|find|prove)"
    r"[\s\S]{0,800}?(?:\(\s*(?:2|II)\s*\)|（\s*2\s*）)[\s\S]{0,400}?"
    r"(?:求|证明|find|prove)",
    re.IGNORECASE,
)
IMAGE_MARKER = re.compile(r"(?:<ImageHere>|如图|as\s+shown|given\s+figure)", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class Evidence:
    rule_id: str
    category: str
    weight: int
    field: str
    snippet: str
    reason: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "category": self.category,
            "weight": self.weight,
            "field": self.field,
            "snippet": self.snippet,
            "reason": self.reason,
        }


def _snippet(text: str, match: re.Match[str] | None, radius: int = 90) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    if not match:
        return compact[: 2 * radius]
    matched = re.sub(r"\s+", " ", match.group(0)).strip()
    location = compact.lower().find(matched.lower())
    if location < 0:
        return compact[: 2 * radius]
    return compact[max(0, location - radius) : location + len(matched) + radius]


def _add(
    evidence: list[Evidence],
    rule_id: str,
    category: str,
    weight: int,
    field: str,
    text: str,
    match: re.Match[str] | None,
    reason: str,
) -> None:
    evidence.append(
        Evidence(rule_id, category, weight, field, _snippet(text, match), reason)
    )


def classify_record(record: NormalizedRecord) -> dict[str, Any] | None:
    problem = re.sub(r"https?://\S+", " ", record.problem_text or "")
    auxiliary = re.sub(r"https?://\S+", " ", record.auxiliary_text or "")
    all_text = "\n".join(x for x in (problem, auxiliary) if x)
    p_trig = TRIG.search(problem)
    a_trig = TRIG.search(auxiliary)
    triangle = TRIANGLE.search(problem)
    b_measure = B_MEASUREMENT.search(problem)
    b_target = B_GEOMETRY_TARGET.search(problem)
    b_law = B_LAW_OR_RATIO.search(all_text)
    side_assignments = B_SIDE_ASSIGNMENT.findall(problem)
    angle_assignment = B_ANGLE_ASSIGNMENT.search(problem)
    inferred_law = bool(triangle and len(side_assignments) >= 2 and angle_assignment)
    polar_geometry = B_POLAR_GEOMETRY.search(problem)
    general_geometry = B_GENERAL_GEOMETRY.search(problem)
    periodic_model_match = PERIODIC_MODEL.search(problem)
    named_concept_match = A_CONCEPT.search(problem)
    diagram_ratio = IMAGE_MARKER.search(problem)
    diagram_angle = re.search(r"(?:\\angle|角)", problem)
    semantic_b = bool(
        (triangle and b_target and (p_trig or b_law))
        or inferred_law
        or b_measure
        or (
            (p_trig or a_trig)
            and (polar_geometry or general_geometry)
            and not periodic_model_match
            and not named_concept_match
        )
    )
    semantic_a = bool(periodic_model_match or FUNCTION_OBJECT.search(problem))
    c_context = C_CONTEXT.search(all_text)

    if not (p_trig or a_trig or semantic_a or semantic_b or (c_context and TRIG.search(all_text))):
        return None

    evidence: list[Evidence] = []

    function_match = FUNCTION_OBJECT.search(problem)
    if function_match and not polar_geometry:
        _add(
            evidence,
            "A_FUNCTION_OBJECT",
            "A",
            DECISIVE,
            "problem_text",
            problem,
            function_match,
            "三角函数本身被显式建模为函数对象",
        )
    concept_match = named_concept_match
    if concept_match:
        _add(
            evidence,
            "A_NAMED_CONCEPT",
            "A",
            DECISIVE,
            "problem_text",
            problem,
            concept_match,
            "题面直接命名三角函数概念、公式或反函数",
        )
    property_match = A_PROPERTY.search(problem)
    if p_trig and property_match:
        _add(
            evidence,
            "A_FUNCTION_PROPERTY",
            "A",
            STRONG,
            "problem_text",
            problem,
            property_match,
            "考查三角函数图像或结构性质",
        )
    equation_match = A_EQUATION.search(problem)
    if equation_match and not (
        triangle or polar_geometry or general_geometry or (diagram_ratio and diagram_angle)
    ):
        _add(
            evidence,
            "A_TRIG_EQUATION",
            "A",
            DECISIVE,
            "problem_text",
            problem,
            equation_match,
            "三角方程或不等式是直接求解对象",
        )
    direct_match = A_DIRECT_TASK.search(problem)
    geometry_dominant = bool(
        (triangle or polar_geometry or general_geometry)
        and (
            b_target
            or b_law
            or inferred_law
            or (triangle and p_trig)
            or (diagram_ratio and diagram_angle and p_trig)
            or polar_geometry
            or general_geometry
        )
        and not function_match
    )
    if p_trig and direct_match and not geometry_dominant:
        _add(
            evidence,
            "A_DIRECT_EXPRESSION_TASK",
            "A",
            DECISIVE,
            "problem_text",
            problem,
            p_trig,
            "三角表达式本身是求值、化简、比较、证明或求解对象",
        )
    model_match = periodic_model_match
    if model_match:
        _add(
            evidence,
            "A_PERIODIC_MODEL",
            "A",
            DECISIVE,
            "problem_text",
            problem,
            model_match,
            "题面描述正弦型周期现象或周期函数建模",
        )
    if p_trig:
        _add(
            evidence,
            "A_TRIG_TOKEN",
            "A",
            SUPPORTING,
            "problem_text",
            problem,
            p_trig,
            "题面含三角词符，仅作为弱支持证据",
        )
    elif a_trig:
        _add(
            evidence,
            "A_AUXILIARY_TRIG_TOKEN",
            "A",
            SUPPORTING,
            "auxiliary_text",
            auxiliary,
            a_trig,
            "三角词符只出现在解析或答案中",
        )

    if triangle:
        _add(
            evidence,
            "B_TRIANGLE_CONTEXT",
            "B",
            STRONG,
            "problem_text",
            problem,
            triangle,
            "题目以三角形或其几何元素为语境",
        )
    if triangle and p_trig and not function_match:
        _add(
            evidence,
            "B_TRIANGLE_TRIG_TOOL",
            "B",
            DECISIVE,
            "problem_text",
            problem,
            p_trig,
            "三角表达式受三角形边角关系约束并服务于几何推理",
        )
    if (
        diagram_ratio
        and diagram_angle
        and p_trig
        and not function_match
        and not periodic_model_match
    ):
        _add(
            evidence,
            "B_DIAGRAM_TRIG_RATIO",
            "B",
            DECISIVE,
            "problem_text",
            problem,
            diagram_ratio,
            "几何图中的角与三角比是主要求解对象",
        )
    if b_law:
        field = "problem_text" if B_LAW_OR_RATIO.search(problem) else "auxiliary_text"
        source = problem if field == "problem_text" else auxiliary
        _add(
            evidence,
            "B_TRIG_LAW_OR_RATIO",
            "B",
            DECISIVE,
            field,
            source,
            B_LAW_OR_RATIO.search(source),
            "正余弦定理或锐角三角比作为几何求解工具",
        )
    if b_measure:
        _add(
            evidence,
            "B_MEASUREMENT_APPLICATION",
            "B",
            DECISIVE,
            "problem_text",
            problem,
            b_measure,
            "目标是测高、测距、方位或其他几何测量",
        )
    if triangle and b_target and (p_trig or a_trig or b_law):
        _add(
            evidence,
            "B_GEOMETRY_TARGET",
            "B",
            DECISIVE,
            "problem_text",
            problem,
            b_target,
            "边、角、面积或其他几何量是主要目标",
        )
    if inferred_law:
        _add(
            evidence,
            "B_INFERRED_SIDE_ANGLE_CONFIGURATION",
            "B",
            DECISIVE,
            "problem_text",
            problem,
            angle_assignment,
            "题面给出边角配置，求解需要正弦或余弦定理",
        )
    if (p_trig or a_trig) and polar_geometry and not periodic_model_match:
        _add(
            evidence,
            "B_POLAR_COORDINATE_GEOMETRY",
            "B",
            DECISIVE,
            "problem_text",
            problem,
            polar_geometry,
            "三角表达式服务于极坐标、柱坐标或球坐标几何目标",
        )
    if (
        (p_trig or a_trig)
        and general_geometry
        and not periodic_model_match
        and not named_concept_match
    ):
        _add(
            evidence,
            "B_GENERAL_GEOMETRY_WITH_TRIG",
            "B",
            DECISIVE,
            "problem_text",
            problem,
            general_geometry,
            "三角比服务于圆、弦、切线或其他几何量求解",
        )
    geom_constraint = B_GEOMETRY_CONSTRAINT.search(problem)
    if function_match and triangle and geom_constraint:
        _add(
            evidence,
            "B_ESSENTIAL_GEOMETRY_CONSTRAINT",
            "B",
            DECISIVE,
            "problem_text",
            problem,
            geom_constraint,
            "几何结构是恢复或推理三角函数关系的必要条件",
        )

    if c_context:
        _add(
            evidence,
            "C_INCIDENTAL_DOMAIN_CONTEXT",
            "C",
            DECISIVE,
            "problem_text" if C_CONTEXT.search(problem) else "auxiliary_text",
            all_text,
            c_context,
            "三角词符位于优化、PDE、机器人、信号或数值算法语境",
        )

    scores = Counter({"A": 0, "B": 0, "C": 0})
    for item in evidence:
        scores[item.category] += item.weight
    a_score, b_score, c_score = scores["A"], scores["B"], scores["C"]
    multipart = bool(MULTIPART_TASK.search(problem))
    trace = [
        f"candidate gate: problem_trig={bool(p_trig)}, auxiliary_trig={bool(a_trig)}, "
        f"semantic_A={semantic_a}, semantic_B={semantic_b}",
        f"scores: A={a_score}, B={b_score}, C={c_score}",
    ]

    if c_score >= DECISIVE and a_score < DECISIVE and b_score < DECISIVE:
        label = "C"
        trace.append("C reached decisive threshold without direct A/B evidence")
    elif a_score >= DECISIVE and b_score >= DECISIVE:
        mixed_structure = multipart or bool(
            function_match and triangle and geom_constraint
        )
        if mixed_structure:
            label = "MIXED"
            trace.append("A and B are both core reasoning objects")
        elif geometry_dominant and not function_match:
            label = "B"
            trace.append("triangle target dominates incidental trig expression")
        else:
            label = "UNCERTAIN"
            trace.append("A/B conflict cannot be resolved from available fields")
    elif a_score >= DECISIVE and b_score < DECISIVE and c_score < DECISIVE:
        label = "A"
        trace.append("direct trigonometric-function evidence reached threshold")
    elif b_score >= DECISIVE and a_score < DECISIVE and c_score < DECISIVE:
        label = "B"
        trace.append("geometry-with-trigonometry evidence reached threshold")
    else:
        label = "UNCERTAIN"
        trace.append("candidate has only weak, auxiliary-only, or conflicting evidence")

    opposing = max(
        score for category, score in scores.items() if category != label and category in {"A", "B", "C"}
    ) if label in {"A", "B", "C"} else max(a_score, b_score, c_score)
    has_decisive = any(item.category == label and item.weight == DECISIVE for item in evidence)
    if label in {"A", "B", "C"} and opposing < DECISIVE and (
        scores[label] >= 6 or has_decisive
    ):
        confidence = "high"
    else:
        confidence = "medium"
    review_required = label in {"MIXED", "UNCERTAIN"} or confidence != "high"

    return {
        "label": label,
        "confidence": confidence,
        "review_required": review_required,
        "scores": {key: scores[key] for key in ("A", "B", "C")},
        "matched_rules": [item.as_dict() for item in evidence],
        "decision_trace": trace,
        "rule_version": RULE_VERSION,
    }


def matched_rule_ids(classification: dict[str, Any]) -> Iterable[str]:
    for rule in classification.get("matched_rules", []):
        yield str(rule.get("rule_id"))
