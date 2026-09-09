#!/usr/bin/env python3
"""Stream the official expression CSV and retain the first 100 filtered genes."""

import csv
import sys
import time
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit("Usage: prepare_figure5_benchmark_data.py GEX_CSV OUTPUT_CSV AUDIT_CSV")

    source = Path(sys.argv[1])
    output = Path(sys.argv[2])
    audit = Path(sys.argv[3])
    output.parent.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    total_genes = 0
    filtered_genes = 0
    retained_rows = []

    with source.open(newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        cell_count = len(header) - 1
        for row in reader:
            total_genes += 1
            nonzero = sum(float(value) > 0 for value in row[1:])
            if nonzero / cell_count > 0.5:
                filtered_genes += 1
                if len(retained_rows) < 100:
                    retained_rows.append(row)

    with output.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(retained_rows)

    with audit.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["measure", "value"])
        writer.writerows(
            [
                ("expression_cells", cell_count),
                ("expression_genes", total_genes),
                ("filtered_genes", filtered_genes),
                ("retained_benchmark_genes", len(retained_rows)),
                ("stream_filter_seconds", time.perf_counter() - started),
            ]
        )


if __name__ == "__main__":
    main()
