"""Repeated evaluation with prespecified seeds, fixed ablations and saved evidence."""

import json
from copy import deepcopy
from hashlib import sha256
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import yaml
from sklearn.base import clone
from sklearn.inspection import permutation_importance

from .data import INPUTS, TARGET, recipe_ids, validate_frame
from .diagnostics import partition_audit, risk_table, summarize, width_error_correlation
from .experiment import regression_metrics, run_experiment, validate_config
from .models import model_candidates
from .splitting import grouped_split, random_split
from .study_features import FEATURE_SETS, feature_set
from .study_reporting import write_study_report
from .uncertainty import group_max_scores

METRICS = ["mae", "rmse", "r2", "group_rmse"]


def validate_study(settings):
    seeds = settings["seeds"]
    if (
        not isinstance(seeds, list)
        or not seeds
        or len(set(seeds)) != len(seeds)
        or any(type(s) is not int or not 0 <= s < 2**32 - 1 for s in seeds)
    ):
        raise ValueError("Study seeds must be unique nonnegative integers below 2**32 - 1.")
    quantiles = settings["ood_quantiles"]
    if not quantiles or any(not np.isfinite(q) or not 0 < q < 1 for q in quantiles):
        raise ValueError("OOD quantiles must lie strictly between zero and one.")
    if not np.isfinite(settings["high_error_mpa"]) or settings["high_error_mpa"] <= 0:
        raise ValueError("high_error_mpa must be finite and positive.")
    if type(settings["permutation_repeats"]) is not int or settings["permutation_repeats"] < 1:
        raise ValueError("permutation_repeats must be a positive integer.")


