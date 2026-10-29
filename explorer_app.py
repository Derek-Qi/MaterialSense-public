"""The live materials workspace and its frozen research record."""

import json
import os
from functools import partial
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import streamlit as st

from dashboard_text import (
    feature_label,
    input_error,
    metrics_table,
    model_label,
    physical_warning,
    text,
)
from explorer import (
    CONTROL_LIMITS,
    age_curve,
    composition_data,
    input_values,
    prepare_observations,
    selected_row,
    snapshot_recipe,
    validated_assignments,
)
from explorer_charts import composition_chart, material_map, recipe_audit_chart, response_chart
from materialsense.artifacts import validate_bundle
from materialsense.data import INPUTS, MATERIALS, load_data
from materialsense.inference import predict_bundle
from materialsense.safety import physical_warnings

ROOT = Path(__file__).resolve().parent


@st.cache_resource
def load_bundle(path, modified_ns):
    return validate_bundle(joblib.load(path))


@st.cache_data(max_entries=128, show_spinner=False)
def cached_curve(token, material_values, _bundle):
    recipe = dict(zip(MATERIALS, material_values, strict=True))
    recipe["age"] = 28.0
    return age_curve(_bundle, recipe)


@st.cache_data(max_entries=8, show_spinner=False)
def load_observations(path, modified_ns, fingerprint):
    return prepare_observations(load_data(path), fingerprint)


def toggle_language():
    # Re-send current values to native controls whose labels/options are changing.
    # AppTest retains server state, but a browser can otherwise replay old defaults.
    for key in [*INPUTS, "preset", "interval_method", "split_view"]:
        if key in st.session_state:
            st.session_state[key] = st.session_state[key]
    st.session_state.ui_language = "en" if st.session_state.ui_language == "zh" else "zh"


def mark_custom():
    st.session_state.preset = "custom"


def set_recipe(recipe):
    for key in INPUTS:
        st.session_state[key] = float(recipe[key])
    mark_custom()


def reset_recipe():
    set_recipe(st.session_state["_example"])
    st.session_state.preset = "example"


def change_preset():
    name = st.session_state.preset
    if name == "custom":
        return
    recipe = st.session_state["_example"].copy()
    if name == "water":
        recipe["water"] = 900.0
    set_recipe(recipe)
    st.session_state.preset = name


def pin_reference():
    try:
        reference = snapshot_recipe(input_values(st.session_state))
    except (ValueError, TypeError):
        # The render path shows translated input guidance; preserve the prior A.
        return
    st.session_state.reference_recipe = reference


def clear_reference():
    st.session_state.reference_recipe = None


def chart(chart_object, **kwargs):
    return st.altair_chart(chart_object, width="stretch", theme=None, **kwargs)


