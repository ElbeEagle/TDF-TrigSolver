"""Streamlit UI for one isolated assisted human-review session."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from annotation_app.core import AnnotationError, AnnotationSession, extract_formula_strings  # noqa: E402
from annotation_app.editor import render_editor  # noqa: E402


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--annotator", required=True)
    parser.add_argument("--template", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--seed", required=True)
    args, _ = parser.parse_known_args(sys.argv[1:])
    return args


@st.cache_resource(show_spinner=False)
def _session(template: str, workspace: str, annotator: str, seed: str) -> AnnotationSession:
    return AnnotationSession(Path(template), Path(workspace), annotator, Path(seed))


def _next_incomplete(session: AnnotationSession, current_index: int) -> str:
    rows = session.records
    for offset in range(1, len(rows) + 1):
        row = rows[(current_index + offset) % len(rows)]
        if (row.get("annotation") or {}).get("annotation_status") != "completed":
            return row["source_id"]
    return rows[current_index]["source_id"]


def _install_sticky_styles() -> None:
    st.markdown(
        """
        <style>
        [data-testid="stLayoutWrapper"]:has(> .st-key-sticky_question_card) {
            position: sticky;
            top: 3.75rem;
            z-index: 20;
            max-height: calc(100vh - 4.75rem);
            overflow-y: auto;
            background: var(--background-color);
            box-shadow: 0 0.25rem 1rem rgba(0, 0, 0, 0.08);
        }
        .st-key-sticky_question_card {
            max-height: none;
            overflow: visible;
        }
        @media (max-width: 900px) {
            [data-testid="stLayoutWrapper"]:has(> .st-key-sticky_question_card) {
                top: 3.25rem;
                max-height: 38vh;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_question_card(record: dict) -> None:
    with st.container(key="sticky_question_card", border=True):
        st.subheader("题目")
        st.markdown((record.get("problem") or {}).get("question") or "")
        options = (record.get("problem") or {}).get("options") or []
        if options:
            st.divider()
            for index, option in enumerate(options):
                st.markdown(f"**{chr(ord('A') + index)}.** {option}")
        st.divider()
        st.caption(
            f"题型：{record['task_family']} · 输出：{record['output_format']} · 模板组：{record['template_group']}"
        )
        detected_formulas = extract_formula_strings((record.get("problem") or {}).get("question") or "")
        with st.expander("题面公式"):
            if detected_formulas:
                for index, formula in enumerate(detected_formulas, start=1):
                    st.code(f"E{index}: {formula}", language=None)
            else:
                st.info("没有自动检测到公式。")


def main() -> None:
    st.set_page_config(page_title="Trig Gold 辅助审查", page_icon="∠", layout="wide")
    _install_sticky_styles()
    args = _arguments()
    try:
        session = _session(args.template, args.workspace, args.annotator, args.seed)
    except AnnotationError as exc:
        st.error(f"安全边界检查失败：{exc}")
        st.stop()

    rows = session.records
    labels = {
        row["source_id"]: (
            f"{'✓' if (row.get('annotation') or {}).get('annotation_status') == 'completed' else '○'} "
            f"{row['source_id']} · {row['task_family']}"
        )
        for row in rows
    }
    source_ids = [row["source_id"] for row in rows]
    if "selected_source_id" not in st.session_state:
        st.session_state.selected_source_id = source_ids[0]

    with st.sidebar:
        st.title("Gold 辅助审查")
        st.caption(f"标注者：`{session.annotator_id}`")
        st.caption(f"Silver seed：`{session.seed_bundle.seed_id}`")
        st.progress(session.completed_count / len(rows), text=f"已完成 {session.completed_count} / {len(rows)}")
        selected_source_id = st.selectbox(
            "题目",
            source_ids,
            format_func=lambda item: labels[item],
            key="selected_source_id",
        )
        current_index = source_ids.index(selected_source_id)
        left, right = st.columns(2)
        if left.button("上一题", use_container_width=True):
            st.session_state.selected_source_id = source_ids[(current_index - 1) % len(rows)]
            st.rerun()
        if right.button("下一题", use_container_width=True):
            st.session_state.selected_source_id = source_ids[(current_index + 1) % len(rows)]
            st.rerun()
        if st.button("下一道未完成", use_container_width=True):
            st.session_state.selected_source_id = _next_incomplete(session, current_index)
            st.rerun()
        st.download_button(
            "导出本人的 JSONL",
            data=session.export_bytes(),
            file_name=f"{session.annotator_id}.jsonl",
            mime="application/x-ndjson",
            use_container_width=True,
        )
        st.divider()
        st.caption("页面加载冻结空白模板、机器 Silver seed 和当前标注者目录。")
        st.caption("不读取原始答案、来源解析、solver prediction 或另一位标注者结果。")

    record = session.record(selected_source_id)
    stored_draft = session.drafts.get(selected_source_id) or session.initial_draft(record)
    status = (record.get("annotation") or {}).get("annotation_status")

    st.title(f"{record['source_id']} · {record['task_family']}")
    if status == "completed":
        st.success("该题已有一份有效人工审查。再次保存会保留审计事件并覆盖本人的旧版本。")
    st.warning(
        "Oracle-URM 和数学 Gold 均由 machine_prepared_silver 预填。"
        "标注者必须独立核算并修改错误；结构校验通过不代表数学答案正确。"
    )

    question_column, editor_column = st.columns([0.9, 1.6], gap="large")
    with question_column:
        _render_question_card(record)
    with editor_column:
        render_editor(session, record, stored_draft, selected_source_id)


if __name__ == "__main__":
    main()
