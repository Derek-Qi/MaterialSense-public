from pathlib import Path

import joblib
import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


def test_missing_artifact_has_recovery_message(monkeypatch, tmp_path):
    monkeypatch.setenv("MATERIALSENSE_RUN_DIR", str(tmp_path / "missing"))
    app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
    assert not app.exception
    assert app.info


def test_dashboard_predicts_and_rejects_zero_binder(
    concrete_frame, tiny_config, tmp_path, monkeypatch
):
    from materialsense.experiment import run_experiment

    run_experiment(concrete_frame, tiny_config, tmp_path / "run")
    monkeypatch.setenv("MATERIALSENSE_RUN_DIR", str(tmp_path / "run"))
    app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
    assert not app.exception
    assert any(metric.label == "Predicted strength" for metric in app.metric)
    labels = {node.proto.label for node in app.get("download_button")}
    assert {"Download current prediction (CSV)", "Download benchmark metrics (CSV)"} <= labels
    assert all(
        node.proto.ignore_rerun
        for node in app.get("download_button")
        if node.proto.label.endswith("(CSV)")
    )
    for key in ["cement", "slag", "fly_ash"]:
        app.slider(key=key).set_value(0.0)
    app.run(timeout=30)
    assert not app.exception
    assert any("binder" in error.value.lower() for error in app.error)


@pytest.mark.parametrize(
    "missing", ["config", "input_ranges", "nested_coverage", "string_coverage", "string_range"]
)
def test_incomplete_bundle_has_recovery_instead_of_crashing(
    concrete_frame, tiny_config, tmp_path, monkeypatch, missing
):
    from materialsense.experiment import run_experiment

    run_dir = tmp_path / "run"
    run_experiment(concrete_frame, tiny_config, run_dir)
    bundle = joblib.load(run_dir / "model.joblib")
    if missing == "nested_coverage":
        del bundle["metadata"]["intervals"]["group_max_cqr"]
    elif missing == "string_coverage":
        bundle["metadata"]["nominal_coverage"] = "0.9"
    elif missing == "string_range":
        bundle["input_ranges"]["cement"][0] = "200.0"
    else:
        del bundle[missing]
    joblib.dump(bundle, run_dir / "model.joblib")
    monkeypatch.setenv("MATERIALSENSE_RUN_DIR", str(run_dir))
    app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
    assert not app.exception
    assert app.error


def test_broken_optional_evidence_does_not_break_predictions(
    concrete_frame, tiny_config, tmp_path, monkeypatch
):
    from materialsense.experiment import run_experiment

    run_dir = tmp_path / "run"
    run_experiment(concrete_frame, tiny_config, run_dir)
    (run_dir / "metrics.csv").write_text('"unterminated', encoding="utf-8")
    monkeypatch.setenv("MATERIALSENSE_RUN_DIR", str(run_dir))
    app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
    assert not app.exception
    assert any(metric.label == "Predicted strength" for metric in app.metric)
    assert app.warning


@pytest.mark.parametrize("missing", ["data_sha256_float64", "data_audit", "random_split_audit"])
def test_optional_explorer_metadata_fails_closed(
    concrete_frame, tiny_config, tmp_path, monkeypatch, missing
):
    from materialsense.experiment import run_experiment

    run_dir = tmp_path / "run"
    run_experiment(concrete_frame, tiny_config, run_dir)
    bundle = joblib.load(run_dir / "model.joblib")
    del bundle["metadata"][missing]
    joblib.dump(bundle, run_dir / "model.joblib")
    data_path = tmp_path / "data.csv"
    concrete_frame.to_csv(data_path, index=False)
    monkeypatch.setenv("MATERIALSENSE_RUN_DIR", str(run_dir))
    monkeypatch.setenv("MATERIALSENSE_DATA_PATH", str(data_path))
    app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
    assert not app.exception
    assert app.metric[0].label == "Predicted strength"
    if missing == "random_split_audit":
        app.radio(key="split_view").set_value("random").run(timeout=30)
        assert not app.exception


def test_corrupt_evidence_image_keeps_prediction_usable(
    concrete_frame, tiny_config, tmp_path, monkeypatch
):
    from materialsense.experiment import run_experiment

    run_dir = tmp_path / "run"
    run_experiment(concrete_frame, tiny_config, run_dir)
    (run_dir / "residuals.png").write_bytes(b"invalid-image")
    monkeypatch.setenv("MATERIALSENSE_RUN_DIR", str(run_dir))
    app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
    assert not app.exception
    assert app.metric[0].label == "Predicted strength"
    assert app.warning


def test_language_toggle_translates_ui_and_warnings_without_resetting_recipe(
    concrete_frame, tiny_config, tmp_path, monkeypatch
):
    from materialsense.experiment import run_experiment

    run_dir = tmp_path / "run"
    run_experiment(concrete_frame, tiny_config, run_dir)
    monkeypatch.setenv("MATERIALSENSE_RUN_DIR", str(run_dir))
    app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
    assert not app.exception
    assert app.button(key="language_toggle").label == "中文"
    assert app.slider(key="cement").label == "Cement"
    app.slider(key="water").set_value(900.0).run(timeout=30)
    assert not app.exception
    english_prediction = app.metric[0].value
    assert any("Water/binder" in warning.value for warning in app.warning)
    assert any("extrapolation" in warning.value for warning in app.warning)
    app.button(key="language_toggle").click().run(timeout=30)
    assert not app.exception
    assert app.button(key="language_toggle").label == "English"
    assert app.slider(key="cement").label == "水泥"
    assert app.slider(key="water").value == 900.0
    assert app.metric[0].label == "预测抗压强度"
    # Native widgets must explicitly receive the current value when labels change.
    # Otherwise the real browser can replay an older default on the return toggle.
    assert app.slider(key="water").proto.set_value
    assert list(app.slider(key="water").proto.value) == [900.0]
    assert app.metric[0].value == english_prediction
    assert any("水胶比" in warning.value for warning in app.warning)
    assert any("外推" in warning.value for warning in app.warning)
    app.button(key="language_toggle").click().run(timeout=30)
    assert not app.exception
    assert app.metric[0].value == english_prediction
    assert app.slider(key="water").value == 900.0
    assert app.slider(key="water").proto.set_value
    assert any(tab.label == "Research record" for tab in app.tabs)


