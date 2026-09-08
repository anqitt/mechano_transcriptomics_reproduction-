"""Inspect the six processed Figure 3c inputs without reproducing Figure 3c."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np
import pandas as pd


DATA_ROOT = (
    Path("data/stage4b_required")
    / "Data_Hallou_He_et al_BioRxiv_Aug_2023"
    / "reproduce_data"
)
OUTPUT_DIR = Path("outputs/stage4b_real_data")
DATASETS = ("dataset1", "dataset2", "dataset3")


def load_dataset(name: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    cells = pd.read_csv(DATA_ROOT / name / "tensionmap_res.csv", index_col=0)
    tensions = pd.read_csv(DATA_ROOT / name / "adj_mat.csv", index_col=0)
    # Preserve and verify the authors' shared cell-ID order rather than remapping it.
    if not cells.index.equals(tensions.index) or not cells.index.equals(tensions.columns):
        raise ValueError(f"{name}: cell IDs or their order differ between the two files")
    values = tensions.to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise ValueError(f"{name}: adjacency/tension matrix contains NaN or infinity")
    if not np.allclose(values, values.T) or not np.all(np.diag(values) == 0):
        raise ValueError(f"{name}: matrix is not symmetric with a zero diagonal")
    return cells, tensions


def edges_from_matrix(tensions: pd.DataFrame) -> pd.DataFrame:
    values = tensions.to_numpy(dtype=float)
    row, col = np.where(np.triu(values, k=1) != 0)
    return pd.DataFrame(
        {
            "cell_a": tensions.index[row],
            "cell_b": tensions.columns[col],
            "tension": values[row, col],
        }
    )


def segments_for_edges(cells: pd.DataFrame, edges: pd.DataFrame) -> np.ndarray:
    xy = cells[["centroid_x", "centroid_y"]]
    return np.asarray(
        [
            [xy.loc[a].to_numpy(), xy.loc[b].to_numpy()]
            for a, b in edges[["cell_a", "cell_b"]].itertuples(index=False)
        ],
        dtype=float,
    )


def finish_axis(ax: plt.Axes, title: str) -> None:
    ax.set_title(title)
    ax.set_aspect("equal")
    ax.invert_yaxis()
    ax.set_xlabel("centroid_x (pixels)")
    ax.set_ylabel("centroid_y (pixels)")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    loaded = {name: load_dataset(name) for name in DATASETS}
    summaries: dict[str, dict] = {}

    # Cells colored by the tissue-compartment annotation used by Figure 3 code.
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), constrained_layout=True)
    for ax, (name, (cells, tensions)) in zip(axes, loaded.items()):
        annotations = cells["boundary_annotation"].fillna("Missing").astype(str)
        categories = sorted(annotations.unique())
        palette = plt.get_cmap("tab10")
        for idx, category in enumerate(categories):
            selected = annotations == category
            ax.scatter(
                cells.loc[selected, "centroid_x"],
                cells.loc[selected, "centroid_y"],
                s=8,
                alpha=0.8,
                color=palette(idx % 10),
                label=category,
            )
        ax.legend(fontsize=6, markerscale=1.7, frameon=False)
        finish_axis(ax, name)
    fig.suptitle("E8.5 embryo brain cells colored by boundary_annotation")
    fig.savefig(OUTPUT_DIR / "real_embryo_cells.png", dpi=180)
    plt.close(fig)

    # Network topology only: every nonzero upper-triangle entry is one junction.
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), constrained_layout=True)
    for ax, (name, (cells, tensions)) in zip(axes, loaded.items()):
        edges = edges_from_matrix(tensions)
        segments = segments_for_edges(cells, edges)
        ax.add_collection(LineCollection(segments, colors="0.55", linewidths=0.35, alpha=0.6))
        ax.scatter(cells["centroid_x"], cells["centroid_y"], s=3, color="black")
        ax.autoscale()
        finish_axis(ax, f"{name}: {len(edges):,} junctions")
    fig.suptitle("Cell-centroid junction network (nonzero adj_mat entries)")
    fig.savefig(OUTPUT_DIR / "real_embryo_junctions.png", dpi=180)
    plt.close(fig)

    # Raw/precomputed edge tensions mapped onto the same centroid network.
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), constrained_layout=True)
    for ax, (name, (cells, tensions)) in zip(axes, loaded.items()):
        edges = edges_from_matrix(tensions)
        segments = segments_for_edges(cells, edges)
        collection = LineCollection(
            segments,
            array=edges["tension"].to_numpy(),
            cmap="viridis",
            linewidths=0.7,
        )
        ax.add_collection(collection)
        ax.scatter(cells["centroid_x"], cells["centroid_y"], s=2, color="black", alpha=0.35)
        ax.autoscale()
        fig.colorbar(collection, ax=ax, shrink=0.72, label="precomputed tension")
        finish_axis(ax, name)
    fig.suptitle("Sanity-check preview of precomputed junction tensions")
    fig.savefig(OUTPUT_DIR / "real_embryo_tension_preview.png", dpi=180)
    plt.close(fig)

    for name, (cells, tensions) in loaded.items():
        edges = edges_from_matrix(tensions)
        first_edge = edges.iloc[0]
        first_cell = cells.iloc[0]
        summaries[name] = {
            "cell_table_shape": list(cells.shape),
            "matrix_shape": list(tensions.shape),
            "ids_match_exactly": bool(
                cells.index.equals(tensions.index) and cells.index.equals(tensions.columns)
            ),
            "cell_columns": list(cells.columns),
            "boundary_annotation_values": sorted(
                cells["boundary_annotation"].dropna().astype(str).unique().tolist()
            ),
            "nonzero_undirected_junctions": int(len(edges)),
            "pressure_present": "pressure" in cells.columns,
            "representative_cell": {
                "cell_id": str(cells.index[0]),
                "centroid_x": float(first_cell["centroid_x"]),
                "centroid_y": float(first_cell["centroid_y"]),
                "boundary_annotation": str(first_cell["boundary_annotation"]),
                "celltype": str(first_cell["celltype"]),
                "pressure": float(first_cell["pressure"]),
            },
            "representative_junction": {
                "cell_a": str(first_edge["cell_a"]),
                "cell_b": str(first_edge["cell_b"]),
                "tension": float(first_edge["tension"]),
            },
        }

    (OUTPUT_DIR / "inspection_summary.json").write_text(
        json.dumps(summaries, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
