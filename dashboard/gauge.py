"""Risk gauge for the profile page: a 270° dial with risk bands, ticks and needle.

The dial is drawn with polar traces so every element (band colours, tick marks,
needle, hub ring, value) stays under direct control and matches the dashboard
palette.
"""

from __future__ import annotations

import math

import plotly.graph_objects as go

TEXT = "#E6EDF7"
MUTED = "#94A3B8"
TRACK = "#3A4E6F"
NEEDLE = "#EAF2FF"
HUB_RING = "#38BDF8"

# (label, upper bound in %, band colour, suggested follow-up)
RISK_BANDS = (
    ("Low risk", 15, "#11625A", "Routine screening · no extra action"),
    ("Moderate risk", 30, "#38A9E8", "Lifestyle counselling and standard screening"),
    ("High risk", 50, "#8A5320", "Targeted screening and clinical review"),
    ("Very high risk", 100, "#8E2540", "Clinical review and intensive risk management"),
)

SWEEP_DEGREES = 270.0
START_ANGLE = 225.0


def angle_for(value: float) -> float:
    """Screen angle (degrees, counter-clockwise from east) for a 0-100 dial value."""
    return START_ANGLE - SWEEP_DEGREES * (max(0.0, min(100.0, value)) / 100.0)


def band_for(value_pct: float) -> tuple[str, str, str]:
    """Return (label, colour, follow-up) for a percentage estimate."""
    for label, upper, colour, follow_up in RISK_BANDS:
        if value_pct <= upper:
            return label, colour, follow_up
    return RISK_BANDS[-1][0], RISK_BANDS[-1][2], RISK_BANDS[-1][3]


def build_risk_gauge(value_pct: float, baseline_pct: float | None = None,
                     height: int = 400) -> tuple[go.Figure, dict]:
    """Build the gauge figure and return it with the resolved risk band."""
    label, colour, follow_up = band_for(value_pct)
    figure = go.Figure()

    edges = [0.0] + [upper for _, upper, _, _ in RISK_BANDS]
    for index, (_, _, band_colour, _) in enumerate(RISK_BANDS):
        low, high = edges[index], edges[index + 1]
        steps = max(int((high - low) * 2), 8)
        outer = [angle_for(low + (high - low) * step / steps) for step in range(steps + 1)]
        inner = list(reversed(outer))
        radii = [1.0] * len(outer) + [0.80] * len(inner)
        figure.add_trace(go.Scatterpolar(
            r=radii, theta=outer + inner, mode="lines", fill="toself",
            fillcolor=band_colour, line=dict(color=band_colour, width=0),
            hoverinfo="skip", showlegend=False))

    tick_r, tick_theta = [], []
    for tick in range(0, 101, 10):
        tick_r += [0.80, 0.74]
        tick_theta += [angle_for(tick), angle_for(tick)]
    figure.add_trace(go.Scatterpolar(
        r=tick_r, theta=tick_theta, mode="lines", line=dict(color="#54657E", width=1.6),
        hoverinfo="skip", showlegend=False))

    figure.add_trace(go.Scatterpolar(
        r=[0.66] * 11, theta=[angle_for(tick) for tick in range(0, 101, 10)],
        mode="text", text=[str(tick) for tick in range(0, 101, 10)],
        textfont=dict(color=MUTED, size=11), textposition="middle center",
        hoverinfo="skip", showlegend=False))

    if baseline_pct is not None:
        figure.add_trace(go.Scatterpolar(
            r=[0.78, 1.02], theta=[angle_for(baseline_pct), angle_for(baseline_pct)],
            mode="lines", line=dict(color="#F8FAFC", width=2.5),
            hoverinfo="skip", showlegend=False))

    needle_angle = angle_for(value_pct)
    figure.add_trace(go.Scatterpolar(
        r=[0.10, 0.86], theta=[needle_angle, needle_angle], mode="lines",
        line=dict(color="#070C16", width=7), hoverinfo="skip", showlegend=False))
    figure.add_trace(go.Scatterpolar(
        r=[0.09, 0.86], theta=[needle_angle, needle_angle], mode="lines",
        line=dict(color=NEEDLE, width=3), hoverinfo="skip", showlegend=False))
    figure.add_trace(go.Scatterpolar(
        r=[0], theta=[needle_angle], mode="markers",
        marker=dict(size=19, color="#0B1220", line=dict(color=HUB_RING, width=3)),
        hoverinfo="skip", showlegend=False))

    figure.update_layout(
        height=height,
        margin=dict(l=8, r=8, t=8, b=8),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT), showlegend=False,
        polar=dict(
            domain=dict(x=[0.06, 0.94], y=[0.04, 0.96]),
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=False, range=[0, 1]),
            angularaxis=dict(visible=False, rotation=0, direction="counterclockwise"),
        ),
        annotations=[
            dict(x=0.5, y=0.38, xref="paper", yref="paper", showarrow=False,
                 text=f"<b>{value_pct:.1f}%</b>", font=dict(size=52, color=TEXT,
                 family="Arial, Helvetica, sans-serif")),
            dict(x=0.5, y=0.28, xref="paper", yref="paper", showarrow=False,
                 text="estimated diabetes risk", font=dict(size=12, color=MUTED)),
        ],
    )
    return figure, {"label": label, "colour": colour, "follow_up": follow_up}


def badge_html(label: str, colour: str) -> str:
    """Pill badge that matches the band colour."""
    return (f'<div style="display:flex;justify-content:center;margin:2px 0 6px;">'
            f'<span style="border:1px solid {colour};color:{colour};border-radius:999px;'
            f'padding:5px 16px;font-size:13px;font-weight:700;letter-spacing:.03em;'
            f'background:rgba(255,255,255,.03);">🛡 &nbsp;{label}</span></div>')