def render_lab(bundle, token, language, t):
    labels = {key: t(key) for key in INPUTS}
    controls, stage = st.columns([1, 2.5], gap="large")
    with controls:
        st.subheader(t("live_b"))
        st.selectbox(
            t("preset"),
            ["example", "water", "custom"],
            key="preset",
            format_func=lambda key: t("preset_" + key),
            on_change=change_preset,
        )
        st.caption(t("slider_note"))
        for key in MATERIALS:
            minimum, maximum, step = CONTROL_LIMITS[key]
            maximum = max(maximum, float(st.session_state[key]))
            st.slider(
                labels[key],
                min_value=minimum,
                max_value=maximum,
                step=step,
                key=key,
                on_change=mark_custom,
                format="%.2f" if step < 1 else "%.0f",
            )
        st.button(t("reset"), key="reset_recipe", on_click=reset_recipe, width="stretch")
        st.caption(t("example") if st.session_state.preset == "example" else t("pin_hint"))
    with stage:
        st.slider(
            t("age"),
            min_value=1.0,
            max_value=max(365.0, float(st.session_state.age)),
            step=1.0,
            key="age",
            on_change=mark_custom,
            format="%.0f",
        )
        quick, pin, clear = st.columns([2, 2, 1])
        with quick:
            st.radio(
                t("interval_method"),
                ["cqr", "residual"],
                horizontal=True,
                format_func=lambda mode: t(mode + "_method"),
                key="interval_method",
            )
        with pin:
            st.button(t("pin"), key="pin_a", on_click=pin_reference, width="stretch")
        with clear:
            st.button(
                t("clear_a"),
                key="clear_a",
                on_click=clear_reference,
                disabled=st.session_state.reference_recipe is None,
            )
        try:
            recipe = snapshot_recipe(input_values(st.session_state))
            prediction = predict_bundle(bundle, pd.DataFrame([recipe])).iloc[0]
        except (ValueError, TypeError) as error:
            st.error(t("input_error", error=input_error(error, language)))
            st.stop()
        reference = st.session_state.reference_recipe
        ref_prediction = (
            predict_bundle(bundle, pd.DataFrame([reference])).iloc[0] if reference else None
        )
        prefix = st.session_state.interval_method
        low, high = prediction[f"{prefix}_lower_mpa"], prediction[f"{prefix}_upper_mpa"]
        finite = np.isfinite([low, high]).all()
        point_column, interval_column, width_column = st.columns([1.15, 1.4, 0.9])
        delta = (
            f"{prediction.point_mpa - ref_prediction.point_mpa:+.1f} MPa (B − A)"
            if reference
            else None
        )
        point_column.metric(
            t("point"), f"{prediction.point_mpa:.1f} MPa", delta=delta, delta_color="off"
        )
        interval_column.metric(
            t(
                "interval_metric",
                nominal=bundle["metadata"]["nominal_coverage"],
                method=t(prefix + "_method"),
            ),
            f"{low:.1f} – {high:.1f}" if finite else t("unbounded_value"),
        )
        width_column.metric(t("width_metric"), f"{high - low:.1f} MPa" if finite else "∞")
        st.subheader(t("curve_title"))
        curve = cached_curve(token, tuple(recipe[key] for key in MATERIALS), bundle)
        ref_curve = (
            cached_curve(token, tuple(reference[key] for key in MATERIALS), bundle)
            if reference
            else None
        )
        ref_marker = (
            {"age": reference["age"], "point_mpa": ref_prediction.point_mpa} if reference else None
        )
        chart(response_chart(curve, prediction, recipe["age"], prefix, t, ref_curve, ref_marker))
        st.html(
            '<div class="lab-legend"><span>'
            + t("live_b")
            + "</span>"
            + ('<span class="reference">' + t("reference_a") + "</span>" if reference else "")
            + "</div>"
        )
        st.caption(t("curve_note"))
        composition_column, risk_column = st.columns([1.15, 1], gap="large")
        with composition_column:
            st.subheader(t("composition"))
            composition = composition_data(recipe)
            chart(composition_chart(composition, labels, t))
            st.caption(t("mass_total", mass=composition.mass.sum()))
        with risk_column:
            st.subheader(t("risk_title"))
            threshold = bundle["ood"].threshold_
            st.progress(
                min(float(prediction.ood_distance) / max(2 * threshold, 1e-12), 1.0),
                text=t("distance_meter", distance=prediction.ood_distance, threshold=threshold),
            )
            if prediction.ood_warning:
                st.warning(t("ood"))
            else:
                st.info(t("no_ood"))
            for warning in physical_warnings(
                pd.DataFrame([recipe]), **bundle["config"]["heuristics"]
            ):
                st.warning(physical_warning(warning, language))
            outside = [
                labels[key]
                for key in INPUTS
                if not bundle["input_ranges"][key][0]
                <= recipe[key]
                <= bundle["input_ranges"][key][1]
            ]
            if outside:
                st.warning(
                    t("out_of_range", names=("、" if language == "zh" else ", ").join(outside))
                )
        if reference:
            st.subheader(t("comparison"))
            comparison_rows = []
            for name, values, result in [
                (t("reference_a"), reference, ref_prediction),
                (t("live_b"), recipe, prediction),
            ]:
                comparison_rows.append(
                    {
                        t("mix"): name,
                        t("age"): values["age"],
                        t("prediction"): result.point_mpa,
                        t("width_metric"): result[f"{prefix}_upper_mpa"]
                        - result[f"{prefix}_lower_mpa"],
                        "OOD": bool(result.ood_warning),
                    }
                )
            st.dataframe(pd.DataFrame(comparison_rows), hide_index=True, width="stretch")
        exported = pd.DataFrame([{**recipe, **prediction.to_dict()}])
        st.download_button(
            t("prediction_csv"),
            exported.to_csv(index=False),
            "materialsense-prediction.csv",
            "text/csv",
            key="prediction_csv",
            on_click="ignore",
        )
    return recipe, prediction


