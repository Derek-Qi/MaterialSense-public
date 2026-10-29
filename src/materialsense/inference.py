"""One inference path shared by benchmark, dashboard and tests."""

import pandas as pd

from .data import INPUTS, validate_frame
from .features import material_features
from .uncertainty import cqr_interval


def predict_bundle(bundle, frame):
    frame = validate_frame(frame, require_target=False)
    point = bundle["point_model"].predict(material_features(frame, bundle["engineered"]))
    x = material_features(frame, True)
    low, high = cqr_interval(
        bundle["quantile_models"][0].predict(x),
        bundle["quantile_models"][1].predict(x),
        bundle["cqr_correction"],
    )
    distance, flag = bundle["ood"].predict(frame[INPUTS].to_numpy())
    return pd.DataFrame(
        {
            "point_mpa": point,
            "residual_lower_mpa": point - bundle["residual_correction"],
            "residual_upper_mpa": point + bundle["residual_correction"],
            "cqr_lower_mpa": low,
            "cqr_upper_mpa": high,
            "ood_distance": distance,
            "ood_warning": flag,
        },
        index=frame.index,
    )
