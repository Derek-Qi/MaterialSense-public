"""Small fixed candidate set; all preprocessing stays inside fitted pipelines."""

from sklearn.dummy import DummyRegressor
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def model_candidates(config):
    return {
        "mean": DummyRegressor(strategy="mean"),
        "ridge": make_pipeline(StandardScaler(), Ridge(alpha=10.0)),
        "random_forest": RandomForestRegressor(
            random_state=config["seed"], n_jobs=1, **config["models"]["random_forest"]
        ),
        "gradient_boosting": GradientBoostingRegressor(
            random_state=config["seed"], **config["models"]["gradient_boosting"]
        ),
    }


def quantile_models(config):
    return tuple(
        GradientBoostingRegressor(
            loss="quantile",
            alpha=quantile,
            random_state=config["seed"],
            **config["models"]["gradient_boosting"],
        )
        for quantile in [config["alpha"] / 2, 1 - config["alpha"] / 2]
    )
