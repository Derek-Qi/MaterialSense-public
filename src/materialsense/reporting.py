"""Saved static figures and readable reports from measured results only."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def save_plots(predictions, ablation, output):
    actual, point = predictions.actual_mpa.to_numpy(), predictions.point_mpa.to_numpy()
    residual = actual - point
    plt.rcParams.update(
        {"figure.dpi": 140, "axes.spines.top": False, "axes.spines.right": False, "font.size": 10}
    )
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.8), layout="constrained")
    axes[0].scatter(actual, point, s=14, alpha=0.7, color="#167d9a")
    limits = [min(actual.min(), point.min()), max(actual.max(), point.max())]
    axes[0].plot(limits, limits, "--", color="grey")
    axes[0].set(xlabel="Measured strength (MPa)", ylabel="Predicted strength (MPa)")
    axes[1].scatter(point, residual, s=14, alpha=0.7, color="#167d9a")
    axes[1].axhline(0, ls="--", color="grey")
    axes[1].set(xlabel="Predicted strength (MPa)", ylabel="Measured - predicted (MPa)")
    axes[2].hist(residual, bins=20, color="#167d9a", edgecolor="white")
    axes[2].set(xlabel="Residual (MPa)", ylabel="Test observations")
    fig.suptitle("Unseen exact recipes: held-out diagnostics")
    fig.savefig(output / "residuals.png")
    plt.close(fig)

    shown = predictions.sort_values("point_mpa").iloc[:60]
    lo, hi = shown.cqr_lower_mpa.to_numpy(), shown.cqr_upper_mpa.to_numpy()
    fig, ax = plt.subplots(figsize=(10, 4), layout="constrained")
    if np.isfinite(lo).all() and np.isfinite(hi).all():
        ax.vlines(np.arange(len(shown)), lo, hi, alpha=0.5, color="#167d9a", label="Group-max CQR")
    ax.scatter(np.arange(len(shown)), shown.actual_mpa, s=12, color="#b44729", label="Measured")
    ax.set(
        xlabel="First 60 test observations sorted by point estimate",
        ylabel="Strength (MPa)",
        title="Intervals for held-out recipes (finite measured age sets)",
    )
    ax.legend()
    fig.savefig(output / "intervals.png")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4), layout="constrained")
    positions = np.arange(len(ablation))
    ax.bar(positions - 0.18, ablation.raw_cv_group_rmse, 0.36, label="Raw", color="#91b6c2")
    ax.bar(
        positions + 0.18,
        ablation.engineered_cv_group_rmse,
        0.36,
        label="Engineered",
        color="#167d9a",
    )
    ax.set_xticks(positions, ablation.model, rotation=10)
    ax.set(ylabel="Out-of-fold group-balanced RMSE (MPa)", title="Training-only feature ablation")
    ax.legend()
    fig.savefig(output / "ablation.png")
    plt.close(fig)


def write_report(metadata, metrics, intervals, output):
    selected = metadata["selected"]
    primary = metrics[
        (metrics.protocol == "grouped")
        & (metrics.model == selected["model"])
        & (metrics.features == selected["features"])
    ].iloc[0]
    lines = [
        "# MaterialSense measured experiment",
        "",
        f"Seed: {metadata['config']['seed']}. Data: {metadata['data_audit']['rows']} observations, "
        f"{metadata['data_audit']['recipes']} exact recipes.",
        "",
        f"Training-only grouped CV selected **{selected['model']} / {selected['features']}**.",
        f"Held-out grouped RMSE: **{primary.rmse:.3f} MPa**; MAE: **{primary.mae:.3f} MPa**; "
        f"R2: **{primary.r2:.4f}**; group-balanced RMSE: **{primary.group_rmse:.3f} MPa**.",
        "",
        "## Frozen candidate comparison",
        "",
        "| Protocol | Model | Features | RMSE (MPa) | MAE (MPa) | R2 | Group RMSE |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for row in metrics.itertuples():
        lines.append(
            f"| {row.protocol} | {row.model} | {row.features} | {row.rmse:.3f} | "
            f"{row.mae:.3f} | {row.r2:.4f} | {row.group_rmse:.3f} |"
        )
    lines += [
        "",
        "The random and grouped test sets differ. This comparison is descriptive; "
        "it is not a causal leakage effect estimate or a demonstrated method improvement.",
        "",
        "## Group-maximum calibrated intervals",
        "",
    ]
    for name, values in intervals.items():
        width = values["mean_width_mpa"]
        width_text = f"{width:.3f} MPa" if width is not None else "unbounded"
        lines.append(
            f"- {name}: row coverage {values['covered_rows']}/{values['n_rows']} "
            f"({values['row_coverage']:.1%}); whole-recipe coverage "
            f"{values['covered_recipes']}/{values['n_recipes']} "
            f"({values['whole_recipe_coverage']:.1%}); mean width {width_text}."
        )
    lines += [
        "",
        "Nominal level and exact denominators are in metadata.json. Guarantees require "
        "exchangeable recipe clusters, including their size and age measurement process. "
        "The historical compilation does not verify that assumption. CQR is a separate "
        "quantile model and does not necessarily contain the selected point estimate.",
        "",
        "OOD is a training-distance heuristic, not a coverage repair. Physical input ranges "
        "are screening heuristics. This is a public-data case study, not engineering validation.",
        "",
        "See docs/methodology.md for the complete protocol and limitations.",
    ]
    (output / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