def render_data(bundle, run_dir, recipe, prediction, language, t):
    st.subheader(t("map_title"))
    data_path = Path(os.environ.get("MATERIALSENSE_DATA_PATH", str(ROOT / "data/raw/concrete.csv")))
    try:
        observations = load_observations(
            str(data_path), data_path.stat().st_mtime_ns, bundle["metadata"]["data_sha256_float64"]
        )
    except (OSError, ValueError, KeyError, TypeError) as error:
        st.info(t("data_unavailable"))
        with st.expander(t("details")):
            st.write(str(error))
        return
    st.caption(t("map_hint"))
    event = chart(
        material_map(observations, recipe, prediction, t),
        key="sample_map",
        on_select="rerun",
        selection_mode="sample",
    )
    picked = selected_row(event, len(observations))
    if picked != st.session_state.get("last_map_selection"):
        if picked is not None:
            st.session_state.sample_row = picked
        st.session_state.last_map_selection = picked
    if st.session_state.get("sample_row", 0) not in range(len(observations)):
        st.session_state.sample_row = 0
    selected_column, action = st.columns([3, 2], vertical_alignment="bottom")
    with selected_column:
        row_id = st.selectbox(
            t("sample"),
            observations.row_id.tolist(),
            key="sample_row",
            format_func=lambda index: (
                f"#{index} ({observations.iloc[index].age:g} d, "
                f"{observations.iloc[index].strength:.2f} MPa)"
            ),
        )
    row = observations.iloc[row_id]
    with action:
        st.button(
            t("load_sample"),
            key="load_sample",
            on_click=set_recipe,
            args=(row[INPUTS].to_dict(),),
            width="stretch",
        )
    st.caption(t("selected_sample", strength=row.strength, age=row.age, row=row_id))
    st.dataframe(
        pd.DataFrame([{t(key): row[key] for key in INPUTS}]), hide_index=True, width="stretch"
    )
    st.divider()
    st.subheader(t("split_title"))
    protocol = st.radio(
        t("split_view"),
        ["grouped", "random"],
        key="split_view",
        horizontal=True,
        format_func=lambda value: t(value),
    )
    metadata = bundle["metadata"]
    try:
        audit = metadata["split_audit" if protocol == "grouped" else "random_split_audit"]
        shared = audit["pairwise_overlap"]["train_test"]
        if not isinstance(shared, int) or shared < 0:
            raise ValueError("Invalid shared-recipe count.")
    except (KeyError, TypeError, ValueError):
        st.warning(t("assignments_unavailable"))
        return
    shared_column, metric_column = st.columns(2)
    shared_column.metric(t("shared_recipes"), shared)
    metrics_path = run_dir / "metrics.csv"
    try:
        metrics = pd.read_csv(metrics_path)
        selected = bundle["selected"]
        row_metrics = metrics[
            (metrics.protocol == ("grouped" if protocol == "grouped" else "row_random_diagnostic"))
            & (metrics.model == selected["model"])
            & (metrics.features == selected["features"])
        ].iloc[0]
        metric_column.metric(t("test_rmse"), f"{row_metrics.rmse:.3f} MPa")
    except (OSError, ValueError, AttributeError, IndexError, KeyError):
        pass  # The research-record tab provides the actionable optional-evidence warning.
    try:
        name = "split_assignments.csv" if protocol == "grouped" else "random_split_assignments.csv"
        assignments = validated_assignments(run_dir / name, observations)
        data = observations.merge(
            assignments[["row_id", "partition"]], on="row_id", validate="one_to_one"
        )
        repeated = data.mix_id.value_counts()
        options = repeated[repeated > 1].index.tolist()
        if options:
            mix = st.selectbox(
                t("audit_recipe"),
                options,
                key="audit_recipe",
                format_func=lambda value: "Mix " + value[:12],
            )
            chart(recipe_audit_chart(data[data.mix_id == mix], t))
    except (OSError, ValueError, KeyError) as error:
        st.warning(t("assignments_unavailable"))
        with st.expander(t("details")):
            st.write(str(error))
    st.caption(t("split_note"))


