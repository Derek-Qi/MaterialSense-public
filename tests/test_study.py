from copy import deepcopy

import numpy as np
import pandas as pd
import pytest


def test_incremental_features_have_explicit_definitions(concrete_frame):
    from materialsense.study_features import feature_set

    raw = feature_set(concrete_frame, "raw")
    wb = feature_set(concrete_frame, "water_binder")
    scm = feature_set(concrete_frame, "scm_ratio")
    mass = feature_set(concrete_frame, "total_mass")
    assert raw.shape[1] == 8
    assert list(wb.columns) == list(raw.columns) + ["water_binder"]
    assert list(scm.columns) == list(wb.columns) + ["scm_ratio"]
    binder = concrete_frame.cement + concrete_frame.slag + concrete_frame.fly_ash
    np.testing.assert_allclose(wb.water_binder, concrete_frame.water / binder)
    np.testing.assert_allclose(
        scm.scm_ratio, (concrete_frame.slag + concrete_frame.fly_ash) / binder
    )
    np.testing.assert_allclose(mass.total_mass, concrete_frame.iloc[:, :7].sum(axis=1))
    with pytest.raises(ValueError):
        feature_set(concrete_frame, "unknown")


def test_full_row_audit_counts_distinct_duplicates_and_recipe_overlap(concrete_frame):
    from materialsense.diagnostics import partition_audit

    frame = concrete_frame.iloc[[0, 0, 1]].reset_index(drop=True)
    frame.loc[2, "strength"] += 1
    result = partition_audit(frame, {"train": np.array([0]), "test": np.array([1, 2])})
    pair = result[0]
    assert pair["shared_complete_rows"] == 1
    assert pair["test_rows_duplicated_in_train"] == 1
    assert pair["shared_recipes"] == 1


def test_risk_confusion_uses_prespecified_error_event_and_training_threshold():
    from materialsense.diagnostics import risk_table, width_error_correlation

    pred = pd.DataFrame(
        {
            "actual_mpa": [0, 0, 0, 0],
            "point_mpa": [1, 12, 3, 14],
            "ood_distance": [0, 1, 2, 3],
            "cqr_lower_mpa": [0] * 4,
            "cqr_upper_mpa": [5] * 4,
        }
    )
    row = risk_table(pred, np.array([0, 1, 2]), [0.5], 10).iloc[0]
    assert row.threshold == 1
    assert (row.tp, row.fp, row.fn, row.tn) == (1, 1, 1, 1)
    assert row.precision == 0.5 and row.recall == 0.5
    assert width_error_correlation(pred, "cqr") is None


def test_summary_reports_sample_sd_not_confidence_interval():
    from materialsense.diagnostics import summarize

    result = summarize(pd.DataFrame({"model": ["x", "x"], "rmse": [2, 4]}), ["model"], ["rmse"])
    row = result.iloc[0]
    assert row["mean"] == 3 and row["std"] == pytest.approx(np.sqrt(2))
    assert row["min"] == 2 and row["max"] == 4 and row["count"] == 2


def test_study_is_reproducible_and_writes_per_seed_evidence(concrete_frame, tiny_config, tmp_path):
    from materialsense.study import run_study

    tiny_config = deepcopy(tiny_config)
    tiny_config["alpha"] = 0.2
    settings = {
        "seeds": [42, 43],
        "ood_quantiles": [0.8, 0.95],
        "high_error_mpa": 7.5,
        "permutation_repeats": 2,
    }
    first = tmp_path / "first"
    second = tmp_path / "second"
    run_study(concrete_frame, tiny_config, settings, first)
    run_study(concrete_frame, tiny_config, settings, second)
    assert ">7.5 MPa" in (first / "summary.md").read_text(encoding="utf-8")
    assert "80.0%" in (first / "summary.md").read_text(encoding="utf-8")
    for name in ["metrics.csv", "ablation.csv", "intervals.csv", "risk_thresholds.csv"]:
        pd.testing.assert_frame_equal(pd.read_csv(first / name), pd.read_csv(second / name))
    audit = pd.read_csv(first / "split_audit.csv")
    assert (audit.loc[audit.protocol == "grouped", "shared_recipes"] == 0).all()
    assert set(pd.read_csv(first / "ablation.csv").features) == {
        "raw",
        "water_binder",
        "scm_ratio",
        "total_mass",
    }
    assert (first / "seed-42/model.joblib").is_file()
    assert (first / "seed-43/calibration_group_scores.csv").is_file()
    with pytest.raises(FileExistsError):
        run_study(concrete_frame, tiny_config, settings, first)
    bad = deepcopy(settings)
    bad["seeds"] = [42, 42]
    with pytest.raises(ValueError):
        run_study(concrete_frame, tiny_config, bad, tmp_path / "bad")


def test_risk_exact_boundary_and_empty_denominators():
    from materialsense.diagnostics import risk_table

    pred = pd.DataFrame({"actual_mpa": [0, 0], "point_mpa": [10, 1], "ood_distance": [0, 0]})
    row = risk_table(pred, np.array([1, 2]), [0.95], 10).iloc[0]
    assert row.tp == 0 and row.fn == 0 and row.tn == 2
    assert row.precision is None or pd.isna(row.precision)
    assert row.recall is None or pd.isna(row.recall)
    assert row.flagged_mae is None or pd.isna(row.flagged_mae)
