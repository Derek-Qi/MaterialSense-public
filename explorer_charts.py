"""Linked scientific views for the explorer; no simulated measurements."""

import altair as alt
import numpy as np
import pandas as pd

from explorer import COLORS

INK = "#dceaf3"
MUTED = "#9cb6c8"
CYAN = "#55c6cd"
AMBER = "#f1ba69"


def finish(chart, height):
    return (
        chart.properties(height=height, background="transparent")
        .configure_view(stroke=None)
        .configure_axis(
            labelColor=MUTED,
            titleColor=INK,
            gridColor="#2c475b",
            domainColor="#476276",
            tickColor="#476276",
            titleFontSize=12,
        )
        .configure_legend(labelColor=INK, titleColor=MUTED, labelFontSize=11)
        .configure_title(color=INK)
    )


def response_chart(curve, current, current_age, prefix, t, reference_curve=None, reference=None):
    x = alt.X(
        "age:Q",
        title=t("age"),
        scale=alt.Scale(type="log", domain=[1, 365]),
        axis=alt.Axis(values=[1, 3, 7, 14, 28, 56, 90, 180, 365], format="g"),
    )
    layers = []
    for frame, color, opacity, dashed in [
        (reference_curve, AMBER, 0.07, True),
        (curve, CYAN, 0.18, False),
    ]:
        if frame is None:
            continue
        base = alt.Chart(frame).encode(x=x)
        if np.isfinite(frame[[f"{prefix}_lower_mpa", f"{prefix}_upper_mpa"]].to_numpy()).all():
            layers.append(
                base.mark_area(color=color, opacity=opacity).encode(
                    y=alt.Y(f"{prefix}_lower_mpa:Q", title=t("strength_axis")),
                    y2=f"{prefix}_upper_mpa:Q",
                )
            )
        layers.append(
            base.mark_line(
                color=color, strokeWidth=2.7, strokeDash=[5, 3] if dashed else [1, 0]
            ).encode(
                y=alt.Y("point_mpa:Q", title=t("strength_axis")),
                tooltip=[
                    alt.Tooltip("age:Q", title=t("age"), format=".1f"),
                    alt.Tooltip("point_mpa:Q", title=t("point_axis"), format=".1f"),
                ],
            )
        )
    marker = pd.DataFrame([{"age": current_age, "point_mpa": current.point_mpa}])
    layers += [
        alt.Chart(marker).mark_rule(color=CYAN, strokeDash=[3, 4], opacity=0.6).encode(x=x),
        alt.Chart(marker)
        .mark_point(color=CYAN, filled=True, size=140, stroke="#ffffff", strokeWidth=2)
        .encode(x=x, y="point_mpa:Q"),
    ]
    if reference is not None:
        point = pd.DataFrame([reference])
        layers.append(
            alt.Chart(point)
            .mark_point(color=AMBER, filled=True, size=95)
            .encode(x=x, y="point_mpa:Q")
        )
    return finish(alt.layer(*layers), 300)


def composition_chart(composition, labels, t):
    frame = composition.copy()
    frame["label"] = frame.ingredient.map(labels)
    domain = [labels[key] for key in frame.ingredient]
    chart = (
        alt.Chart(frame)
        .mark_arc(innerRadius=43, outerRadius=72, stroke="#10283b", strokeWidth=2)
        .encode(
            theta=alt.Theta("mass:Q", stack=True),
            color=alt.Color(
                "label:N",
                scale=alt.Scale(domain=domain, range=COLORS),
                legend=alt.Legend(title=None, orient="right", labelLimit=160),
            ),
            order=alt.Order("fraction:Q", sort="descending"),
            tooltip=[
                alt.Tooltip("label:N", title=t("ingredient")),
                alt.Tooltip("mass:Q", title="kg/m³", format=".1f"),
                alt.Tooltip("fraction:Q", title=t("mass_share"), format=".1%"),
            ],
        )
    )
    return finish(chart, 165)


def material_map(observed, recipe, prediction, t):
    selection = alt.selection_point(
        name="sample",
        fields=["row_id"],
        nearest=True,
        toggle=False,
        on="click",
        clear="dblclick",
        empty=False,
    )
    base = (
        alt.Chart(observed)
        .mark_circle(size=36)
        .encode(
            x=alt.X("water_binder:Q", title=t("water_binder")),
            y=alt.Y("strength:Q", title=t("measured_axis")),
            color=alt.Color(
                "age:Q", title=t("age"), scale=alt.Scale(scheme="tealblues", type="log")
            ),
            opacity=alt.condition(selection, alt.value(1), alt.value(0.48)),
            stroke=alt.condition(selection, alt.value("#ffffff"), alt.value("transparent")),
            strokeWidth=alt.value(2),
            tooltip=[
                alt.Tooltip("row_id:Q", title=t("sample"), format="d"),
                alt.Tooltip("age:Q", title=t("age"), format="g"),
                alt.Tooltip("strength:Q", title=t("measured_axis"), format=".2f"),
                alt.Tooltip("water_binder:Q", title=t("water_binder"), format=".3f"),
            ],
        )
        .add_params(selection)
    )
    binder = recipe["cement"] + recipe["slag"] + recipe["fly_ash"]
    current = pd.DataFrame(
        [
            {
                "water_binder": recipe["water"] / binder,
                "strength": prediction.point_mpa,
                "label": t("live_b"),
            }
        ]
    )
    query = (
        alt.Chart(current)
        .mark_point(
            shape="diamond", color=AMBER, filled=True, size=240, stroke="#ffffff", strokeWidth=1.5
        )
        .encode(
            x="water_binder:Q",
            y="strength:Q",
            tooltip=[
                alt.Tooltip("label:N", title=""),
                alt.Tooltip("strength:Q", title=t("point_axis"), format=".1f"),
            ],
        )
    )
    return finish((base + query).interactive(), 330)


def recipe_audit_chart(rows, t):
    palette = alt.Scale(domain=["train", "calibration", "test"], range=[CYAN, "#ae9ae7", AMBER])
    x = alt.X("age:Q", title=t("age"), scale=alt.Scale(type="log"))
    base = alt.Chart(rows)
    line = base.mark_line(color="#698395", strokeDash=[3, 3], opacity=0.7).encode(
        x=x, y=alt.Y("strength:Q", title=t("measured_axis"))
    )
    points = base.mark_circle(size=125, opacity=0.9).encode(
        x=x,
        y="strength:Q",
        color=alt.Color("partition:N", title=t("partition"), scale=palette),
        tooltip=[
            alt.Tooltip("row_id:Q", title=t("sample")),
            alt.Tooltip("age:Q", title=t("age")),
            alt.Tooltip("strength:Q", title=t("measured_axis"), format=".2f"),
            alt.Tooltip("partition:N", title=t("partition")),
        ],
    )
    return finish(line + points, 230)
