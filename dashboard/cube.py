"""Interactive OLAP cube console for the BRFSS data warehouse.

Every operation in this console is executed as real SQL against the Review 1
SQLite star schema (``review1/diabetes_dw.db``), so the dashboard, the stored
Review 1 artifacts and the scripts in ``review1/sql`` all describe the same
warehouse instead of parallel, hand-made summaries.
"""

from __future__ import annotations

import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
WAREHOUSE_DB = ROOT / "review1" / "diabetes_dw.db"

NAVY, TEAL, ORANGE, SKY, MUTED = "#0B1220", "#2DD4BF", "#FB923C", "#60A5FA", "#94A3B8"
PLOT_BG, PAPER_BG, TEXT, GRID = "#111C2E", "#111C2E", "#E6EDF7", "#334155"
CUBE_COLORSCALE = [[0.0, "#0F3B4A"], [0.45, TEAL], [0.72, "#FBBF24"], [1.0, "#FB7185"]]

AGES = {1: "18–24", 2: "25–29", 3: "30–34", 4: "35–39", 5: "40–44", 6: "45–49",
        7: "50–54", 8: "55–59", 9: "60–64", 10: "65–69", 11: "70–74", 12: "75–79", 13: "80+"}
HEALTH = {1: "Excellent", 2: "Very good", 3: "Good", 4: "Fair", 5: "Poor"}
INCOME = {1: "<$10k", 2: "$10–15k", 3: "$15–20k", 4: "$20–25k", 5: "$25–35k",
          6: "$35–50k", 7: "$50–75k", 8: ">$75k"}
EDUCATION = {1: "No school", 2: "Elementary", 3: "Some high school", 4: "High school",
             5: "Some college", 6: "College graduate"}
AGE_GROUP_EXPR = ("CASE WHEN d.age <= 2 THEN '18–29' WHEN d.age <= 5 THEN '30–44' "
                  "WHEN d.age <= 8 THEN '45–59' WHEN d.age <= 11 THEN '60–74' ELSE '75+' END")
AGE_GROUPS = ("18–29", "30–44", "45–59", "60–74", "75+")
YES_NO = {0: "No", 1: "Yes"}


@dataclass(frozen=True)
class Level:
    """One level of a dimension inside the concept hierarchy."""

    expr: str
    members: tuple[Any, ...]
    labels: dict[Any, str]
    title: str

    def label(self, value: Any) -> str:
        return str(self.labels.get(value, value))


@dataclass(frozen=True)
class Dimension:
    key: str
    label: str
    levels: tuple[Level, ...]


def _binary(expr: str, title: str) -> Level:
    return Level(expr, (0, 1), dict(YES_NO), title)


DIMENSIONS: dict[str, Dimension] = {
    "age": Dimension("age", "Age band", (
        Level("d.age", tuple(AGES), dict(AGES), "Age band"),
        Level(AGE_GROUP_EXPR, AGE_GROUPS, {g: g for g in AGE_GROUPS}, "Age group"),
    )),
    "sex": Dimension("sex", "Sex", (
        Level("d.sex", (0, 1), {0: "Female", 1: "Male"}, "Sex"),
    )),
    "income": Dimension("income", "Income band", (
        Level("d.income", tuple(INCOME), dict(INCOME), "Income band"),
    )),
    "education": Dimension("education", "Education", (
        Level("d.education", tuple(EDUCATION), dict(EDUCATION), "Education"),
    )),
    "genhlth": Dimension("genhlth", "General health", (
        Level("g.gen_hlth_rating", tuple(HEALTH), dict(HEALTH), "General health"),
    )),
    "highbp": Dimension("highbp", "High blood pressure", (
        _binary("c.high_bp", "High blood pressure"),
    )),
    "highchol": Dimension("highchol", "High cholesterol", (
        _binary("c.high_chol", "High cholesterol"),
    )),
    "cholcheck": Dimension("cholcheck", "Cholesterol checked", (
        _binary("c.chol_check", "Cholesterol checked"),
    )),
    "stroke": Dimension("stroke", "Stroke", (
        _binary("c.stroke", "Stroke"),
    )),
    "heart": Dimension("heart", "Heart disease / attack", (
        _binary("c.heart_disease_or_attack", "Heart disease / attack"),
    )),
    "diffwalk": Dimension("diffwalk", "Difficulty walking", (
        _binary("c.diff_walk", "Difficulty walking"),
    )),
    "smoker": Dimension("smoker", "Smoker", (
        _binary("l.smoker", "Smoker"),
    )),
    "physact": Dimension("physact", "Physically active", (
        _binary("l.phys_activity", "Physically active"),
    )),
    "fruits": Dimension("fruits", "Eats fruit", (
        _binary("l.fruits", "Eats fruit"),
    )),
    "veggies": Dimension("veggies", "Eats vegetables", (
        _binary("l.veggies", "Eats vegetables"),
    )),
    "alcohol": Dimension("alcohol", "Heavy alcohol use", (
        _binary("l.hvy_alcohol_consump", "Heavy alcohol use"),
    )),
    "healthcare": Dimension("healthcare", "Any healthcare access", (
        _binary("c.any_healthcare", "Any healthcare access"),
    )),
    "nocost": Dimension("nocost", "No doctor due to cost", (
        _binary("c.no_doc_bc_cost", "No doctor due to cost"),
    )),
}