def run_study(data, config, settings, output_dir):
    validate_config(config)
    validate_study(settings)
    frame = validate_frame(data).reset_index(drop=True)
    groups = recipe_ids(frame)
    fractions = [config["split"][k] for k in ["train", "calibration", "test"]]
    output = Path(output_dir)
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"Study output is nonempty: {output}. Use a new output directory.")
    output.mkdir(parents=True, exist_ok=True)
    (output / "study_config.yaml").write_text(yaml.safe_dump(settings), encoding="utf-8")
    (output / "base_config.yaml").write_text(yaml.safe_dump(config), encoding="utf-8")
    rows = {
        key: []
        for key in [
            "metrics",
            "ablation",
            "intervals",
            "risk_thresholds",
            "split_audit",
            "permutation",
            "failures",
        ]
    }
    for seed in settings["seeds"]:
        current = deepcopy(config)
        current["seed"] = seed
        run_dir = output / f"seed-{seed}"
        print(f"Running prespecified seed {seed}", flush=True)
        metadata = run_experiment(frame, current, run_dir)
        parts = grouped_split(groups, seed, fractions)
        random_parts = random_split(len(frame), seed, fractions)
        for protocol, split in [("grouped", parts), ("row_random_diagnostic", random_parts)]:
            rows["split_audit"].extend(
                {"seed": seed, "protocol": protocol, **v} for v in partition_audit(frame, split)
            )
        metrics = pd.read_csv(run_dir / "metrics.csv")
        metrics["seed"] = seed
        selected = metadata["selected"]
        metrics["selected"] = (metrics.model == selected["model"]) & (
            metrics.features == selected["features"]
        )
        rows["metrics"].extend(metrics.to_dict("records"))
        train, test = parts["train"], parts["test"]
        y = frame[TARGET].to_numpy()
        for name in FEATURE_SETS:
            x = feature_set(frame, name)
            model = clone(model_candidates(current)["random_forest"]).fit(x.iloc[train], y[train])
            prediction = model.predict(x.iloc[test])
            rows["ablation"].append(
                {
                    "seed": seed,
                    "model": "random_forest",
                    "features": name,
                    **regression_metrics(y[test], prediction, groups[test]),
                }
            )
            pd.DataFrame(
                {
                    "row_id": test,
                    "mix_id": groups[test],
                    "actual_mpa": y[test],
                    "point_mpa": prediction,
                }
            ).to_csv(run_dir / f"ablation_predictions_{name}.csv", index=False)
            if name == "total_mass":

                def group_score(estimator, xx, yy):
                    return -regression_metrics(yy, estimator.predict(xx), groups[test])[
                        "group_rmse"
                    ]

                importance = permutation_importance(
                    model,
                    x.iloc[test],
                    y[test],
                    scoring=group_score,
                    n_jobs=1,
                    n_repeats=settings["permutation_repeats"],
                    random_state=seed,
                )
                for index, feature in enumerate(x.columns):
                    for repeat, value in enumerate(importance.importances[index]):
                        rows["permutation"].append(
                            {
                                "seed": seed,
                                "feature": feature,
                                "repeat": repeat,
                                "delta_group_rmse": value,
                            }
                        )
        pred = pd.read_csv(run_dir / "test_predictions.csv", float_precision="round_trip")
        bundle = joblib.load(run_dir / "model.joblib")
        risk = risk_table(
            pred,
            bundle["ood"].training_distances_,
            settings["ood_quantiles"],
            settings["high_error_mpa"],
        )
        rows["risk_thresholds"].extend({"seed": seed, **v} for v in risk.to_dict("records"))
        for interval, values in metadata["intervals"].items():
            prefix = "cqr" if interval.endswith("cqr") else "residual"
            rows["intervals"].append(
                {
                    "seed": seed,
                    "method": prefix,
                    **values,
                    "width_error_spearman": width_error_correlation(pred, prefix),
                }
            )
        scores = pd.read_csv(run_dir / "calibration_scores.csv", float_precision="round_trip")
        grouped = pd.DataFrame(
            {
                "mix_id": sorted(scores.mix_id.unique()),
                "residual_score": group_max_scores(scores.residual_score, scores.mix_id),
                "cqr_score": group_max_scores(scores.cqr_score, scores.mix_id),
            }
        )
        grouped.to_csv(run_dir / "calibration_group_scores.csv", index=False)
        pred["absolute_error_mpa"] = abs(pred.actual_mpa - pred.point_mpa)
        for prefix in ["cqr", "residual"]:
            pred[f"{prefix}_width_mpa"] = pred[f"{prefix}_upper_mpa"] - pred[f"{prefix}_lower_mpa"]
            pred[f"{prefix}_covered"] = (pred[f"{prefix}_lower_mpa"] <= pred.actual_mpa) & (
                pred.actual_mpa <= pred[f"{prefix}_upper_mpa"]
            )
        pred.to_csv(run_dir / "reliability_predictions.csv", index=False)
        worst = pred.nlargest(10, "absolute_error_mpa").copy()
        for column in INPUTS:
            worst[column] = frame.iloc[worst.row_id][column].to_numpy()
        rows["failures"].extend({"seed": seed, **v} for v in worst.to_dict("records"))
        print(f"Completed seed {seed}: {selected['model']} / {selected['features']}", flush=True)
    tables = {name: pd.DataFrame(values) for name, values in rows.items()}
    for name, table in tables.items():
        table.to_csv(output / f"{name}.csv", index=False)
    summarize(tables["metrics"], ["protocol", "model", "features"], METRICS).to_csv(
        output / "metric_summary.csv", index=False
    )
    chosen = tables["metrics"].loc[tables["metrics"].selected]
    summarize(chosen, ["protocol"], METRICS).to_csv(output / "selected_summary.csv", index=False)
    summarize(tables["ablation"], ["features"], METRICS).to_csv(
        output / "ablation_summary.csv", index=False
    )
    paired = tables["ablation"].pivot(index="seed", columns="features", values="group_rmse")
    paired = paired.subtract(paired["raw"], axis=0).reset_index()
    paired.to_csv(output / "paired_ablation.csv", index=False)
    summarize(
        tables["intervals"],
        ["method"],
        ["row_coverage", "whole_recipe_coverage", "mean_width_mpa", "width_error_spearman"],
    ).to_csv(output / "interval_summary.csv", index=False)
    summarize(
        tables["risk_thresholds"],
        ["training_quantile"],
        [
            "precision",
            "recall",
            "false_positive_rate",
            "false_negative_rate",
            "flagged_mae",
            "unflagged_mae",
        ],
    ).to_csv(output / "risk_summary.csv", index=False)
    manifest = {
        "status": "complete",
        "seeds": settings["seeds"],
        "settings": settings,
        "source_code_sha256": metadata["source_code_sha256"],
        "data_sha256_float64": metadata["data_sha256_float64"],
        "packages": metadata["packages"],
        "python": metadata["python"],
        "platform": metadata["platform"],
        "settings_sha256": sha256(json.dumps(settings, sort_keys=True).encode()).hexdigest(),
        "base_config_sha256": sha256(json.dumps(config, sort_keys=True).encode()).hexdigest(),
        "interpretation": "Descriptive resplit variation; overlapping test sets; no independent CI.",
    }
    write_study_report(output, tables)
    manifest["file_sha256"] = {
        str(p.relative_to(output)).replace("\\", "/"): sha256(p.read_bytes()).hexdigest()
        for p in sorted(output.rglob("*"))
        if p.is_file()
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, allow_nan=False), encoding="utf-8"
    )
    return manifest
