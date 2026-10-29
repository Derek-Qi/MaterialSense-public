import json
from copy import deepcopy

import joblib
import numpy as np
import pandas as pd
import pytest


def test_offline_pipeline_writes_auditable_reproducible_outputs(
    concrete_frame, tiny_config, tmp_path
):
    from materialsense.experiment import run_experiment
    from materialsense.inference import predict_bundle

    first, second = tmp_path / "first", tmp_path / "second"
    result = run_experiment(concrete_frame, tiny_config, first)
    again = run_experiment(concrete_frame, tiny_config, second)
    assert result["selected"] == again["selected"]
    pd.testing.assert_frame_equal(
        pd.read_csv(first / "metrics.csv"), pd.read_csv(second / "metrics.csv")
    )
    audit = pd.read_csv(first / "split_assignments.csv")
    assert audit.groupby("mix_id")["partition"].nunique().max() == 1
    assert set(audit.partition) == {"train", "calibration", "test"}
    assert set(pd.read_csv(first / "metrics.csv").model) == {
        "mean",
        "ridge",
        "random_forest",
        "gradient_boosting",
    }
    assert (first / "residuals.png").stat().st_size > 1000
    assert (first / "ablation.csv").is_file()
    assert json.loads((first / "metadata.json").read_text())["split_audit"]["overlap_groups"] == 0
    bundle = joblib.load(first / "model.joblib")
    predictions = predict_bundle(bundle, concrete_frame.iloc[:2])
    assert len(predictions) == 2
    assert np.isfinite(predictions.point_mpa).all()
    assert (predictions.cqr_lower_mpa <= predictions.cqr_upper_mpa).all()
    train_rows = audit.loc[audit.partition == "train", "row_id"]
    assert bundle["ood"].scaler_.mean_.tolist() == pytest.approx(
        concrete_frame.iloc[train_rows, :8].mean().tolist()
    )


def test_heldout_labels_cannot_affect_selection_or_fitted_point_model(
    concrete_frame, tiny_config, tmp_path
):
    from materialsense.data import recipe_ids
    from materialsense.experiment import run_experiment
    from materialsense.splitting import grouped_split

    groups = recipe_ids(concrete_frame)
    parts = grouped_split(groups, 42, [0.6, 0.2, 0.2])
    altered = concrete_frame.copy()
    altered.loc[np.concatenate([parts["calibration"], parts["test"]]), "strength"] += 1000
    one = run_experiment(concrete_frame, tiny_config, tmp_path / "one")
    two = run_experiment(altered, tiny_config, tmp_path / "two")
    assert one["selected"] == two["selected"]
    p1 = pd.read_csv(tmp_path / "one" / "test_predictions.csv")
    p2 = pd.read_csv(tmp_path / "two" / "test_predictions.csv")
    np.testing.assert_array_equal(p1.point_mpa, p2.point_mpa)


@pytest.mark.parametrize(
    "patch",
    [
        {"alpha": 0},
        {"cv_folds": 1},
        {"split": {"train": 0.6, "calibration": 0, "test": 0.4}},
    ],
)
def test_invalid_experiment_config_is_rejected_before_training(tiny_config, patch):
    from materialsense.experiment import validate_config

    changed = deepcopy(tiny_config)
    changed.update(patch)
    with pytest.raises(ValueError):
        validate_config(changed)