def test_live_sliders_pin_independent_reference_and_reset(
    concrete_frame, tiny_config, tmp_path, monkeypatch
):
    from materialsense.experiment import run_experiment

    run_dir = tmp_path / "run"
    run_experiment(concrete_frame, tiny_config, run_dir)
    monkeypatch.setenv("MATERIALSENSE_RUN_DIR", str(run_dir))
    app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
    assert not app.exception
    assert not any(button.key == "predict" for button in app.button)
    initial = app.metric[0].value
    original_water = app.slider(key="water").value
    app.button(key="pin_a").click().run(timeout=30)
    app.slider(key="water").set_value(900.0).run(timeout=30)
    assert not app.exception
    assert app.metric[0].value != initial
    assert app.session_state["reference_recipe"]["water"] == original_water
    assert app.session_state["reference_recipe"]["age"] == 7.0
    app.slider(key="age").set_value(90.0).run(timeout=30)
    assert not app.exception
    assert app.session_state["reference_recipe"]["age"] == 7.0
    app.radio(key="interval_method").set_value("residual").run(timeout=30)
    assert not app.exception
    app.button(key="reset_recipe").click().run(timeout=30)
    assert not app.exception
    assert app.slider(key="water").value == original_water
    assert app.metric[0].value == initial


def test_measured_map_can_load_a_selected_sample(
    concrete_frame, tiny_config, tmp_path, monkeypatch
):
    from materialsense.experiment import run_experiment

    run_dir = tmp_path / "run"
    run_experiment(concrete_frame, tiny_config, run_dir)
    data_path = tmp_path / "concrete.csv"
    concrete_frame.to_csv(data_path, index=False)
    monkeypatch.setenv("MATERIALSENSE_RUN_DIR", str(run_dir))
    monkeypatch.setenv("MATERIALSENSE_DATA_PATH", str(data_path))
    app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
    assert not app.exception
    app.selectbox(key="sample_row").set_value(20).run(timeout=30)
    app.button(key="load_sample").click().run(timeout=30)
    assert not app.exception
    assert app.slider(key="water").value == concrete_frame.iloc[20].water
    assert app.slider(key="age").value == concrete_frame.iloc[20].age
    app.radio(key="split_view").set_value("random").run(timeout=30)
    assert not app.exception


def test_invalid_recipe_does_not_crash_pin_or_replace_reference(
    concrete_frame, tiny_config, tmp_path, monkeypatch
):
    from materialsense.experiment import run_experiment

    run_dir = tmp_path / "run"
    run_experiment(concrete_frame, tiny_config, run_dir)
    monkeypatch.setenv("MATERIALSENSE_RUN_DIR", str(run_dir))
    app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
    app.button(key="pin_a").click().run(timeout=30)
    reference = app.session_state["reference_recipe"].copy()
    for key in ["cement", "slag", "fly_ash"]:
        app.slider(key=key).set_value(0.0)
    app.run(timeout=30)
    app.button(key="pin_a").click().run(timeout=30)
    assert not app.exception
    assert app.error
    assert app.session_state["reference_recipe"] == reference


def test_map_can_reselect_a_point_after_dropdown_and_deselection(
    concrete_frame, tiny_config, tmp_path, monkeypatch
):
    import explorer_app
    from materialsense.experiment import run_experiment

    run_dir = tmp_path / "run"
    run_experiment(concrete_frame, tiny_config, run_dir)
    data_path = tmp_path / "data.csv"
    concrete_frame.to_csv(data_path, index=False)
    monkeypatch.setenv("MATERIALSENSE_RUN_DIR", str(run_dir))
    monkeypatch.setenv("MATERIALSENSE_DATA_PATH", str(data_path))
    event = {"selection": {"sample": [{"row_id": 5}]}}
    original_chart = explorer_app.chart

    def selected_chart(chart_object, **kwargs):
        rendered = original_chart(chart_object, **kwargs)
        return event if kwargs.get("key") == "sample_map" else rendered

    # AppTest cannot click Vega marks; inject only the external chart event boundary.
    monkeypatch.setattr(explorer_app, "chart", selected_chart)
    app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
    assert app.selectbox(key="sample_row").value == 5
    app.selectbox(key="sample_row").set_value(20).run(timeout=30)
    assert app.selectbox(key="sample_row").value == 20
    event["selection"]["sample"] = []
    app.run(timeout=30)
    event["selection"]["sample"] = [{"row_id": 5}]
    app.run(timeout=30)
    assert not app.exception
    assert app.selectbox(key="sample_row").value == 5


def test_language_toggle_is_available_before_training(monkeypatch, tmp_path):
    monkeypatch.setenv("MATERIALSENSE_RUN_DIR", str(tmp_path / "missing"))
    app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
    assert not app.exception
    assert "No trained experiment" in app.info[0].value
    app.button(key="language_toggle").click().run(timeout=30)
    assert not app.exception
    assert "尚未" in app.info[0].value
