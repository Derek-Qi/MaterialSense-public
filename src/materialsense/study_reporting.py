"""Figures and a concise report generated entirely from saved study tables."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml


def write_study_report(output, tables):
    config = yaml.safe_load((output / "base_config.yaml").read_text(encoding="utf-8"))
    settings = yaml.safe_load((output / "study_config.yaml").read_text(encoding="utf-8"))
    nominal = 1 - config["alpha"]
    metrics = pd.read_csv(output / "selected_summary.csv")
    ablation = pd.read_csv(output / "ablation_summary.csv")
    intervals = pd.read_csv(output / "interval_summary.csv")
    lines = [
        "# Repeated MaterialSense benchmark",
        "",
        "Fixed seeds; training-only grouped CV selects each point predictor. Random-row results",
        "apply that seed's selected model specification to a different diagnostic test set.",
        "Mean +/- sample SD and min/max describe overlapping resplits, not independent replications",
        "or population confidence intervals. No test-based tuning is performed.",
        "",
        "## Selected-model test metrics",
        "",
        "| Protocol | Metric | Mean | Sample SD | Min | Max |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for r in metrics.itertuples():
        lines.append(
            f"| {r.protocol} | {r.metric} | {r.mean:.4f} | {r.std:.4f} | {r.min:.4f} | {r.max:.4f} |"
        )
    lines += [
        "",
        "## Fixed RandomForest incremental ablation",
        "",
        "These nested sets are not the legacy engineered set used in model selection.",
        "Same per-seed partition and frozen forest parameters. Negative paired deltas favor the new set.",
        "",
        "| Features | Group RMSE mean | Sample SD | Min | Max |",
        "|---|---:|---:|---:|---:|",
    ]
    for r in ablation[ablation.metric == "group_rmse"].itertuples():
        lines.append(f"| {r.features} | {r.mean:.4f} | {r.std:.4f} | {r.min:.4f} | {r.max:.4f} |")
    lines += [
        "",
        "## Group-maximum intervals",
        f"Nominal interval coverage: {nominal:.1%}.",
        "",
        "| Method | Metric | Mean | Sample SD | Min | Max |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for r in intervals.itertuples():
        lines.append(
            f"| {r.method} | {r.metric} | {r.mean:.4f} | {r.std:.4f} | {r.min:.4f} | {r.max:.4f} |"
        )
    lines += [
        "",
        "Residual interval widths are constant within each seed, so their width/error",
        "correlation is undefined. CQR width need not increase with error or novelty.",
        "",
        "## Error-risk alarms",
        "",
        f"risk_thresholds.csv evaluates absolute prediction error >{settings['high_error_mpa']:g} MPa, "
        "not a ground-truth",
        "OOD label. Thresholds are quantiles of training-only leave-self-out KNN distances.",
        "Undefined rates remain missing when denominators are zero. Statistical novelty and",
        "physical heuristic screening are separate; neither certifies engineering safety.",
        "",
        "## Failure inspection",
        "",
        "failures.csv contains the ten largest errors per seed, their actual inputs, intervals",
        "and novelty flags. All test predictions are retained in seed-*/reliability_predictions.csv.",
        "Permutation importance is a post-hoc held-out diagnostic in delta group-RMSE units.",
        "Correlated ingredient/ratio variables make individual importances non-causal.",
        "",
        "Exchangeability of historical recipe clusters, including group sizes and measured ages,",
        "is assumed rather than established. Exact recipes do not identify labs/batches or",
        "near-duplicate compositions. Continuous age curves and OOD coverage are not guaranteed.",
    ]
    (output / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    fig, axes = plt.subplots(1, 3, figsize=(14, 4), layout="constrained")
    chosen = tables["metrics"].loc[tables["metrics"].selected]
    for protocol, color in [("grouped", "#167d9a"), ("row_random_diagnostic", "#b44729")]:
        data = chosen.loc[chosen.protocol == protocol].sort_values("seed")
        axes[0].plot(data.seed, data.rmse, "o-", label=protocol, color=color)
    axes[0].set(xlabel="Prespecified seed", ylabel="Test RMSE (MPa)")
    axes[0].legend(fontsize=7)
    for name, group in tables["ablation"].groupby("features"):
        axes[1].scatter(np.repeat(name, len(group)), group.group_rmse, s=18, alpha=0.65)
    axes[1].tick_params(axis="x", rotation=25)
    axes[1].set(ylabel="Group-balanced RMSE (MPa)", title="Fixed forest, identical grouped splits")
    for method, group in tables["intervals"].groupby("method"):
        axes[2].scatter(group.mean_width_mpa, group.whole_recipe_coverage, label=method)
    axes[2].axhline(nominal, linestyle="--", color="grey")
    axes[2].set(xlabel="Mean interval width (MPa)", ylabel="Whole-recipe coverage")
    axes[2].legend()
    fig.savefig(output / "study_overview.png", dpi=150)
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), layout="constrained")
    risk = (
        tables["risk_thresholds"]
        .groupby("training_quantile")[["flagged_mae", "unflagged_mae", "precision", "recall"]]
        .mean()
    )
    risk[["flagged_mae", "unflagged_mae"]].plot(ax=axes[0], marker="o")
    axes[0].set(xlabel="Training distance quantile", ylabel="MAE (MPa)")
    risk[["precision", "recall"]].plot(ax=axes[1], marker="o")
    axes[1].set(
        xlabel="Training distance quantile", ylabel="Error-event detection rate", ylim=(0, 1)
    )
    fig.savefig(output / "risk_analysis.png", dpi=150)
    plt.close(fig)
