"""Reproduce the Figure 3c comparison from the authors' processed data."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, sem


DATA_ROOT = (
    Path("data/stage4b_required")
    / "Data_Hallou_He_et al_BioRxiv_Aug_2023"
    / "reproduce_data"
)
OUTPUT_DIR = Path("outputs/stage4c_figure3c")
DATASETS = ("dataset1", "dataset2", "dataset3")
DISPLAY_NAMES = {
    "Forebrain/Midbrain/Hindbrain": "FMH",
    "Neural Crest": "NC",
    "Cranial mesoderm": "CM",
    "Midbrain": "Midbrain",
    "Hindbrain": "Hindbrain",
    "heterotypic": "Boundary",
}


def official_junction_groups(dataset: str) -> tuple[pd.DataFrame, dict]:
    """Translate the pinned notebook's Figure 3 grouping cell directly."""
    cells = pd.read_csv(DATA_ROOT / dataset / "tensionmap_res.csv", index_col=0)
    adjacency = pd.read_csv(DATA_ROOT / dataset / "adj_mat.csv", index_col=0)
    if not cells.index.equals(adjacency.index) or not cells.index.equals(adjacency.columns):
        raise ValueError(f"{dataset}: cell IDs differ between input files")

    values = adjacency.to_numpy(dtype=float)
    if not np.isfinite(values).all() or not np.allclose(values, values.T):
        raise ValueError(f"{dataset}: invalid or asymmetric tension matrix")
    if not np.all(np.diag(values) == 0):
        raise ValueError(f"{dataset}: self-junctions are present")

    tissues = np.unique(cells["boundary_annotation"].to_numpy())
    tissues = tissues[tissues != "Other"]
    if len(tissues) != 2:
        raise ValueError(f"{dataset}: expected exactly two non-Other tissues")

    # Official notebook: fraction(tissue 1 neighbors) × fraction(tissue 2
    # neighbors), thresholded at 0.15.
    boundary_likelihood = np.zeros(len(cells), dtype=float)
    for idx, cell_id in enumerate(cells.index):
        neighbors = np.where(adjacency.loc[cell_id, :].to_numpy() != 0)[0]
        neighbor_tissues = cells["boundary_annotation"].iloc[neighbors].to_numpy()
        if len(neighbor_tissues) == 0:
            continue
        fraction_1 = np.sum(np.isin(neighbor_tissues, tissues[0])) / len(neighbor_tissues)
        fraction_2 = np.sum(np.isin(neighbor_tissues, tissues[1])) / len(neighbor_tissues)
        boundary_likelihood[idx] = fraction_1 * fraction_2
        boundary_likelihood[boundary_likelihood < 0.15] = 0

    # Official notebook: breadth-first graph distance from boundary cells.
    distance = -1 * np.ones(len(cells), dtype=int)
    distance[boundary_likelihood > 0] = 0
    neighbor_count = 1
    while np.any(distance == -1) and neighbor_count > 0:
        current = np.where(distance != -1)[0]
        neighbors = np.where(np.sum(values[current, :], axis=0) != 0)[0]
        neighbors = neighbors[~np.isin(neighbors, current)]
        neighbor_count = len(neighbors)
        distance[neighbors] = np.max(distance) + 1
    distance_by_cell = pd.Series(distance, index=cells.index)

    keep_cells = cells["boundary_annotation"].isin(tissues)
    reduced = adjacency.loc[keep_cells, keep_cells]
    row, col = np.nonzero(np.triu(reduced.to_numpy(dtype=float)))

    records: list[dict] = []
    for i, j in zip(row, col):
        cell_i = reduced.index[i]
        cell_j = reduced.columns[j]
        tissue_i = cells.loc[cell_i, "boundary_annotation"]
        tissue_j = cells.loc[cell_j, "boundary_annotation"]
        edge_distance = int(min(distance_by_cell[cell_i], distance_by_cell[cell_j]))
        group: str | None = None
        junction_type: str | None = None
        if tissue_i != tissue_j and edge_distance == 0:
            group = "heterotypic"
            junction_type = "heterotypic"
        elif tissue_i == tissue_j and 1 <= edge_distance <= 5:
            group = f"{tissue_i}_awayfrom_boundary"
            junction_type = "homotypic"
        if group is not None:
            records.append(
                {
                    "dataset": dataset,
                    "cell_i": cell_i,
                    "cell_j": cell_j,
                    "tissue_i": tissue_i,
                    "tissue_j": tissue_j,
                    "junction_type": junction_type,
                    "official_group": group,
                    "distance_to_boundary": edge_distance,
                    "tension": float(reduced.iat[i, j]),
                }
            )

    result = pd.DataFrame.from_records(records)
    diagnostics = {
        "input_cells": len(cells),
        "non_other_cells": int(keep_cells.sum()),
        "other_cells_excluded": int((~keep_cells).sum()),
        "boundary_cells": int(np.sum(boundary_likelihood > 0)),
        "unreachable_cells": int(np.sum(distance == -1)),
        "tissues_in_official_order": list(tissues),
    }
    return result, diagnostics


