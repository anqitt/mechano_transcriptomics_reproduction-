"""Run the official TensionMap synthetic example and save compact outputs."""

import json
import os
import sys
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from skimage.io import imread


PROJECT_ROOT = Path(__file__).resolve().parent
TENSIONMAP_ROOT = PROJECT_ROOT / "TensionMap"
INPUT_PATH = TENSIONMAP_ROOT / "example_data" / "synthetic" / "test.tiff"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "stage3_synthetic"

sys.path.insert(0, str(TENSIONMAP_ROOT))
from src.VMSI import run_VMSI  # noqa: E402


def finite_summary(values):
    """Return compact finite-value checks for numeric data."""
    array = np.asarray(values, dtype=float)
    finite = np.isfinite(array)
    summary = {
        "shape": list(array.shape),
        "nan_count": int(np.isnan(array).sum()),
        "infinity_count": int(np.isinf(array).sum()),
        "finite_count": int(finite.sum()),
    }
    if finite.any():
        summary.update(
            minimum=float(array[finite].min()),
            maximum=float(array[finite].max()),
        )
    return summary


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    image = imread(INPUT_PATH)
    labels = np.unique(image)

    previous_directory = Path.cwd()
    os.chdir(OUTPUT_DIR)
    start = time.perf_counter()
    try:
        # This is the exact one-line call used by the official notebook.
        model = run_VMSI(image)
    finally:
        runtime_seconds = time.perf_counter() - start
        os.chdir(previous_directory)
        for optimizer_trace in (".init_opt.csv", ".theta_opt.csv", ".main_opt.csv"):
            (OUTPUT_DIR / optimizer_trace).unlink(missing_ok=True)

    results, adjacency = model.output_results(neighbours=True)
    tensions = pd.to_numeric(model.edges["tension"], errors="coerce")
    pressures = pd.to_numeric(results["pressure"], errors="coerce")
    stress_columns = [
        "stresstensor_eigval1",
        "stresstensor_eigval2",
        "stresstensor_orientation",
        "stresstensor_anisotropy",
    ]

    results.to_csv(OUTPUT_DIR / "cell_results.csv", index=True)
    adjacency.to_csv(OUTPUT_DIR / "adjacency_tension.csv", index=True)
    pd.DataFrame(
        {"edge_id": model.edges.index, "tension": tensions}
    ).to_csv(OUTPUT_DIR / "edge_tensions.csv", index=False)

    model.plot(
        ["tension"],
        line_thickness=5,
        size=25,
        file=OUTPUT_DIR / "tension.png",
    )
    plt.close("all")
    model.plot(
        ["pressure"], image, size=25, file=OUTPUT_DIR / "pressure.png"
    )
    plt.close("all")
    model.plot(
        ["stress", "cap"], size=25, file=OUTPUT_DIR / "stress.png"
    )
    plt.close("all")

    metadata = {
        "input_file": str(INPUT_PATH.relative_to(PROJECT_ROOT)),
        "image_shape": list(image.shape),
        "image_dtype": str(image.dtype),
        "unique_values": int(labels.size),
        "foreground_labels": int(np.count_nonzero(labels)),
        "runtime_seconds": runtime_seconds,
        "optimizer": "nlopt",
        "optimization_status": (
            "completed_without_exception; upstream run_VMSI does not expose "
            "NLopt termination codes"
        ),
        "analyzed_cells": int(len(model.involved_cells)),
        "result_dataframe_shape": list(results.shape),
        "adjacency_matrix_shape": list(adjacency.shape),
        "tension": finite_summary(tensions),
        "pressure": finite_summary(pressures),
        "stress": finite_summary(results[stress_columns]),
        "adjacency_tension": finite_summary(adjacency),
    }
    with open(OUTPUT_DIR / "run_summary.json", "w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2)

    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
