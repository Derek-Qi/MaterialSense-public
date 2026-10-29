"""Deterministic, label-free material descriptors; no fitted state."""

import numpy as np

from .data import INPUTS, MATERIALS, validate_frame


def material_features(frame, engineered: bool = True):
    x = validate_frame(frame, require_target=False)[INPUTS].copy()
    if not engineered:
        return x
    binder = x.cement + x.slag + x.fly_ash
    x["binder"] = binder
    x["water_binder"] = x.water / binder
    x["water_cement"] = x.water / np.maximum(x.cement, 1.0)
    x["slag_fraction"] = x.slag / binder
    x["fly_ash_fraction"] = x.fly_ash / binder
    x["admixture_binder"] = x.superplasticizer / binder
    x["total_mass"] = x[MATERIALS].sum(axis=1)
    x["aggregate_binder"] = (x.coarse_aggregate + x.fine_aggregate) / binder
    x["log_age"] = np.log1p(x.age)
    if not np.isfinite(x.to_numpy()).all():
        raise ValueError("Engineered inputs overflowed; check ingredient magnitudes.")
    return x
