"""Presentation data for the live explorer. Never fit or modify the frozen models."""

from hashlib import sha256
from numbers import Real

import numpy as np
import pandas as pd

from materialsense.data import INPUTS, MATERIALS, recipe_ids, validate_frame
from materialsense.inference import predict_bundle

COLORS = ["#55c6cd", "#ae9ae7", "#eda57d", "#6ca9f0", "#e2cb74", "#94b9a1", "#c4cdd5"]
CONTROL_LIMITS = {
    "cement": (0.0, 650.0, 0.5),
    "slag": (0.0, 400.0, 0.5),
    "fly_ash": (0.0, 350.0, 0.5),
    "water": (0.0, 900.0, 0.5),
    "superplasticizer": (0.0, 50.0, 0.1),
    "coarse_aggregate": (0.0, 1400.0, 1.0),
    "fine_aggregate": (0.0, 1300.0, 1.0),
    "age": (1.0, 365.0, 1.0),
}


def snapshot_recipe(recipe):
    return validate_frame(pd.DataFrame([recipe]), require_target=False).iloc[0].to_dict()


def composition_data(recipe):
    values = snapshot_recipe(recipe)
    masses = np.array([values[key] for key in MATERIALS])
    return pd.DataFrame(
        {"ingredient": MATERIALS, "mass": masses, "fraction": masses / masses.sum()}
    )


def age_curve(bundle, recipe, ages=None):
    recipe = snapshot_recipe(recipe)
    ages = np.geomspace(1, 365, 64) if ages is None else np.asarray(ages, dtype=float)
    frame = pd.DataFrame([recipe] * len(ages))
    frame["age"] = ages
    result = predict_bundle(bundle, frame)
    result["age"] = ages
    return result


def prepare_observations(frame, expected_fingerprint):
    frame = validate_frame(frame).reset_index(drop=True)
    actual = sha256(frame.to_numpy(dtype="<f8").tobytes()).hexdigest()
    if actual != expected_fingerprint:
        raise ValueError("Measured-data fingerprint differs from this frozen experiment.")
    result = frame.copy()
    result["row_id"] = np.arange(len(frame))
    result["mix_id"] = recipe_ids(frame)
    result["water_binder"] = result.water / result[["cement", "slag", "fly_ash"]].sum(axis=1)
    return result


def selected_row(event, n_rows):
    try:
        selection = event["selection"]["sample"]
        value = selection[0]["row_id"]
        if isinstance(value, Real) and not isinstance(value, bool) and np.isfinite(value):
            index = int(value)
            if value == index and 0 <= index < n_rows:
                return index
    except (KeyError, IndexError, TypeError, ValueError, OverflowError):
        pass
    return None


def validated_assignments(path, observations):
    assignments = pd.read_csv(path)
    required = {"row_id", "mix_id", "partition"}
    if not required <= set(assignments) or len(assignments) != len(observations):
        raise ValueError("Saved split assignments are incomplete.")
    assignments = assignments.sort_values("row_id").reset_index(drop=True)
    if (
        assignments.row_id.tolist() != list(range(len(observations)))
        or assignments.mix_id.tolist() != observations.mix_id.tolist()
        or not set(assignments.partition) <= {"train", "calibration", "test"}
    ):
        raise ValueError("Saved split assignments do not match the measured observations.")
    return assignments


def input_values(state):
    return {key: float(state[key]) for key in INPUTS}
