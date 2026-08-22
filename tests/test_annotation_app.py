import hashlib
import json
from pathlib import Path

import pytest

from annotation_app.core import (
    AnnotationSession,
    DraftValidationError,
    TemplateBoundaryError,
    default_draft,
    load_sealed_template,
    validate_draft,
)


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "data" / "benchmarks" / "trig_pilot_v1" / "test_annotation_template.jsonl"


def _record(rows: list[dict], source_id: str) -> dict:
    return next(row for row in rows if row["source_id"] == source_id)


def test_sealed_template_contains_no_prefilled_or_forbidden_fields():
    rows = load_sealed_template(TEMPLATE)
    assert len(rows) == 50
    assert all(row["oracle_urm"] is None for row in rows)
    assert all(row["gold_answer"] is None for row in rows)
    assert all(row["gold_option"] is None for row in rows)


def test_template_rejects_hidden_source_analysis_even_with_matching_hash(tmp_path: Path):
    rows = [json.loads(line) for line in TEMPLATE.read_text(encoding="utf-8").splitlines()]
    rows[0]["analysis"] = "must never be exposed"
    content = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)
    template = tmp_path / "test_annotation_template.jsonl"
    template.write_text(content, encoding="utf-8")
    manifest = {"test_annotation_template_sha256": hashlib.sha256(content.encode()).hexdigest()}
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(TemplateBoundaryError, match="forbidden field"):
        load_sealed_template(template)


def test_template_rejects_prior_human_annotation_even_with_matching_hash(tmp_path: Path):
    rows = [json.loads(line) for line in TEMPLATE.read_text(encoding="utf-8").splitlines()]
    rows[0]["annotation"]["annotator"] = "prior_annotator"
    rows[0]["annotation"]["annotation_status"] = "completed"
    content = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)
    template = tmp_path / "test_annotation_template.jsonl"
    template.write_text(content, encoding="utf-8")
    manifest = {"test_annotation_template_sha256": hashlib.sha256(content.encode()).hexdigest()}
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(TemplateBoundaryError, match="prior human annotation"):
        load_sealed_template(template)


def test_two_annotators_have_isolated_output_and_resume_state(tmp_path: Path):
    session_a = AnnotationSession(TEMPLATE, tmp_path, "annotator_a")
    session_b = AnnotationSession(TEMPLATE, tmp_path, "annotator_b")
    assert session_a.paths.root != session_b.paths.root
    assert session_a.paths.annotations != session_b.paths.annotations

    record = session_a.record("18046-test")
    draft = default_draft(record)
    draft.update(
        {
            "target_latex": r"\sin 165^{\circ}",
            "gold_expression": r"\frac{\sqrt{6}-\sqrt{2}}{4}",
            "gold_option": "D",
        }
    )
    validated = validate_draft(record, draft)
    session_a.complete(record["source_id"], validated, "independent trigonometric reduction")

    assert session_a.completed_count == 1
    assert session_b.completed_count == 0
    assert AnnotationSession(TEMPLATE, tmp_path, "annotator_a").completed_count == 1
    assert AnnotationSession(TEMPLATE, tmp_path, "annotator_b").completed_count == 0


def test_interval_set_gold_is_structured():
    rows = load_sealed_template(TEMPLATE)
    record = _record(rows, "17464-test")
    draft = default_draft(record)
    draft.update(
        {
            "target_latex": r"\left|\sin x\right|+\sin x",
            "operator": "range",
            "gold_kind": "set",
            "set_kind": "interval",
            "set_primary": "[0,2]",
            "gold_option": "D",
        }
    )
    validated = validate_draft(record, draft)
    assert validated.gold_answer.kind == "set"
    assert validated.gold_answer.set_value is not None
    assert validated.gold_answer.set_value.kind == "interval"
    target_ast = validated.oracle_urm.expressions[0].ast
    assert "abs" in {node.op for node in target_ast.args} | {target_ast.op}


def test_equation_gold_requires_normalized_periodic_set():
    rows = load_sealed_template(TEMPLATE)
    record = _record(rows, "17774-test")
    draft = default_draft(record)
    draft.update(
        {
            "target_latex": r"\sin(\pi+x)=-\sqrt{3}\cos(2\pi-x)",
            "period": r"\pi",
            "points": r"\frac{\pi}{3}",
            "gold_option": "A",
        }
    )
    validated = validate_draft(record, draft)
    assert validated.oracle_urm.goal.completeness == "all_real"
    assert validated.gold_answer.kind == "periodic_set"
    assert validated.gold_answer.periodic_set is not None
    assert validated.gold_answer.periodic_set.period.to_sympy().equals(
        validated.gold_answer.periodic_set.points[0].to_sympy() * 3
    )

    draft["points"] = r"\frac{4\pi}{3}"
    with pytest.raises(DraftValidationError, match="fundamental interval"):
        validate_draft(record, draft)


def test_open_question_cannot_store_gold_option():
    rows = load_sealed_template(TEMPLATE)
    record = _record(rows, "3597-test")
    draft = default_draft(record)
    draft.update(
        {
            "target_latex": r"\cos 30^{\circ}\tan 60^{\circ}",
            "gold_expression": r"\frac{3}{2}",
            "gold_option": "A",
        }
    )
    validated = validate_draft(record, draft)
    assert validated.gold_option is None
