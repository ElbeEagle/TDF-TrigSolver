import hashlib
import json
from pathlib import Path

import pytest
import sympy as sp

from annotation_app.core import (
    AnnotationSession,
    DraftValidationError,
    TemplateBoundaryError,
    default_draft,
    load_machine_seed,
    load_sealed_template,
    validate_draft,
)


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "data" / "benchmarks" / "trig_pilot_v1" / "test_annotation_template.jsonl"
MANIFEST = ROOT / "data" / "benchmarks" / "trig_pilot_v1" / "manifest.json"
SEED = ROOT / "annotation_app" / "seeds" / "test_seed_v1.json"


def _record(rows: list[dict], source_id: str) -> dict:
    return next(row for row in rows if row["source_id"] == source_id)


def _with_crlf(value: bytes) -> bytes:
    return value.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")


def test_sealed_template_contains_no_prefilled_or_forbidden_fields():
    rows = load_sealed_template(TEMPLATE)
    assert len(rows) == 50
    assert all(row["oracle_urm"] is None for row in rows)
    assert all(row["gold_answer"] is None for row in rows)
    assert all(row["gold_option"] is None for row in rows)


def test_seeded_annotation_session_accepts_windows_crlf_checkout(tmp_path: Path):
    benchmark_dir = tmp_path / "benchmark"
    benchmark_dir.mkdir()
    template = benchmark_dir / TEMPLATE.name
    manifest = benchmark_dir / MANIFEST.name
    seed = tmp_path / SEED.name
    template.write_bytes(_with_crlf(TEMPLATE.read_bytes()))
    manifest.write_bytes(_with_crlf(MANIFEST.read_bytes()))
    seed.write_bytes(_with_crlf(SEED.read_bytes()))

    session = AnnotationSession(template, tmp_path / "runs", "annotator_a", seed)

    assert len(session.template_rows) == 50
    assert session.seed_bundle is not None
    assert len(session.seed_bundle.drafts) == 50


def test_crlf_normalization_does_not_hide_other_template_changes(tmp_path: Path):
    template = tmp_path / TEMPLATE.name
    template.write_bytes(_with_crlf(TEMPLATE.read_bytes()) + b" ")
    (tmp_path / MANIFEST.name).write_bytes(_with_crlf(MANIFEST.read_bytes()))

    with pytest.raises(TemplateBoundaryError, match="template hash"):
        load_sealed_template(template)


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


def test_machine_seed_covers_and_validates_all_fifty_records():
    rows = load_sealed_template(TEMPLATE)
    seed = load_machine_seed(SEED, TEMPLATE, rows)
    assert seed.seed_kind == "machine_prepared_silver"
    assert len(seed.drafts) == 50
    assert set(seed.drafts) == {row["source_id"] for row in rows}
    assert all(validate_draft(row, seed.drafts[row["source_id"]]) for row in rows)


def test_machine_seed_equation_points_satisfy_every_equation():
    rows = load_sealed_template(TEMPLATE)
    seed = load_machine_seed(SEED, TEMPLATE, rows)
    equation_rows = [row for row in rows if row["task_family"] == "EQUATION"]
    assert len(equation_rows) == 10
    for row in equation_rows:
        validated = validate_draft(row, seed.drafts[row["source_id"]])
        relation = validated.oracle_urm.expressions[0].ast.to_sympy()
        periodic = validated.gold_answer.periodic_set
        assert isinstance(relation, sp.Equality)
        assert periodic is not None
        variable = sp.Symbol(periodic.variable, real=True)
        period = periodic.period.to_sympy()
        for point_ast in periodic.points:
            point = point_ast.to_sympy()
            for candidate in (point, point + period):
                residual = sp.N((relation.lhs - relation.rhs).subs(variable, candidate), 30)
                assert abs(complex(residual)) < 1e-12, (row["source_id"], candidate, residual)


def test_seeded_sessions_share_no_mutable_draft_state(tmp_path: Path):
    session_a = AnnotationSession(TEMPLATE, tmp_path, "annotator_a", SEED)
    session_b = AnnotationSession(TEMPLATE, tmp_path, "annotator_b", SEED)
    record_a = session_a.record("18032-test")
    record_b = session_b.record("18032-test")
    draft_a = session_a.initial_draft(record_a)
    draft_b = session_b.initial_draft(record_b)
    assert draft_a["gold_option"] == draft_b["gold_option"] == "A"

    draft_a["notes"] = "annotator A private change"
    session_a.save_draft(record_a["source_id"], draft_a)
    assert session_b.drafts == {}
    assert session_b.initial_draft(record_b)["notes"] == ""
    resumed_a = AnnotationSession(TEMPLATE, tmp_path, "annotator_a", SEED)
    assert resumed_a.drafts[record_a["source_id"]]["notes"] == "annotator A private change"


def test_tampered_seed_is_rejected(tmp_path: Path):
    payload = json.loads(SEED.read_text(encoding="utf-8"))
    payload["template_sha256"] = "0" * 64
    seed_path = tmp_path / "seed.json"
    seed_path.write_text(json.dumps(payload), encoding="utf-8")
    rows = load_sealed_template(TEMPLATE)
    with pytest.raises(TemplateBoundaryError, match="hash"):
        load_machine_seed(seed_path, TEMPLATE, rows)


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
