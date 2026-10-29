from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml


@pytest.fixture
def tiny_config():
    root = Path(__file__).resolve().parents[1]
    config = yaml.safe_load((root / "configs/experiment.yaml").read_text())
    config["cv_folds"] = 3
    config["models"]["random_forest"]["n_estimators"] = 8
    config["models"]["gradient_boosting"]["n_estimators"] = 8
    return config


@pytest.fixture
def concrete_frame():
    """Independent synthetic recipes with three ages; no external data needed."""
    rng = np.random.default_rng(7)
    rows = []
    for _ in range(60):
        cement = rng.uniform(200, 450)
        slag, fly = rng.uniform(0, 120, 2)
        water = rng.uniform(140, 220)
        for age in [7, 28, 90]:
            strength = 12 + 0.04 * cement - 0.03 * water + 5 * np.log1p(age)
            rows.append([cement, slag, fly, water, 4, 950, 750, age, strength])
    return pd.DataFrame(
        rows,
        columns=[
            "cement",
            "slag",
            "fly_ash",
            "water",
            "superplasticizer",
            "coarse_aggregate",
            "fine_aggregate",
            "age",
            "strength",
        ],
    )
