# Figure 5 gSEM Benchmark

## 1. Environment

- Environment: `figure5-gsem-repro`
- Local path: `.conda/figure5-gsem-repro` (ignored by Git)
- Platform: Intel macOS (`x86_64`, 64-bit)
- Package manager: micromamba 2.9.0 using conda-forge. The system Conda
  4.12 solver repeatedly stalled while reading repository metadata, so the
  official micromamba binary was used only as a compatible solver.
- Python: 3.9.12
- R: 4.2.1
- Reproducible specification: `figure5-gsem-environment.yml`

## 2. Core Dependencies

| Package | Authors' saved version | Installed | Load test |
|---|---:|---:|---|
| mgcv | 1.9-0 | 1.9-0 | PASS |
| nlme | 3.1-163 | 3.1-163 | PASS |
| foreach | 1.5.2 | 1.5.2 | PASS |
| doParallel | 1.0.17 | 1.0.17 | PASS |
| iterators | 1.0.14 | 1.0.14 | PASS |

No plotting, GO-enrichment, Bioconductor, scHOT, Figure 4 or Figure 6
packages were installed.

## 3. Data Alignment

The existing official dataset-2 files were used. `gex_res.csv` was extracted
from the already downloaded archive and passed its ZIP CRC test. No new
biological data were downloaded.

| Check | Result |
|---|---:|
| Expression cells | 912 |
| Mechanics cells | 912 |
| Matched cells, same order | 912 |
| Original genes | 29,452 |
| Genes nonzero in >50% of cells | 12,704 |

To avoid expanding the full 264 MB CSV through slow, memory-heavy base-R
parsing, `prepare_figure5_benchmark_data.py` streams every row, applies the
same strict `>0.5` filter, and retains the first 100 passing genes in their
original order. It does not transform values or reorder cell columns.

## 4. Official Preprocessing Reproduced

The benchmark uses the pinned upstream `helper_functions.R` from commit
`1a3ed8e940059d9e3574f21b67f340917f1bf049`. Its local copy differs at the
byte level only by a final newline.

For each gene and each mechanics metric, the official computation was kept:

1. `stresstensor_magnitude = stresstensor_eigval1 + stresstensor_eigval2`;
2. take the natural log of pressure or stress magnitude;
3. fit separate `mgcv::gam()` spatial smooths over `centroid_x` and
   `centroid_y` using `k=300`, `fx=TRUE`, and `method="REML"`;
4. subtract fitted spatial trends from expression and mechanics;
5. fit `lm(residual_expression ~ residual_mechanics)`;
6. retain slope (`beta`), t statistic and two-sided P value, then apply BH
   adjustment to the combined two-metric benchmark table.

No statistical formula or scientific parameter was substituted. Two workers
were used instead of the notebook's example value of eight because this host
has four physical cores and 8 GB RAM.

## 5. One-Gene Test

The deterministic first retained gene was **`Mrpl15`**.

- Cells: 912
- Metric: pressure
- Raw expression: mean 2.3285, SD 0.2037, range 1.3166–2.7739
- Raw pressure: mean 0.9585, SD 0.8389, range 0.0257–11.2879
- Log-pressure: mean -0.3338, SD 0.7934
- Spatial expression residual: mean approximately 0, SD 0.0984
- Spatial log-pressure residual: mean approximately 0, SD 0.5129
- Association beta: -0.0171985
- t statistic: -2.71454
- raw P value: 0.00676231
- Runtime: 31.197 seconds
- Result: SUCCESS

The residual means near zero are the expected numerical behavior after
subtracting the fitted spatial trends. No biological interpretation is made.

## 6. 10-Gene Benchmark

- Deterministic selection: first 10 genes after the official filter
- Metrics per gene: pressure and stress magnitude
- Successful gene fits: 10; failed: 0
- Output rows: 20
- Runtime: 66.893 seconds
- Average: 6.689 seconds per gene for both metrics
- Approximate R heap maximum observed: 166.7 MB

## 7. 50-Gene Benchmark

- Successful gene fits: 50; failed: 0
- Output rows: 100
- Runtime: 404.789 seconds (6 minutes 44.8 seconds)
- Average: 8.096 seconds per gene for both metrics
- Approximate R heap maximum observed: 161.1 MB

## 8. 100-Gene Benchmark

- Successful gene fits: 100; failed: 0
- Output rows: 200
- Runtime: 710.556 seconds (11 minutes 50.6 seconds)
- Average: 7.106 seconds per gene for both metrics
- Approximate R heap maximum observed: 163.5 MB

All tables contain `gene`, `metric`, `beta`, `stat`, `pval`, `padj`, and
`sign`. Both expected metric values occur, positive and negative directions
occur, and every numeric result is finite.

## 9. Runtime and Memory Projection

The 100-gene benchmark is the most stable basis for a linear projection:

| Scope | Projected runtime |
|---|---:|
| Pressure, 12,704 genes | about 12.54 hours |
| Stress magnitude, 12,704 genes | about 12.54 hours |
| Both metrics | about 25.08 hours |

This assumes similar per-gene cost and two workers. It is an engineering
projection, not a timed full run. The measured 164–167 MB is R heap usage for
the 100-gene subset and excludes all worker resident memory. With a streamed
12,704-gene matrix and two forked workers, a practical total of roughly
**1–3 GB** is expected; **2–4 GB of free memory** should be reserved. macOS
sandboxing prevented direct peak-RSS measurement, so this is deliberately
reported as an approximate range.

## 10. Compatibility Deviations

Requested and installed scientific package versions match the authors'
saved session. Conda-forge reports that several binary packages were built
under R 4.2.3 while they run under R 4.2.1. They loaded and completed all 320
benchmark fits without error; expected scientific impact is negligible, but
the build-version warning is retained here. The package solver differs
(micromamba rather than old Conda) and has no effect on model calculations.

## 11. Recommendation for Full Figure 5 Run

The **core full gSEM is feasible but operationally costly** on this machine.
Use at most two workers; one worker is safer if other applications are open.
Eight workers are not recommended with 8 GB RAM. The main risks are a
roughly day-long uninterrupted run, worker or laptop interruption, slow CSV
parsing, and loss of all progress because the official helper returns one
combined result only at completion.

For Step 5D, if explicitly authorized, prepare the full filtered matrix by
streaming, run the same official model in deterministic checkpointed chunks
with one or two workers, combine all chunks before a single BH adjustment,
and validate completeness. This benchmark does not authorize or start that
run, final Figure 5 panels, or GO enrichment.
