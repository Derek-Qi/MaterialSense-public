"""Heuristic novelty and input screening, with training-only fitted state."""

import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

from .data import MATERIALS, validate_frame


class KNNWarning:
    def __init__(self, neighbors=5, threshold_quantile=0.95):
        self.neighbors = neighbors
        self.threshold_quantile = threshold_quantile

    def fit(self, x):
        x = np.asarray(x, dtype=float)
        if (
            x.ndim != 2
            or not np.isfinite(x).all()
            or not isinstance(self.neighbors, int)
            or not 1 <= self.neighbors < len(x)
            or not 0 < self.threshold_quantile < 1
        ):
            raise ValueError("KNN requires finite 2D data, 1 <= k < n_train and 0 < quantile < 1.")
        self.scaler_ = StandardScaler().fit(x)
        scaled = self.scaler_.transform(x)
        self.neighbors_ = NearestNeighbors().fit(scaled)
        # One removed zero is the observation itself. Other identical observations remain.
        distances = self.neighbors_.kneighbors(scaled, n_neighbors=self.neighbors + 1)[0][:, 1:]
        self.training_distances_ = distances.mean(axis=1)
        self.threshold_ = float(np.quantile(self.training_distances_, self.threshold_quantile))
        return self

    def predict(self, x):
        scaled = self.scaler_.transform(np.asarray(x, dtype=float))
        distances = self.neighbors_.kneighbors(scaled, n_neighbors=self.neighbors)[0].mean(axis=1)
        return distances, distances > self.threshold_


def physical_warnings(frame, total_mass_range=(2100, 2550), water_binder_range=(0.2, 0.8)):
    x = validate_frame(frame, require_target=False)
    total = x[MATERIALS].sum(axis=1)
    ratio = x.water / x[["cement", "slag", "fly_ash"]].sum(axis=1)
    warnings = []
    if ((total < total_mass_range[0]) | (total > total_mass_range[1])).any():
        warnings.append(
            f"Total ingredient mass is outside the heuristic range {total_mass_range} kg/m3."
        )
    if ((ratio < water_binder_range[0]) | (ratio > water_binder_range[1])).any():
        warnings.append(f"Water/binder is outside the heuristic range {water_binder_range}.")
    return warnings
