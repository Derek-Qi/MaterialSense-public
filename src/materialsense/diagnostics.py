"""Descriptive held-out diagnostics. No model/threshold fitting occurs here."""

from hashlib import sha256
from itertools import combinations

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from .data import recipe_ids, validate_frame


def partition_audit(frame, parts):
    frame = validate_frame(frame)
    groups = recipe_ids(frame)
    values = frame.to_numpy(dtype="<f8")
    values[values == 0] = 0.0
    identities = np.array([sha256(row.tobytes()).hexdigest() for row in values])
    rows = []
    for a, b in combinations(parts, 2):
        ia, ib = parts[a], parts[b]
        rows.append(
            {
                "pair": f"{a}_{b}",
                "a_rows": len(ia),
                "b_rows": len(ib),
                "a_groups": len(set(groups[ia])),
                "b_groups": len(set(groups[ib])),
                "shared_recipes": len(set(groups[ia]) & set(groups[ib])),
                "shared_complete_rows": len(set(identities[ia]) & set(identities[ib])),
                "test_rows_duplicated_in_train": int(np.isin(identities[ib], identities[ia]).sum()),
            }
        )
    return rows


def _ratio(a, b):
    return float(a / b) if b else None


def risk_table(predictions, training_distances, quantiles, high_error_mpa):
    absolute = np.abs(predictions.actual_mpa - predictions.point_mpa).to_numpy()
    large_error = absolute > high_error_mpa
    rows = []
    for quantile in quantiles:
        threshold = float(np.quantile(training_distances, quantile))
        alarm = predictions.ood_distance.to_numpy() > threshold
        tp, fp = int((alarm & large_error).sum()), int((alarm & ~large_error).sum())
        fn, tn = int((~alarm & large_error).sum()), int((~alarm & ~large_error).sum())
        rows.append(
            {
                "training_quantile": quantile,
                "threshold": threshold,
                "high_error_mpa": high_error_mpa,
                "n_rows": len(absolute),
                "flagged": int(alarm.sum()),
                "tp": tp,
                "fp": fp,
                "fn": fn,
                "tn": tn,
                "precision": _ratio(tp, tp + fp),
                "recall": _ratio(tp, tp + fn),
                "false_positive_rate": _ratio(fp, fp + tn),
                "false_negative_rate": _ratio(fn, fn + tp),
                "flagged_mae": float(absolute[alarm].mean()) if alarm.any() else None,
                "unflagged_mae": float(absolute[~alarm].mean()) if (~alarm).any() else None,
            }
        )
    return pd.DataFrame(rows)


def width_error_correlation(predictions, prefix):
    width = (predictions[f"{prefix}_upper_mpa"] - predictions[f"{prefix}_lower_mpa"]).to_numpy()
    error = np.abs(predictions.actual_mpa - predictions.point_mpa).to_numpy()
    if not np.isfinite(width).all() or len(np.unique(np.round(width, 10))) < 2:
        return None
    if len(np.unique(error)) < 2:
        return None
    return float(spearmanr(width, error).statistic)


def summarize(table, keys, metrics):
    melted = table.melt(id_vars=keys, value_vars=metrics, var_name="metric", value_name="value")
    return (
        melted.groupby(keys + ["metric"], dropna=False)
        .value.agg(["count", "mean", "std", "min", "max"])
        .reset_index()
    )