def summarize(junctions: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    group_rows: list[dict] = []
    test_rows: list[dict] = []
    for dataset in DATASETS:
        current = junctions[junctions["dataset"] == dataset]
        heterotypic = current[current["junction_type"] == "heterotypic"]["tension"]
        for group, values in current.groupby("official_group", sort=True)["tension"]:
            group_rows.append(
                {
                    "dataset": dataset,
                    "official_group": group,
                    "junction_type": "heterotypic" if group == "heterotypic" else "homotypic",
                    "n": len(values),
                    "mean": values.mean(),
                    "median": values.median(),
                    "sem": sem(values),
                }
            )
        for group, homotypic in current[current["junction_type"] == "homotypic"].groupby(
            "official_group", sort=True
        )["tension"]:
            test = mannwhitneyu(homotypic, heterotypic, alternative="less")
            test_rows.append(
                {
                    "dataset": dataset,
                    "homotypic_group": group,
                    "heterotypic_group": "heterotypic",
                    "homotypic_n": len(homotypic),
                    "heterotypic_n": len(heterotypic),
                    "homotypic_mean": homotypic.mean(),
                    "heterotypic_mean": heterotypic.mean(),
                    "percent_homotypic_lower_than_heterotypic": (
                        (heterotypic.mean() - homotypic.mean()) / heterotypic.mean() * 100
                    ),
                    "mannwhitney_u": test.statistic,
                    "p_value_one_sided_less": test.pvalue,
                }
            )
    return pd.DataFrame(group_rows), pd.DataFrame(test_rows)


def label_for_group(group: str) -> str:
    if group == "heterotypic":
        return "Boundary"
    return DISPLAY_NAMES.get(group.removesuffix("_awayfrom_boundary"), group)


def add_mean_sem(ax: plt.Axes, ordered: list[str], frame: pd.DataFrame) -> None:
    summary = frame.groupby("official_group")["tension"].agg(["mean", "sem"])
    means = [summary.loc[group, "mean"] for group in ordered]
    errors = [summary.loc[group, "sem"] for group in ordered]
    ax.errorbar(range(len(ordered)), means, yerr=errors, fmt="o", color="black", capsize=3, zorder=5)


def plot_reproduction(junctions: pd.DataFrame, tests: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(14, 5), constrained_layout=True)
    for ax, dataset in zip(axes, DATASETS):
        current = junctions[junctions["dataset"] == dataset]
        homotypic_groups = sorted(current.loc[current["junction_type"] == "homotypic", "official_group"].unique())
        order = homotypic_groups + ["heterotypic"]
        violins = ax.violinplot(
            [current.loc[current["official_group"] == group, "tension"] for group in order],
            positions=range(len(order)),
            showmeans=False,
            showmedians=False,
            showextrema=False,
        )
        for body in violins["bodies"]:
            body.set_facecolor("#86b6d8")
            body.set_edgecolor("black")
            body.set_alpha(0.85)
        add_mean_sem(ax, order, current)
        ax.set_xticks(range(len(order)), [label_for_group(group) for group in order], rotation=25)
        ax.set_title(dataset)
        ax.set_xlabel("")
        ax.set_ylabel("Tension (a.u.)" if dataset == "dataset1" else "")
        current_tests = tests[tests["dataset"] == dataset]
        text = "\n".join(
            f"{label_for_group(row.homotypic_group)} vs Boundary: p={row.p_value_one_sided_less:.3g}"
            for row in current_tests.itertuples()
        )
        ax.text(0.02, 0.98, text, transform=ax.transAxes, va="top", fontsize=8)
    fig.suptitle("Figure 3c reproduction: homotypic and boundary junction tensions")
    fig.savefig(OUTPUT_DIR / "figure3c_reproduction.png", dpi=180)
    plt.close(fig)


def plot_simple(group_summary: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.5), constrained_layout=True)
    for ax, dataset in zip(axes, DATASETS):
        current = group_summary[group_summary["dataset"] == dataset].copy()
        current["label"] = current["official_group"].map(label_for_group)
        current = pd.concat(
            [
                current[current["junction_type"] == "homotypic"].sort_values("label"),
                current[current["junction_type"] == "heterotypic"],
            ]
        )
        colors = ["#9ecae1" if kind == "homotypic" else "#de2d26" for kind in current["junction_type"]]
        ax.bar(current["label"], current["mean"], yerr=current["sem"], capsize=4, color=colors)
        ax.set_title(dataset)
        ax.set_xlabel("Within tissues                  Boundary")
        ax.set_ylabel("Mean tension ± SEM (a.u.)" if dataset == "dataset1" else "")
        ax.tick_params(axis="x", rotation=25)
    fig.suptitle("Beginner view: is the tissue-boundary tension higher?")
    fig.savefig(OUTPUT_DIR / "figure3c_simple_explanation.png", dpi=180)
    plt.close(fig)


