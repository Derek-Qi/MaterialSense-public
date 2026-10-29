"""Prespecified nested feature sets for paired, fixed-model ablation."""

from .features import material_features

FEATURE_SETS = ("raw", "water_binder", "scm_ratio", "total_mass")


def feature_set(frame, name):
    if name not in FEATURE_SETS:
        raise ValueError(f"Unknown feature set: {name}")
    x = material_features(frame, False)
    binder = x.cement + x.slag + x.fly_ash
    if name != "raw":
        x["water_binder"] = x.water / binder
    if name in ("scm_ratio", "total_mass"):
        x["scm_ratio"] = (x.slag + x.fly_ash) / binder
    if name == "total_mass":
        x["total_mass"] = (
            x.cement
            + x.slag
            + x.fly_ash
            + x.water
            + x.superplasticizer
            + x.coarse_aggregate
            + x.fine_aggregate
        )
    return x
