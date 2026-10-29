from copy import deepcopy
from hashlib import sha256

import numpy as np
import pandas as pd
import pytest


def test_snapshot_and_mass_shares_do_not_mutate_recipe(concrete_frame):
    from explorer import composition_data, snapshot_recipe

    recipe = concrete_frame.iloc[0, :8].to_dict()
    snapshot = snapshot_recipe(recipe)
    recipe["water"] = 900
    assert snapshot["water"] != 900
    simple = {
        "cement": 200,
        "slag": 50,
        "fly_ash": 50,
        "water": 150,
        "superplasticizer": 0,
        "coarse_aggregate": 1000,
        "fine_aggregate": 800,
        "age": 28,
    }
    before = deepcopy(simple)
    composition = composition_data(simple)
    assert composition.mass.sum() == 2250
    assert composition.loc[composition.ingredient == "cement", "fraction"].iloc[0] == pytest.approx(
        200 / 2250
    )
    assert composition.fraction.sum() == pytest.approx(1)
    assert simple == before


def test_measured_data_requires_matching_provenance(concrete_frame):
    from explorer import prepare_observations

    fingerprint = sha256(concrete_frame.to_numpy(dtype="<f8").tobytes()).hexdigest()
    observed = prepare_observations(concrete_frame, fingerprint)
    assert observed.row_id.tolist() == list(range(len(concrete_frame)))
    assert observed.loc[0, "water_binder"] == pytest.approx(
        concrete_frame.loc[0, "water"] / concrete_frame.loc[0, ["cement", "slag", "fly_ash"]].sum()
    )
    altered = concrete_frame.copy()
    altered.loc[0, "strength"] += 1
    with pytest.raises(ValueError, match="fingerprint"):
        prepare_observations(altered, fingerprint)


@pytest.mark.parametrize(
    "selection,expected",
    [
        ({"selection": {"sample": [{"row_id": 3}]}}, 3),
        ({"selection": {"sample": []}}, None),
        ({"selection": {"sample": [{"row_id": -1}]}}, None),
        ({"selection": {"sample": [{"row_id": 999}]}}, None),
        ({"selection": {"sample": [{"row_id": 1.5}]}}, None),
        ({"selection": {"sample": [{"row_id": True}]}}, None),
        ({}, None),
    ],
)
def test_chart_selection_only_accepts_valid_row_ids(selection, expected):
    from explorer import selected_row

    assert selected_row(selection, 10) == expected


def test_age_curve_uses_model_predictions_and_preserves_input(
    concrete_frame, tiny_config, tmp_path
):
    import joblib

    from explorer import age_curve
    from materialsense.experiment import run_experiment
    from materialsense.inference import predict_bundle

    run_experiment(concrete_frame, tiny_config, tmp_path)
    bundle = joblib.load(tmp_path / "model.joblib")
    recipe = concrete_frame.iloc[0, :8].to_dict()
    before = recipe.copy()
    curve = age_curve(bundle, recipe, ages=[7, 28, 90])
    query = pd.DataFrame([recipe] * 3)
    query["age"] = [7, 28, 90]
    exact = predict_bundle(bundle, query)
    np.testing.assert_array_equal(curve.point_mpa, exact.point_mpa)
    assert curve.age.tolist() == [7, 28, 90]
    assert recipe == before