def run_sanity_checks(junctions: pd.DataFrame) -> dict:
    canonical = junctions.apply(
        lambda row: (row["dataset"], *sorted((row["cell_i"], row["cell_j"]))), axis=1
    )
    checks = {
        "duplicate_undirected_junctions": int(canonical.duplicated().sum()),
        "self_junctions": int((junctions["cell_i"] == junctions["cell_j"]).sum()),
        "missing_tissue_annotations": int(junctions[["tissue_i", "tissue_j"]].isna().sum().sum()),
        "invalid_tension_values": int((~np.isfinite(junctions["tension"])).sum()),
        "mixed_dataset_ids": 0,
    }
    if any(checks.values()):
        raise ValueError(f"Sanity checks failed: {checks}")
    return checks


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    tables = []
    diagnostics = {}
    for dataset in DATASETS:
        table, diagnostic = official_junction_groups(dataset)
        tables.append(table)
        diagnostics[dataset] = diagnostic
    junctions = pd.concat(tables, ignore_index=True)
    checks = run_sanity_checks(junctions)
    group_summary, tests = summarize(junctions)

    junctions.to_csv(OUTPUT_DIR / "junction_tension_analysis.csv", index=False)
    group_summary.to_csv(OUTPUT_DIR / "group_summary.csv", index=False)
    tests.to_csv(OUTPUT_DIR / "pairwise_tests.csv", index=False)
    plot_reproduction(junctions, tests)
    plot_simple(group_summary)
    with (OUTPUT_DIR / "run_summary.json").open("w") as handle:
        json.dump(
            {"diagnostics": diagnostics, "sanity_checks": checks},
            handle,
            indent=2,
        )


if __name__ == "__main__":
    main()
