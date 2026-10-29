"""Finite-sample group-maximum calibration and nonshrinking CQR."""

import math

import numpy as np
import pandas as pd


def finite_sample_quantile(scores, alpha: float) -> float:
    values = np.asarray(scores, dtype=float)
    if values.ndim != 1 or not len(values) or not np.isfinite(values).all():
        raise ValueError("Calibration scores must be a nonempty finite vector.")
    if not 0 < alpha < 1:
        raise ValueError("alpha must be strictly between zero and one.")
    rank = math.ceil((len(values) + 1) * (1 - alpha))
    return float(np.sort(values)[rank - 1]) if rank <= len(values) else float("inf")


def group_max_scores(scores, groups) -> np.ndarray:
    scores, groups = np.asarray(scores, dtype=float), np.asarray(groups)
    if scores.ndim != 1 or len(scores) != len(groups) or not len(scores):
        raise ValueError("Scores and recipe IDs must be aligned nonempty vectors.")
    if not np.isfinite(scores).all():
        raise ValueError("Calibration scores must be finite.")
    return pd.Series(scores).groupby(groups, sort=True).max().to_numpy()


def cqr_scores(y, lower, upper) -> np.ndarray:
    y, lower, upper = np.broadcast_arrays(y, lower, upper)
    lo, hi = np.minimum(lower, upper), np.maximum(lower, upper)
    return np.maximum.reduce([lo - y, y - hi, np.zeros_like(y)])


def cqr_interval(lower, upper, correction):
    return np.minimum(lower, upper) - correction, np.maximum(lower, upper) + correction


def interval_metrics(y, lower, upper, groups):
    y, lower, upper = np.asarray(y), np.asarray(lower), np.asarray(upper)
    covered = (lower <= y) & (y <= upper)
    group_covered = pd.Series(covered).groupby(np.asarray(groups)).all()
    width = upper - lower
    finite = bool(np.isfinite(width).all())
    return {
        "row_coverage": float(covered.mean()),
        "whole_recipe_coverage": float(group_covered.mean()),
        "covered_rows": int(covered.sum()),
        "n_rows": len(y),
        "covered_recipes": int(group_covered.sum()),
        "n_recipes": len(group_covered),
        "mean_width_mpa": float(width.mean()) if finite else None,
        "median_width_mpa": float(np.median(width)) if finite else None,
        "finite": finite,
    }