MEASURES: dict[str, tuple[str, str]] = {
    "Respondents": ("COUNT(*)", "respondents"),
    "Diabetes cases": ("SUM(f.diabetes_binary)", "diabetes_cases"),
    "Diabetes prevalence (%)": ("ROUND(AVG(f.diabetes_binary) * 100, 2)", "prevalence_pct"),
    "Average BMI": ("ROUND(AVG(f.bmi_value), 2)", "avg_bmi"),
    "Average mental-health days": ("ROUND(AVG(f.ment_hlth_days), 2)", "avg_ment_hlth"),
    "Average physical-health days": ("ROUND(AVG(f.phys_hlth_days), 2)", "avg_phys_hlth"),
}
DEFAULT_MEASURE = "Diabetes prevalence (%)"
COUNT_ALIAS = "respondents"

AXIS_OPTIONS: list[str] = ["ALL"] + [
    f"{dim.key}:{level}"
    for dim in DIMENSIONS.values()
    for level in range(len(dim.levels))
]


# --------------------------------------------------------------------------- #
# Axis helpers
# --------------------------------------------------------------------------- #

def axis_option(dim_key: str | None, level: int = 0) -> str:
    return "ALL" if dim_key is None else f"{dim_key}:{level}"


def parse_axis_option(value: str) -> tuple[str | None, int]:
    if not value or value == "ALL":
        return None, 0
    dim_key, _, level = value.partition(":")
    return dim_key, int(level or 0)


def axis_option_label(value: str) -> str:
    dim_key, level = parse_axis_option(value)
    if dim_key is None:
        return "ALL (collapsed)"
    return DIMENSIONS[dim_key].levels[level].title


def level_for(dim_key: str, level: int) -> Level:
    return DIMENSIONS[dim_key].levels[level]


# --------------------------------------------------------------------------- #
# SQL layer
# --------------------------------------------------------------------------- #

def sql_literal(value: Any) -> str:
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (int, np.integer)):
        return str(int(value))
    if isinstance(value, (float, np.floating)):
        return repr(float(value))
    return "'" + str(value).replace("'", "''") + "'"


def build_sql(axes: Sequence[tuple[str | None, int]],
              filters: Sequence[dict],
              measures: Sequence[str] = tuple(MEASURES)) -> str:
    """Render the cube query: three axis expressions, filters and measures."""
    select_items: list[str] = []
    group_items: list[str] = []
    for index, (dim_key, level) in enumerate(axes):
        if dim_key is None:
            select_items.append(f"'ALL' AS axis_{index}")
            continue
        expr = level_for(dim_key, level).expr
        select_items.append(f"{expr} AS axis_{index}")
        group_items.append(expr)
    for name in measures:
        select_items.append(f"{MEASURES[name][0]} AS {MEASURES[name][1]}")

    where: list[str] = []
    for item in filters:
        expr = level_for(item["dim"], item.get("level", 0)).expr
        where.append(f"{expr} = {sql_literal(item['value'])}")

    sql = "SELECT\n    " + ",\n    ".join(select_items)
    sql += "\nFROM FACT_HEALTH_SURVEY f"
    sql += "\nJOIN DIM_DEMOGRAPHICS d ON d.demog_key = f.demog_key"
    sql += "\nJOIN DIM_LIFESTYLE l ON l.lifestyle_key = f.lifestyle_key"
    sql += "\nJOIN DIM_CLINICAL_RISK c ON c.clinical_key = f.clinical_key"
    sql += "\nJOIN DIM_GENERAL_HEALTH g ON g.genhealth_key = f.genhealth_key"
    if where:
        sql += "\nWHERE " + "\n  AND ".join(where)
    if group_items:
        sql += "\nGROUP BY " + ", ".join(group_items)
    sql += "\nORDER BY axis_0, axis_1, axis_2"
    return sql


