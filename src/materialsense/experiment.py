"""Auditable benchmark: grouped model selection, untouched calibration and test."""

import json
import platform
from datetime import UTC, datetime
from hashlib import sha256
from importlib.metadata import version
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import yaml
from sklearn.base import clone
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from .data import INPUTS, TARGET, recipe_ids, validate_frame
from .features import material_features
from .inference import predict_bundle
from .models import model_candidates, quantile_models
from .reporting import save_plots, write_report
from .safety import KNNWarning
from .splitting import group_cv, grouped_split, random_split, split_audit, validate_fractions
from .uncertainty import cqr_scores, finite_sample_quantile, group_max_scores, interval_metrics


def validate_config(config):
    validate_fractions([config["split"][k] for k in ["train", "calibration", "test"]])
    if not isinstance(config["seed"], int) or not 0 <= config["seed"] < 2**32 - 1:
        raise ValueError("seed must be an integer in [0, 2**32 - 2].")
    if not isinstance(config["cv_folds"], int) or config["cv_folds"] < 2:
        raise ValueError("At least two CV folds are required.")
    if not 0 < config["alpha"] < 1:
        raise ValueError("alpha must be in (0, 1).")
    ood = config["ood"]
    if (
        not isinstance(ood["neighbors"], int)
        or ood["neighbors"] < 1
        or not 0 < ood["threshold_quantile"] < 1
    ):
        raise ValueError("Invalid OOD neighbors or threshold quantile.")
    for key in ["total_mass_range", "water_binder_range"]:
        bounds = np.asarray(config["heuristics"][key], dtype=float)
        if bounds.shape != (2,) or not np.isfinite(bounds).all() or not 0 < bounds[0] < bounds[1]:
            raise ValueError(f"Invalid heuristic bounds: {key}")


def regression_metrics(y, prediction, groups):
    y, prediction = np.asarray(y), np.asarray(prediction)
    error = y - prediction
    errors = pd.DataFrame({"group": groups, "square": error**2, "absolute": np.abs(error)})
    per_group = errors.groupby("group")[["square", "absolute"]].mean()
    return {
        "rmse": float(np.sqrt(mean_squared_error(y, prediction))),
        "mae": float(mean_absolute_error(y, prediction)),
        "r2": float(r2_score(y, prediction)),
        "group_rmse": float(np.sqrt(per_group.square.mean())),
        "group_mae": float(per_group.absolute.mean()),
        "n_rows": len(y),
        "n_groups": len(per_group),
    }


def _save_assignments(groups, parts, output, filename):
    partitions = np.full(len(groups), "", dtype=object)
    for name, indexes in parts.items():
        partitions[indexes] = name
    pd.DataFrame(
        {"row_id": np.arange(len(groups)), "mix_id": groups, "partition": partitions}
    ).to_csv(output / filename, index=False)