def render_record(bundle, run_dir, language, t):
    metadata, selected = bundle["metadata"], bundle["selected"]
    st.write(
        t(
            "selected",
            model=model_label(selected["model"], language),
            features=feature_label(selected["features"], language),
        )
    )
    st.write(t("coverage", **metadata["intervals"]["group_max_cqr"]))
    st.caption(t("interval_note"))
    try:
        metrics = pd.read_csv(run_dir / "metrics.csv")
        if not {"protocol", "model", "features", "rmse", "mae", "r2"} <= set(metrics.columns):
            raise ValueError("The evidence table is missing required columns.")
        st.dataframe(metrics_table(metrics, language), hide_index=True, width="stretch")
        st.download_button(
            t("benchmark_csv"),
            metrics.to_csv(index=False),
            "materialsense-benchmark.csv",
            "text/csv",
            key="benchmark_csv",
            on_click="ignore",
        )
    except (OSError, ValueError) as error:
        st.warning(t("evidence_error", error=error))
    for filename in ["residuals.png", "ablation.png"]:
        if (run_dir / filename).exists():
            try:
                st.image(str(run_dir / filename), width="stretch")
            except (OSError, ValueError) as error:
                st.warning(t("evidence_error", error=error))
    st.download_button(
        t("download"),
        data=json.dumps(metadata, indent=2),
        file_name="materialsense-metadata.json",
        mime="application/json",
    )
    st.write(t("group_method"))
    st.write(t("calibration_method"))
    st.write(t("warning_method"))
    st.markdown(
        t("source") + ": [I-Cheng Yeh, UCI Concrete Compressive Strength]"
        "(https://doi.org/10.24432/C5PK67), CC BY 4.0."
    )
    st.caption(t("saved_run", date=metadata["created_utc"], seed=bundle["config"]["seed"]))


def main():
    st.set_page_config(
        page_title="MaterialSense | Live materials lab", page_icon="🧱", layout="wide"
    )
    st.html("<style>" + (ROOT / "assets/explorer.css").read_text(encoding="utf-8") + "</style>")
    language = st.session_state.setdefault("ui_language", "en")
    t = partial(text, language=language)
    title, language_column = st.columns([5, 1], vertical_alignment="center")
    title.title("MaterialSense")
    language_column.button(
        "English" if language == "zh" else "中文",
        key="language_toggle",
        on_click=toggle_language,
        width="stretch",
    )
    st.subheader(t("lab_title"))
    st.html('<p class="lab-deck">' + t("lab_intro") + "</p>")
    run_dir = Path(os.environ.get("MATERIALSENSE_RUN_DIR", str(ROOT / "artifacts/run")))
    path = run_dir / "model.joblib"
    if not path.exists():
        st.info(t("missing"))
        st.code("python -m materialsense.cli download\npython -m materialsense.cli run")
        st.stop()
    try:
        bundle = load_bundle(str(path), path.stat().st_mtime_ns)
    except Exception as error:
        st.error(t("load_error", error=error))
        st.stop()
    st.session_state["_example"] = bundle["example"].copy()
    for key in INPUTS:
        st.session_state.setdefault(key, float(bundle["example"][key]))
    st.session_state.setdefault("reference_recipe", None)
    st.session_state.setdefault("preset", "example")
    metadata = bundle["metadata"]
    try:
        audit = metadata["data_audit"]
        if not all(isinstance(audit[key], int) and audit[key] > 0 for key in ["rows", "recipes"]):
            raise ValueError("Invalid dataset counts.")
        st.caption(
            t(
                "lab_stats",
                rows=audit["rows"],
                recipes=audit["recipes"],
                model=model_label(bundle["selected"]["model"], language),
            )
        )
    except (KeyError, TypeError, ValueError):
        st.caption(model_label(bundle["selected"]["model"], language))
    live, data, record = st.tabs([t("lab_tab"), t("data_tab"), t("record_tab")])
    with live:
        recipe, prediction = render_lab(bundle, (str(path), path.stat().st_mtime_ns), language, t)
    with data:
        render_data(bundle, run_dir, recipe, prediction, language, t)
    with record:
        render_record(bundle, run_dir, language, t)
    st.caption(t("research_note"))