def execute_sql(sql: str) -> tuple[pd.DataFrame, float]:
    """Run the query read-only against the warehouse and time it."""
    start = time.perf_counter()
    connection = sqlite3.connect(f"file:{WAREHOUSE_DB}?mode=ro", uri=True)
    try:
        frame = pd.read_sql_query(sql, connection)
    finally:
        connection.close()
    return frame, (time.perf_counter() - start) * 1000.0


# --------------------------------------------------------------------------- #
# Cube rendering
# --------------------------------------------------------------------------- #

def format_measure(name: str, value: Any) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if name in ("Respondents", "Diabetes cases"):
        return f"{number:,.0f}"
    if "%" in name:
        return f"{number:,.2f}"
    return f"{number:,.1f}"


def build_cube_figure(frame: pd.DataFrame,
                      dims: Sequence[str | None],
                      measure: str,
                      titles: Sequence[str] | None = None,
                      member_orders: Sequence[Sequence[Any]] | None = None,
                      label_maps: Sequence[dict] | None = None,
                      count_column: str | None = None,
                      colorbar_title: str | None = None,
                      camera: dict | None = None,
                      height: int = 620) -> go.Figure:
    """Build a Mesh3d cube; one cuboid per OLAP cell, coloured by the measure."""
    dims = list(dims) + [None] * (3 - len(dims))
    titles = list(titles) if titles else ["X axis", "Y axis", "Z axis"]
    titles += [""] * (3 - len(titles))
    member_orders = list(member_orders) if member_orders else []
    member_orders += [[]] * (3 - len(member_orders))
    label_maps = list(label_maps) if label_maps else []
    label_maps += [{}] * (3 - len(label_maps))

    axis_members: list[list[Any]] = []
    axis_labels: list[dict] = []
    for index in range(3):
        column = dims[index]
        if column is None or column not in frame.columns:
            axis_members.append(["ALL"])
            axis_labels.append({"ALL": "ALL"})
            continue
        members = list(member_orders[index]) if member_orders[index] else sorted(
            frame[column].dropna().unique().tolist(), key=lambda v: str(v))
        axis_members.append(members)
        axis_labels.append(label_maps[index] or {})

    positions = [{value: i for i, value in enumerate(members)} for members in axis_members]
    vertices_x: list[float] = []
    vertices_y: list[float] = []
    vertices_z: list[float] = []
    intensities: list[float] = []
    hover_text: list[str] = []
    faces_i: list[int] = []
    faces_j: list[int] = []
    faces_k: list[int] = []
    face_template = [(0, 1, 2), (0, 2, 3), (4, 5, 6), (4, 6, 7),
                      (0, 1, 5), (0, 5, 4), (1, 2, 6), (1, 6, 5),
                      (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)]
    half_width = 0.42

    for _, row in frame.iterrows():
        centre = [positions[index].get(row[dims[index]] if dims[index] else "ALL", 0)
                  for index in range(3)]
        x0, y0, z0 = [value - half_width for value in centre]
        x1, y1, z1 = [value + half_width for value in centre]
        cube_vertices = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                         (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        start = len(vertices_x)
        for x, y, z in cube_vertices:
            vertices_x.append(x)
            vertices_y.append(y)
            vertices_z.append(z)
        value = float(row[measure])
        intensities.extend([value] * 8)

        cell_lines = []
        for index in range(3):
            if not titles[index]:
                continue
            column = dims[index]
            raw = row[column] if column else "ALL"
            cell_lines.append(f"<b>{titles[index]}</b>: {axis_labels[index].get(raw, raw)}")
        cell_lines.append(f"<b>{measure}</b>: {format_measure(measure, value)}")
        if count_column and count_column in frame.columns:
            cell_lines.append(f"Respondents: {float(row[count_column]):,.0f}")
        hover_text.extend(["<br>".join(cell_lines)] * 8)
        for i, j, k in face_template:
            faces_i.append(start + i)
            faces_j.append(start + j)
            faces_k.append(start + k)

    values = frame[measure].to_numpy(dtype=float) if measure in frame.columns else np.array([0.0])
    if values.size == 0:
        values = np.array([0.0])
    cmin, cmax = float(values.min()), float(values.max())
    if np.isclose(cmin, cmax):
        cmin -= 0.5
        cmax += 0.5

    figure = go.Figure(go.Mesh3d(
        x=vertices_x, y=vertices_y, z=vertices_z, i=faces_i, j=faces_j, k=faces_k,
        intensity=intensities, intensitymode="vertex", colorscale=CUBE_COLORSCALE,
        cmin=cmin, cmax=cmax, flatshading=True, hovertext=hover_text,
        hovertemplate="%{hovertext}<extra></extra>",
        colorbar=dict(title=dict(text=colorbar_title or measure, font=dict(color=TEXT)),
                      thickness=16, len=.6, tickfont=dict(color=TEXT)),
        showscale=True,
    ))
    for index, axis_name in enumerate(("xaxis", "yaxis", "zaxis")):
        members = axis_members[index]
        figure.update_scenes(**{axis_name: dict(
            title=titles[index], tickmode="array", tickvals=list(range(len(members))),
            ticktext=[str(axis_labels[index].get(member, member)) for member in members],
            tickfont=dict(color=TEXT, size=10), showbackground=True, backgroundcolor=PLOT_BG,
            gridcolor=GRID, linecolor="#475569", color=TEXT, zeroline=False,
        )})
    eye = camera or dict(x=1.55, y=-1.65, z=1.3)
    figure.update_layout(
        scene=dict(aspectmode="cube", camera=dict(eye=eye)),
        margin=dict(l=0, r=0, t=28, b=0), height=height,
        paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG, font=dict(color=TEXT),
    )
    return figure


# --------------------------------------------------------------------------- #
# Console state
# --------------------------------------------------------------------------- #

AXIS_NAMES = ("X", "Y", "Z")
OPERATION_HELP = {
    "Explore": "Three dimensions, every member, no filter. Drag to orbit and hover a cell to read it.",
    "Roll-up": "Climb the concept hierarchy (age band → age group) or collapse an axis to ALL. Cells merge into coarser aggregates.",
    "Drill-down": "Split an axis one level finer (age group → age band) or drill a collapsed axis into a new dimension.",
    "Slice": "Fix one dimension to a single member; the cube keeps that slice and reports the remaining cells.",
    "Dice": "Fix several dimensions at once to build a high-risk sub-cube.",
    "Pivot": "Re-orient the cube: pick which axis becomes rows and which becomes columns.",
}
PRESETS = [
    ("Roll-up · Age band → Age group", "rollup"),
    ("Drill-down · ALL → Income band", "drilldown"),
    ("Slice · High blood pressure = Yes", "slice"),
    ("Dice · 60–74 × High BP × Smoker", "dice"),
    ("Pivot · Education × Sex", "pivot"),
]


def _axis_key(axis_name: str) -> str:
    return f"cube_axis_{axis_name.lower()}"


def _focus_key(axis_name: str, dim_key: str, level: int) -> str:
    return f"cube_focus_{axis_name.lower()}_{dim_key}_{level}"


def _member_key(purpose: str, dim_key: str) -> str:
    return f"cube_member_{purpose}_{dim_key}"


def _init_state() -> None:
    defaults = {
        "cube_op": "Explore",
        "cube_axis_x": axis_option("age", 0),
        "cube_axis_y": axis_option("sex", 0),
        "cube_axis_z": axis_option("genhlth", 0),
        "cube_apply_axis": "X",
        "cube_measure": DEFAULT_MEASURE,
        "cube_filters": [],
        "cube_pivot_rows": "X",
        "cube_pivot_cols": "Y",
        "cube_drill_dim": axis_option("income", 0),
        "cube_dim_slice": axis_option("highbp", 0),
        "cube_dim_dice1": axis_option("age", 1),
        "cube_dim_dice2": axis_option("highbp", 0),
        "cube_dim_dice3": axis_option("smoker", 0),
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)
    for axis_name in AXIS_NAMES:
        key = _axis_key(axis_name)
        if st.session_state.get(key) not in AXIS_OPTIONS:
            st.session_state[key] = defaults[key]


def _filters() -> list[dict]:
    return list(st.session_state.get("cube_filters", []))


def _op_explore() -> None:
    st.session_state["cube_op"] = "Explore"
    st.session_state["cube_filters"] = []


def _op_rollup() -> None:
    st.session_state["cube_op"] = "Roll-up"
    axis_name = st.session_state.get("cube_apply_axis", "X")
    key = _axis_key(axis_name)
    dim_key, level = parse_axis_option(st.session_state.get(key, "ALL"))
    if dim_key is None:
        return
    if level + 1 < len(DIMENSIONS[dim_key].levels):
        st.session_state[key] = axis_option(dim_key, level + 1)
    else:
        st.session_state[key] = "ALL"


def _op_drill_down() -> None:
    st.session_state["cube_op"] = "Drill-down"
    axis_name = st.session_state.get("cube_apply_axis", "X")
    key = _axis_key(axis_name)
    dim_key, level = parse_axis_option(st.session_state.get(key, "ALL"))
    if dim_key is None:
        dim_key, level = parse_axis_option(st.session_state.get("cube_drill_dim", axis_option("income", 0)))
    else:
        level = max(level - 1, 0)
    st.session_state[key] = axis_option(dim_key, level)


def _op_slice() -> None:
    st.session_state["cube_op"] = "Slice"
    dim_key, level = parse_axis_option(st.session_state.get("cube_dim_slice", axis_option("highbp", 0)))
    level_spec = level_for(dim_key, level)
    value = st.session_state.get(_member_key("slice", dim_key), level_spec.members[0])
    filters = [item for item in _filters() if item.get("source") != "slice" or item["dim"] != dim_key]
    filters.append({"dim": dim_key, "level": level, "value": value, "source": "slice"})
    st.session_state["cube_filters"] = filters


def _op_dice() -> None:
    st.session_state["cube_op"] = "Dice"
    filters = [item for item in _filters() if item.get("source") != "dice"]
    for slot in (1, 2, 3):
        dim_key, level = parse_axis_option(st.session_state.get(f"cube_dim_dice{slot}", "ALL"))
        if dim_key is None:
            continue
        level_spec = level_for(dim_key, level)
        value = st.session_state.get(_member_key(f"dice{slot}", dim_key), level_spec.members[0])
        filters.append({"dim": dim_key, "level": level, "value": value, "source": "dice"})
    st.session_state["cube_filters"] = filters


def _op_pivot() -> None:
    st.session_state["cube_op"] = "Pivot"
    rows_axis = st.session_state.get("cube_pivot_rows", "X")
    cols_axis = st.session_state.get("cube_pivot_cols", "Y")
    if rows_axis == cols_axis:
        return
    depth_axis = next(name for name in AXIS_NAMES if name not in (rows_axis, cols_axis))
    axes = {name: st.session_state.get(_axis_key(name), "ALL") for name in AXIS_NAMES}
    st.session_state[_axis_key("X")] = axes[rows_axis]
    st.session_state[_axis_key("Y")] = axes[cols_axis]
    st.session_state[_axis_key("Z")] = axes[depth_axis]


OPERATION_CALLBACKS = {
    "Explore": _op_explore,
    "Roll-up": _op_rollup,
    "Drill-down": _op_drill_down,
    "Slice": _op_slice,
    "Dice": _op_dice,
    "Pivot": _op_pivot,
}


def apply_preset(preset: str) -> None:
    """Load a canned operation into the console state."""
    if preset == "rollup":
        st.session_state.update({
            "cube_op": "Roll-up",
            "cube_apply_axis": "X",
            "cube_axis_x": axis_option("age", 1),
            "cube_axis_y": axis_option("sex", 0),
            "cube_axis_z": axis_option("genhlth", 0),
            "cube_filters": [],
        })
    elif preset == "drilldown":
        st.session_state.update({
            "cube_op": "Drill-down",
            "cube_apply_axis": "X",
            "cube_axis_x": axis_option("income", 0),
            "cube_axis_y": axis_option("sex", 0),
            "cube_axis_z": axis_option("genhlth", 0),
            "cube_filters": [],
        })
    elif preset == "slice":
        st.session_state.update({
            "cube_op": "Slice",
            "cube_apply_axis": "X",
            "cube_axis_x": axis_option("age", 1),
            "cube_axis_y": axis_option("sex", 0),
            "cube_axis_z": axis_option("income", 0),
            "cube_filters": [{"dim": "highbp", "level": 0, "value": 1, "source": "slice"}],
            "cube_dim_slice": axis_option("highbp", 0),
        })
        st.session_state[_member_key("slice", "highbp")] = 1
    elif preset == "dice":
        st.session_state.update({
            "cube_op": "Dice",
            "cube_apply_axis": "X",
            "cube_axis_x": axis_option("age", 0),
            "cube_axis_y": axis_option("sex", 0),
            "cube_axis_z": axis_option("genhlth", 0),
            "cube_filters": [
                {"dim": "age", "level": 1, "value": "60–74", "source": "dice"},
                {"dim": "highbp", "level": 0, "value": 1, "source": "dice"},
                {"dim": "smoker", "level": 0, "value": 1, "source": "dice"},
            ],
            "cube_dim_dice1": axis_option("age", 1),
            "cube_dim_dice2": axis_option("highbp", 0),
            "cube_dim_dice3": axis_option("smoker", 0),
        })
        st.session_state[_member_key("dice1", "age")] = "60–74"
        st.session_state[_member_key("dice2", "highbp")] = 1
        st.session_state[_member_key("dice3", "smoker")] = 1
    elif preset == "pivot":
        st.session_state.update({
            "cube_op": "Pivot",
            "cube_apply_axis": "X",
            "cube_axis_x": axis_option("education", 0),
            "cube_axis_y": axis_option("sex", 0),
            "cube_axis_z": axis_option("age", 0),
            "cube_pivot_rows": "X",
            "cube_pivot_cols": "Y",
            "cube_filters": [],
        })


# --------------------------------------------------------------------------- #
# Console rendering
# --------------------------------------------------------------------------- #

CONSOLE_CSS = """
<style>
.cube-badges { display:flex; gap:8px; flex-wrap:wrap; margin:2px 0 6px; }
.cube-pill { background:#12243A; border:1px solid #2C3E5C; color:#AFC0D5; border-radius:999px;
             padding:3px 12px; font-size:12px; font-weight:700; letter-spacing:.04em;
             font-family:ui-monospace,SFMono-Regular,Menlo,monospace; }
.cube-pill.accent { color:#5EEAD4; border-color:#1E6F66; }
.cube-panel-title { font-size:11px; font-weight:800; letter-spacing:.18em; color:#7C8DA6;
                    text-transform:uppercase; margin-bottom:6px; }
</style>
"""


def _member_picker(st, purpose: str, label: str) -> None:
    """Render a dimension picker plus the member picker for that dimension."""
    st.selectbox(label, AXIS_OPTIONS, format_func=axis_option_label, key=f"cube_dim_{purpose}")
    dim_key, level = parse_axis_option(st.session_state[f"cube_dim_{purpose}"])
    if dim_key is None:
        return
    level_spec = level_for(dim_key, level)
    st.selectbox("Member", list(level_spec.members),
                 format_func=level_spec.label, key=_member_key(purpose, dim_key))


def _focus_picker(st, axis_name: str, dim_key: str | None, level: int) -> None:
    if dim_key is None:
        return
    level_spec = level_for(dim_key, level)
    key = _focus_key(axis_name, dim_key, level)
    st.selectbox(f"Focus {axis_name}", ["ALL"] + list(level_spec.members),
                 format_func=lambda value: "All members" if value == "ALL" else level_spec.label(value),
                 key=key)


def render_cube_console(st) -> None:
    """Render the full cube console (controls, cube, result set, SQL)."""
    _init_state()
    if not WAREHOUSE_DB.exists():
        st.error(f"Warehouse database not found at {WAREHOUSE_DB}. "
                 "Rebuild it with review1/scripts/03_build_warehouse.py.")
        return
    st.markdown(CONSOLE_CSS, unsafe_allow_html=True)
    st.markdown("#### The cube, iteratively")
    st.markdown(
        '<div class="insight">Every operation below runs as <b>real SQL</b> against '
        '<code>review1/diabetes_dw.db</code> — the Review 1 star schema, one fact row per '
        'respondent. Drag to orbit, hover a cell to read it, then roll up, drill down, slice, '
        'dice or pivot with the panel.</div>', unsafe_allow_html=True)

    chip_columns = st.columns(len(PRESETS))
    for column, (label, preset) in zip(chip_columns, PRESETS):
        if column.button(label, key=f"cube_chip_{preset}", width="stretch"):
            apply_preset(preset)
            st.rerun()

    control_column, cube_column = st.columns([1, 2.5])

    with control_column:
        st.markdown('<div class="cube-panel-title">Cube controls</div>', unsafe_allow_html=True)
        button_rows = [st.columns(3), st.columns(3)]
        buttons = [("⬡ Explore", "Explore"), ("↑ Roll-up", "Roll-up"), ("↓ Drill-down", "Drill-down"),
                   ("✂ Slice", "Slice"), ("⚄ Dice", "Dice"), ("⇄ Pivot", "Pivot")]
        for index, (label, operation) in enumerate(buttons):
            active = st.session_state["cube_op"] == operation
            button_rows[index // 3][index % 3].button(
                label, key=f"cube_op_{operation}", width="stretch",
                type="primary" if active else "secondary",
                on_click=OPERATION_CALLBACKS[operation])
        st.caption(OPERATION_HELP[st.session_state["cube_op"]])

        st.selectbox("Apply to axis", list(AXIS_NAMES), key="cube_apply_axis")

        axes_state: list[tuple[str | None, int]] = []
        for axis_name in AXIS_NAMES:
            value = st.selectbox(f"{axis_name} axis", AXIS_OPTIONS,
                                 format_func=axis_option_label, key=_axis_key(axis_name))
            dim_key, level = parse_axis_option(value)
            axes_state.append((dim_key, level))

        with st.expander("Focus one member (drill into a cell)"):
            for axis_name, (dim_key, level) in zip(AXIS_NAMES, axes_state):
                _focus_picker(st, axis_name, dim_key, level)

        st.selectbox("Measure (cell colour)", list(MEASURES), key="cube_measure")

        operation = st.session_state["cube_op"]
        if operation == "Drill-down":
            st.selectbox("Drill into dimension", AXIS_OPTIONS,
                         format_func=axis_option_label, key="cube_drill_dim")
        elif operation == "Slice":
            _member_picker(st, "slice", "Slice dimension")
        elif operation == "Dice":
            for slot in (1, 2, 3):
                st.markdown(f"**Dice constraint {slot}**")
                _member_picker(st, f"dice{slot}", "Dimension")
        elif operation == "Pivot":
            st.selectbox("Rows axis", list(AXIS_NAMES), key="cube_pivot_rows")
            st.selectbox("Columns axis", list(AXIS_NAMES), key="cube_pivot_cols")

    # ----------------------------------------------------------------------- #
    # Build the query: axis dimensions, operation filters and member focuses.
    # ----------------------------------------------------------------------- #
    filters = _filters()
    for axis_name, (dim_key, level) in zip(AXIS_NAMES, axes_state):
        if dim_key is None:
            continue
        focus = st.session_state.get(_focus_key(axis_name, dim_key, level), "ALL")
        if focus != "ALL":
            filters.append({"dim": dim_key, "level": level, "value": focus, "source": "focus"})

    sql = build_sql(axes_state, filters)
    try:
        result, elapsed_ms = execute_sql(sql)
    except sqlite3.Error as error:
        st.error(f"The warehouse query failed: {error}")
        return

    measure = st.session_state["cube_measure"]
    titles = [axis_option_label(st.session_state[_axis_key(name)]) for name in AXIS_NAMES]
    member_orders: list[list[Any]] = []
    label_maps: list[dict] = []
    for dim_key, level in axes_state:
        if dim_key is None:
            member_orders.append(["ALL"])
            label_maps.append({})
            continue
        level_spec = level_for(dim_key, level)
        member_orders.append(list(level_spec.members))
        label_maps.append(dict(level_spec.labels))

    camera = dict(x=1.55, y=-1.65, z=1.3)
    if operation == "Pivot":
        camera = dict(x=-1.55, y=1.65, z=1.3)

    with cube_column:
        total = float(result[COUNT_ALIAS].sum()) if COUNT_ALIAS in result.columns else 0.0
        measure_alias = MEASURES[measure][1]
        measure_values = (result[measure_alias].to_numpy(dtype=float)
                          if measure_alias in result.columns else [])
        spread = ""
        if len(measure_values):
            spread = (f'<span class="cube-pill">{measure} '
                      f'{measure_values.min():,.1f} → {measure_values.max():,.1f}</span>')
        st.markdown(
            f'<div class="cube-badges">'
            f'<span class="cube-pill accent">{len(result):,} cells</span>'
            f'<span class="cube-pill">{total:,.0f} respondents</span>'
            f'<span class="cube-pill">{elapsed_ms:.1f} ms</span>'
            f'{spread}'
            f'</div>', unsafe_allow_html=True)
        if result.empty:
            st.warning("This operation selects no respondents, so the cube is empty. "
                       "Loosen a slice, dice or focus filter to bring cells back.")
            st.code(sql, language="sql")
        else:
            figure = build_cube_figure(
                result, ["axis_0", "axis_1", "axis_2"], MEASURES[measure][1],
                titles=titles, member_orders=member_orders, label_maps=label_maps,
                count_column=COUNT_ALIAS, colorbar_title=measure, camera=camera)
            figure.update_layout(title=f"{measure} across "
                                      f"{' × '.join('ALL' if t == 'ALL (collapsed)' else t for t in titles)}")
            st.plotly_chart(figure, width="stretch", config={"displaylogo": False})
            st.caption("Balanced warehouse sample (70,692 respondents, 50/50 target design). "
                       "Cell colour encodes the selected measure; hover a cuboid for its values.")

    result_column, sql_column = st.columns([1.25, 1])
    with result_column:
        st.markdown('<div class="cube-panel-title">Result set</div>', unsafe_allow_html=True)
        if result.empty:
            st.warning("No cells match this operation.")
        else:
            unique_titles: list[str] = []
            for title in titles:
                candidate, suffix = title, 2
                while candidate in unique_titles:
                    candidate = f"{title} ({suffix})"
                    suffix += 1
                unique_titles.append(candidate)
            display = result.rename(columns={alias: name for name, (_, alias) in MEASURES.items()})
            display = display.rename(columns={
                "axis_0": unique_titles[0], "axis_1": unique_titles[1], "axis_2": unique_titles[2]})
            for index, (dim_key, level) in enumerate(axes_state):
                if dim_key is None:
                    continue
                level_spec = level_for(dim_key, level)
                display[unique_titles[index]] = display[unique_titles[index]].map(
                    lambda value: level_spec.label(value))
            if operation == "Pivot" and len(titles) >= 2:
                pivot = result.pivot_table(index="axis_0", columns="axis_1",
                                           values=MEASURES[measure][1], aggfunc="mean")
                pivot.index = [level_for(axes_state[0][0], axes_state[0][1]).label(value)
                               for value in pivot.index] if axes_state[0][0] else pivot.index
                if axes_state[1][0]:
                    pivot.columns = [level_for(axes_state[1][0], axes_state[1][1]).label(value)
                                     for value in pivot.columns]
                st.dataframe(pivot.round(2).reset_index(), width="stretch", hide_index=True)
            else:
                st.dataframe(display.round(2), width="stretch", hide_index=True)
            st.download_button("Download result set (CSV)",
                               display.round(4).to_csv(index=False).encode(),
                               "cube_result_set.csv", "text/csv", key="cube_dl_result")

    with sql_column:
        st.markdown('<div class="cube-panel-title">Generated SQL</div>', unsafe_allow_html=True)
        st.code(sql, language="sql")
        st.caption("Read-only execution against review1/diabetes_dw.db.")