def run_experiment(data, config, output_dir):
    validate_config(config)
    frame = validate_frame(data).reset_index(drop=True)
    groups = recipe_ids(frame)
    fractions = [config["split"][k] for k in ["train", "calibration", "test"]]
    parts = grouped_split(groups, config["seed"], fractions)
    train, calibration, test = (parts[k] for k in ["train", "calibration", "test"])
    folds = group_cv(groups[train], config["cv_folds"])
    if len(train) <= config["ood"]["neighbors"]:
        raise ValueError("Training partition must contain more rows than OOD neighbors.")
    if len(test) < 2:
        raise ValueError("At least two test observations are required for R2.")
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    y = frame[TARGET].to_numpy()
    candidates = model_candidates(config)
    features = {
        "raw": material_features(frame, False),
        "engineered": material_features(frame, True),
    }
    cv_rows, fold_rows, fitted = [], [], {}
    for feature_name, x in features.items():
        for name, candidate in candidates.items():
            oof = np.full(len(train), np.nan)
            for fold, (inner_train, valid) in enumerate(folds):
                estimator = clone(candidate).fit(x.iloc[train[inner_train]], y[train[inner_train]])
                prediction = estimator.predict(x.iloc[train[valid]])
                oof[valid] = prediction
                fold_rows.append(
                    {
                        "model": name,
                        "features": feature_name,
                        "fold": fold,
                        **regression_metrics(y[train[valid]], prediction, groups[train[valid]]),
                    }
                )
            if not np.isfinite(oof).all():
                raise RuntimeError("Incomplete or nonfinite out-of-fold predictions.")
            cv_rows.append(
                {
                    "model": name,
                    "features": feature_name,
                    **regression_metrics(y[train], oof, groups[train]),
                }
            )
            fitted[(name, feature_name)] = clone(candidate).fit(x.iloc[train], y[train])
    cv = pd.DataFrame(cv_rows).sort_values(["group_rmse", "model", "features"])
    winner = cv.iloc[0]
    selected = {
        "model": winner.model,
        "features": winner.features,
        "cv_group_rmse": float(winner.group_rmse),
    }
    point_model = fitted[(winner.model, winner.features)]
    cv.to_csv(output / "cv_metrics.csv", index=False)
    pd.DataFrame(fold_rows).to_csv(output / "cv_folds.csv", index=False)
    _save_assignments(groups, parts, output, "split_assignments.csv")
    # A separate diagnostic answers a different generalization question; no random-split selection.
    random_parts = random_split(len(frame), config["seed"], fractions)
    _save_assignments(groups, random_parts, output, "random_split_assignments.csv")
    metrics = []
    for protocol, split in [("grouped", parts), ("row_random_diagnostic", random_parts)]:
        for feature_name, x in features.items():
            for name, candidate in candidates.items():
                estimator = (
                    fitted[(name, feature_name)]
                    if protocol == "grouped"
                    else clone(candidate).fit(x.iloc[split["train"]], y[split["train"]])
                )
                prediction = estimator.predict(x.iloc[split["test"]])
                metrics.append(
                    {
                        "protocol": protocol,
                        "model": name,
                        "features": feature_name,
                        **regression_metrics(y[split["test"]], prediction, groups[split["test"]]),
                    }
                )
    metrics = pd.DataFrame(metrics)
    metrics.to_csv(output / "metrics.csv", index=False)
    ablation_rows = []
    for name in candidates:
        rows = cv[cv.model == name].set_index("features")
        raw, engineered = rows.loc["raw", "group_rmse"], rows.loc["engineered", "group_rmse"]
        ablation_rows.append(
            {
                "model": name,
                "raw_cv_group_rmse": raw,
                "engineered_cv_group_rmse": engineered,
                "engineered_minus_raw_mpa": engineered - raw,
            }
        )
    ablation = pd.DataFrame(ablation_rows)
    ablation.to_csv(output / "ablation.csv", index=False)

    calibration_point = point_model.predict(features[winner.features].iloc[calibration])
    residual_scores = np.abs(y[calibration] - calibration_point)
    residual_group_scores = group_max_scores(residual_scores, groups[calibration])
    residual_q = finite_sample_quantile(residual_group_scores, config["alpha"])
    quantiles = quantile_models(config)
    for estimator in quantiles:
        estimator.fit(features["engineered"].iloc[train], y[train])
    lower, upper = (m.predict(features["engineered"].iloc[calibration]) for m in quantiles)
    cqr_raw_scores = cqr_scores(y[calibration], lower, upper)
    cqr_group_scores = group_max_scores(cqr_raw_scores, groups[calibration])
    cqr_q = finite_sample_quantile(cqr_group_scores, config["alpha"])
    pd.DataFrame(
        {
            "row_id": calibration,
            "mix_id": groups[calibration],
            "residual_score": residual_scores,
            "cqr_score": cqr_raw_scores,
        }
    ).to_csv(output / "calibration_scores.csv", index=False)
    ood = KNNWarning(config["ood"]["neighbors"], config["ood"]["threshold_quantile"]).fit(
        frame.iloc[train][INPUTS].to_numpy()
    )
    bundle = {
        "point_model": point_model,
        "engineered": winner.features == "engineered",
        "quantile_models": quantiles,
        "residual_correction": residual_q,
        "cqr_correction": cqr_q,
        "ood": ood,
        "config": config,
        "selected": selected,
        "input_ranges": {
            column: [float(frame.iloc[train][column].min()), float(frame.iloc[train][column].max())]
            for column in INPUTS
        },
        "example": frame.iloc[train[0]][INPUTS].to_dict(),
    }
    prediction = predict_bundle(bundle, frame.iloc[test]).reset_index(drop=True)
    prediction.insert(0, "row_id", test)
    prediction.insert(1, "mix_id", groups[test])
    prediction.insert(2, "age", frame.iloc[test].age.to_numpy())
    prediction.insert(3, "actual_mpa", y[test])
    prediction["residual_mpa"] = y[test] - prediction.point_mpa
    prediction.to_csv(output / "test_predictions.csv", index=False)
    intervals = {
        name: interval_metrics(
            y[test],
            prediction[f"{prefix}_lower_mpa"],
            prediction[f"{prefix}_upper_mpa"],
            groups[test],
        )
        for name, prefix in [("group_max_residual", "residual"), ("group_max_cqr", "cqr")]
    }
    subgroup_rows = []
    for label, mask in [
        ("age_le_28", prediction.age <= 28),
        ("age_gt_28", prediction.age > 28),
        ("ood_warning", prediction.ood_warning),
        ("no_ood_warning", ~prediction.ood_warning),
    ]:
        if mask.any():
            subset = prediction.loc[mask]
            subgroup_rows.append(
                {
                    "subgroup": label,
                    **interval_metrics(
                        subset.actual_mpa, subset.cqr_lower_mpa, subset.cqr_upper_mpa, subset.mix_id
                    ),
                }
            )
    pd.DataFrame(subgroup_rows).to_csv(output / "coverage_subgroups.csv", index=False)
    # An age sensitivity probe, not a monotonicity constraint or a causal experiment.
    probe = frame.iloc[train].drop_duplicates(subset=INPUTS[:7]).head(30)
    age_grid = [
        v
        for v in [1, 3, 7, 14, 28, 56, 90, 180, 365]
        if frame.iloc[train].age.min() <= v <= frame.iloc[train].age.max()
    ]
    sweep = []
    for row_id, row in probe.iterrows():
        for age in age_grid:
            sample = row.to_frame().T.copy()
            sample.loc[:, "age"] = age
            value = point_model.predict(material_features(sample, bundle["engineered"]))[0]
            sweep.append({"training_row_id": row_id, "age": age, "prediction_mpa": value})
    sweep = pd.DataFrame(sweep, columns=["training_row_id", "age", "prediction_mpa"])
    sweep.to_csv(output / "age_sensitivity.csv", index=False)
    difference = sweep.groupby("training_row_id").prediction_mpa.diff().dropna()
    package_versions = {
        p: version(p)
        for p in [
            "numpy",
            "pandas",
            "scikit-learn",
            "scipy",
            "matplotlib",
            "streamlit",
            "joblib",
            "PyYAML",
            "xlrd",
        ]
    }
    source_files = sorted(Path(__file__).parent.glob("*.py"))
    source_hash = sha256(
        b"".join(p.name.encode() + p.read_bytes() for p in source_files)
    ).hexdigest()
    metadata = {
        "created_utc": datetime.now(UTC).isoformat(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "packages": package_versions,
        "config": config,
        "source_code_sha256": source_hash,
        "data_sha256_float64": sha256(frame.to_numpy(dtype="<f8").tobytes()).hexdigest(),
        "config_sha256": sha256(json.dumps(config, sort_keys=True).encode()).hexdigest(),
        "data_audit": {
            "rows": len(frame),
            "recipes": len(np.unique(groups)),
            "full_duplicate_rows_after_first": int(frame.duplicated().sum()),
            "grouping": "Exact first-seven float64; signed zero normalized; no rounding",
        },
        "split_audit": split_audit(groups, parts),
        "random_split_audit": split_audit(groups, random_parts),
        "selected": selected,
        "nominal_coverage": 1 - config["alpha"],
        "intervals": intervals,
        "calibration": {
            "n_groups": len(residual_group_scores),
            "aggregation": "maximum per recipe",
            "residual_correction_mpa": residual_q if np.isfinite(residual_q) else None,
            "cqr_correction_mpa": cqr_q if np.isfinite(cqr_q) else None,
        },
        "ood": {
            "threshold": ood.threshold_,
            "test_flagged_rows": int(prediction.ood_warning.sum()),
            "training_only": True,
            "self_neighbor_excluded": True,
        },
        "age_sensitivity": {
            "adjacent_comparisons": len(difference),
            "decreasing_predictions": int((difference < -1e-8).sum()),
        },
    }
    bundle["metadata"] = metadata
    joblib.dump(bundle, output / "model.joblib")
    (output / "metadata.json").write_text(
        json.dumps(metadata, indent=2, allow_nan=False), encoding="utf-8"
    )
    (output / "resolved_config.yaml").write_text(
        yaml.safe_dump(config, sort_keys=False), encoding="utf-8"
    )
    save_plots(prediction, ablation, output)
    write_report(metadata, metrics, intervals, output)
    return metadata
