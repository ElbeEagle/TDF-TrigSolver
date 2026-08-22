"""Guided Oracle-URM and Gold editors for the Streamlit page."""

from __future__ import annotations

from typing import Any

import streamlit as st

from annotation_app.core import (
    AnnotationError,
    AnnotationSession,
    OPERATORS_BY_FAMILY,
    TaskFamily,
    validate_draft,
)


def _value(options: list[Any], current: Any) -> int:
    try:
        return options.index(current)
    except ValueError:
        return 0


def _draft_value(source_id: str, name: str, draft: dict[str, Any]) -> Any:
    key = f"{source_id}:{name}"
    return st.session_state.get(key, draft.get(name))


def render_editor(
    session: AnnotationSession,
    record: dict[str, Any],
    stored_draft: dict[str, Any],
    source_id: str,
) -> None:
    """Render one assisted-review form and persist only this annotator's state."""

    st.subheader("1. Oracle-URM")
    family = TaskFamily(record["task_family"])
    oracle_left, oracle_right = st.columns([2, 1])
    with oracle_left:
        target_latex = st.text_area(
            "目标公式 LaTeX",
            value=_draft_value(source_id, "target_latex", stored_draft) or "",
            key=f"{source_id}:target_latex",
            help="Silver 已预填题目要求处理的表达式、方程或不等式；必须人工核对。",
        )
        constraints = st.text_area(
            "显式约束（每行一条，可留空）",
            value=_draft_value(source_id, "constraints", stored_draft) or "",
            key=f"{source_id}:constraints",
            help=(
                "关系式可直接填写；属性约束写成 [property] name=value；"
                "成员约束写成 [membership] name=value。"
            ),
        )
        property_names = st.text_input(
            "性质名称（逗号分隔）",
            value=_draft_value(source_id, "property_names", stored_draft) or "",
            key=f"{source_id}:property_names",
            help="例如 amplitude, period, symmetry_axis；非性质题留空。",
        )
    with oracle_right:
        variable = st.text_input(
            "主变量",
            value=_draft_value(source_id, "variable", stored_draft) or "x",
            key=f"{source_id}:variable",
        )
        operator_options = list(OPERATORS_BY_FAMILY[family])
        operator_current = _draft_value(source_id, "operator", stored_draft)
        operator = st.selectbox(
            "操作",
            operator_options,
            index=_value(operator_options, operator_current),
            key=f"{source_id}:operator",
        )
        unit_options = ["radian", "degree", "unspecified"]
        unit_current = _draft_value(source_id, "unit", stored_draft)
        unit = st.selectbox(
            "角制",
            unit_options,
            index=_value(unit_options, unit_current),
            key=f"{source_id}:unit",
        )
        quadrant_options: list[Any] = ["", 1, 2, 3, 4]
        quadrant_current = _draft_value(source_id, "quadrant", stored_draft)
        quadrant = st.selectbox(
            "象限约束",
            quadrant_options,
            index=_value(quadrant_options, quadrant_current),
            key=f"{source_id}:quadrant",
        )
        completeness_options = ["not_applicable", "restricted", "all_real"]
        completeness_current = "all_real" if family == TaskFamily.EQUATION else _draft_value(
            source_id, "completeness", stored_draft
        )
        completeness = st.selectbox(
            "解集完整性",
            completeness_options,
            index=_value(completeness_options, completeness_current),
            disabled=family == TaskFamily.EQUATION,
            key=f"{source_id}:completeness",
        )

    st.subheader("2. 独立审查数学 Gold")
    gold_kind_options = ["expression", "set", "periodic_set"]
    gold_kind_current = "periodic_set" if family == TaskFamily.EQUATION else _draft_value(
        source_id, "gold_kind", stored_draft
    )
    gold_kind = st.selectbox(
        "Gold 类型",
        gold_kind_options,
        index=_value(gold_kind_options, gold_kind_current),
        disabled=family == TaskFamily.EQUATION,
        key=f"{source_id}:gold_kind",
        help="这是机器 Silver 的候选类型，标注者必须根据自己的数学判断核对。",
    )

    gold_expression = _draft_value(source_id, "gold_expression", stored_draft) or ""
    set_kind = _draft_value(source_id, "set_kind", stored_draft) or "interval"
    set_primary = _draft_value(source_id, "set_primary", stored_draft) or ""
    set_secondary = _draft_value(source_id, "set_secondary", stored_draft) or ""
    period = _draft_value(source_id, "period", stored_draft) or ""
    periodic_variable = _draft_value(source_id, "periodic_variable", stored_draft) or variable
    points = _draft_value(source_id, "points", stored_draft) or ""
    intervals = _draft_value(source_id, "intervals", stored_draft) or ""
    excluded_points = _draft_value(source_id, "excluded_points", stored_draft) or ""
    full_period = bool(_draft_value(source_id, "full_period", stored_draft))

    if gold_kind == "expression":
        gold_expression = st.text_input(
            "Gold 表达式 LaTeX",
            value=gold_expression,
            key=f"{source_id}:gold_expression",
            help="页面把人工确认后的内容转换为 ExprAST。",
        )
    elif gold_kind == "set":
        set_kinds = ["empty", "reals", "finite", "interval", "union", "difference"]
        set_kind = st.selectbox(
            "集合类型",
            set_kinds,
            index=_value(set_kinds, set_kind),
            key=f"{source_id}:set_kind",
        )
        if set_kind == "finite":
            set_primary = st.text_area(
                "元素（每行一个 LaTeX 表达式）",
                value=set_primary,
                key=f"{source_id}:set_primary",
            )
        elif set_kind == "interval":
            set_primary = st.text_input(
                "区间",
                value=set_primary,
                key=f"{source_id}:set_primary",
                placeholder=r"例如 [0,2] 或 (-\infty,-1]",
            )
        elif set_kind == "union":
            set_primary = st.text_area(
                "并集分量（每行一个区间、有限集、R 或 empty）",
                value=set_primary,
                key=f"{source_id}:set_primary",
                placeholder="(-oo,-1]\n[1,oo)",
            )
        elif set_kind == "difference":
            set_primary = st.text_input(
                "基础集合",
                value=set_primary,
                key=f"{source_id}:set_primary",
                placeholder="例如 R",
            )
            set_secondary = st.text_input(
                "移除集合",
                value=set_secondary,
                key=f"{source_id}:set_secondary",
                placeholder=r"例如 {\frac{\pi}{2}}",
            )
    else:
        periodic_left, periodic_right = st.columns(2)
        with periodic_left:
            period = st.text_input(
                "最小正周期",
                value=period,
                key=f"{source_id}:period",
                placeholder=r"例如 \pi 或 2\pi",
            )
            periodic_variable = st.text_input(
                "周期变量",
                value=periodic_variable,
                key=f"{source_id}:periodic_variable",
            )
            full_period = st.checkbox(
                "基本周期内全部包含（通常配合排除点）",
                value=full_period,
                key=f"{source_id}:full_period",
            )
            points = st.text_area(
                "基本点（每行一个，必须位于 [0,T)）",
                value=points,
                key=f"{source_id}:points",
                placeholder=r"例如 \frac{\pi}{3}",
                disabled=full_period,
            )
        with periodic_right:
            intervals = st.text_area(
                "基本区间（每行一个，跨周期端点时拆开）",
                value=intervals,
                key=f"{source_id}:intervals",
                placeholder=r"[0,\frac{\pi}{6})\n(\frac{11\pi}{6},2\pi)",
                disabled=full_period,
            )
            excluded_points = st.text_area(
                "排除点（每行一个，必须位于 [0,T)）",
                value=excluded_points,
                key=f"{source_id}:excluded_points",
            )

    st.subheader("3. 选择题与审查说明")
    if record["output_format"] == "multiple_choice":
        option_values = ["", "A", "B", "C", "D"]
        option_current = _draft_value(source_id, "gold_option", stored_draft) or ""
        selected_option = st.selectbox(
            "Gold 选项（机器 Silver 已预填，必须在核对数学 Gold 后确认）",
            option_values,
            format_func=lambda item: "未选择" if item == "" else item,
            index=_value(option_values, option_current),
            key=f"{source_id}:gold_option",
        )
    else:
        selected_option = ""
        st.text_input("Gold 选项", "开放题必须为 null", disabled=True)
    notes = st.text_area(
        "简短人工依据、修改理由或歧义说明",
        value=_draft_value(source_id, "notes", stored_draft) or "",
        key=f"{source_id}:notes",
        help="建议记录关键变换、端点和修改 Silver 的原因；不要粘贴来源解析或求解器输出。",
    )

    current_draft = {
        "target_latex": target_latex,
        "variable": variable,
        "unit": unit,
        "quadrant": quadrant,
        "operator": operator,
        "property_names": property_names,
        "completeness": completeness,
        "constraints": constraints,
        "gold_kind": gold_kind,
        "gold_expression": gold_expression,
        "set_kind": set_kind,
        "set_primary": set_primary,
        "set_secondary": set_secondary,
        "period": period,
        "periodic_variable": periodic_variable,
        "points": points,
        "intervals": intervals,
        "excluded_points": excluded_points,
        "full_period": full_period,
        "gold_option": selected_option,
        "notes": notes,
    }
    try:
        session.save_draft(source_id, current_draft)
    except AnnotationError as exc:
        st.error(f"自动保存草稿失败：{exc}")
        st.stop()

    validated = None
    try:
        validated = validate_draft(record, current_draft)
    except AnnotationError as exc:
        st.error(f"结构校验：{exc}")
    else:
        st.success("结构校验通过。注意：这不代表机器 Silver 或人工修改后的数学答案正确。")
        with st.expander("自动生成的结构化预览"):
            st.json(
                {
                    "oracle_urm": validated.oracle_urm.model_dump(mode="json"),
                    "gold_answer": validated.gold_answer.model_dump(mode="json"),
                    "gold_option": validated.gold_option,
                }
            )

    save_left, save_right = st.columns([1, 3])
    if save_left.button("确认并保存人工审查", type="primary", disabled=validated is None, use_container_width=True):
        assert validated is not None
        try:
            session.complete(source_id, validated, notes)
        except AnnotationError as exc:
            st.error(f"保存失败：{exc}")
        else:
            st.success("已保存到当前标注者的隔离目录。")
            st.rerun()
    save_right.caption(
        f"草稿自动保存在 `{session.paths.drafts}`；有效记录保存在 `{session.paths.annotations}`。"
    )
