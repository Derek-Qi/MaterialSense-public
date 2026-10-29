"""Validate trusted local bundles before presenting a dashboard."""

import json
from numbers import Real

import numpy as np
import pandas as pd

from .data import INPUTS, validate_frame
from .experiment import validate_config
from .inference import predict_bundle


def validate_bundle(bundle):
    """Reject incomplete or incompatible artifacts inside the UI's recovery guard.

    This is compatibility validation, not a security sandbox for pickle files.
    A real inference probe also checks fitted models and the OOD feature schema.
    """
    if not isinstance(bundle, dict):
        raise ValueError("Expected a dictionary model bundle.")
    validate_config(bundle["config"])
    if not isinstance(bundle["engineered"], bool):
        raise ValueError("Invalid point-model feature flag.")
    for key in ["residual_correction", "cqr_correction"]:
        value = float(bundle[key])
        if np.isnan(value) or value < 0:
            raise ValueError(f"Invalid interval correction: {key}")
    metadata = bundle["metadata"]
    nominal = metadata["nominal_coverage"]
    if not isinstance(nominal, Real) or isinstance(nominal, bool) or not 0 < nominal < 1:
        raise ValueError("Invalid nominal coverage.")
    if not isinstance(metadata["created_utc"], str):
        raise ValueError("Missing run timestamp.")
    for key in ["model", "features"]:
        if not isinstance(bundle["selected"][key], str):
            raise ValueError("Invalid selected model description.")
    stats = metadata["intervals"]["group_max_cqr"]
    for covered, total in [("covered_rows", "n_rows"), ("covered_recipes", "n_recipes")]:
        if not (
            isinstance(stats[covered], int)
            and isinstance(stats[total], int)
            and 0 <= stats[covered] <= stats[total]
            and stats[total] > 0
        ):
            raise ValueError("Invalid measured coverage counts.")
    for key in INPUTS:
        raw_bounds = bundle["input_ranges"][key]
        if not all(isinstance(value, Real) and not isinstance(value, bool) for value in raw_bounds):
            raise ValueError(f"Nonnumeric training input range: {key}")
        bounds = np.asarray(raw_bounds, dtype=float)
        if bounds.shape != (2,) or not np.isfinite(bounds).all() or not 0 <= bounds[0] <= bounds[1]:
            raise ValueError(f"Invalid training input range: {key}")
    if bundle["input_ranges"]["age"][0] <= 0:
        raise ValueError("Training ages must be positive.")
    example = validate_frame(pd.DataFrame([bundle["example"]]), require_target=False)
    probe = predict_bundle(bundle, example)
    if not np.isfinite(probe[["point_mpa", "ood_distance"]].to_numpy()).all():
        raise ValueError("Model returned nonfinite point predictions or OOD distances.")
    if not np.isfinite(bundle["ood"].threshold_):
        raise ValueError("Invalid OOD threshold.")
    json.dumps(metadata, allow_nan=False)
    return bundle
