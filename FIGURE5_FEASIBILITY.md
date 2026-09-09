# Figure 5 Feasibility Audit

## Audit scope and evidence

This audit did not fit a model or reproduce a Figure 5 panel. It uses:

- the [published article and Methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC11978512/);
- the official upstream TensionMap repository at commit
  `1a3ed8e940059d9e3574f21b67f340917f1bf049`;
- `notebooks/05_spatial_regression.ipynb` and
  `notebooks/helper_functions.R` from that commit;
- the authors' saved notebook outputs and `sessionInfo()`;
- the official Zenodo archive already present locally.

The word **official** below means directly specified by the paper or pinned
code. Runtime and memory projections are labeled as estimates.

## 1. Figure 5 Biological Question

Figure 5 asks: **which genes have expression levels associated with a cell's
inferred mechanical state after removing spatial trends shared by expression
and mechanics?**

This matters because neighboring cells and cells in the same tissue region
often resemble one another in both gene expression and mechanics. A naive
correlation can therefore identify tissue location rather than a direct
gene–mechanics relationship. The authors use a geoadditive structural equation
model (gSEM) to regress broad two-dimensional spatial patterns out of both
variables before testing their remaining association.

The main Figure 5 panels use **dataset 2**, the E8.5 embryo-2 region containing
cranial mesoderm (CM) and forebrain/midbrain/hindbrain (FMH). The notebook is
generic across datasets, but its checked-in demonstration currently sets
`dataset <- 'dataset3'`. That saved demonstration output is not the published
dataset-2 Figure 5 result.

## 2. Panel-by-Panel Map

| Panel | Plot and biological question | Input | Computational step and output | Mechanics variable | Expression | Dataset | Official code |
|---|---|---|---|---|---|---|---|
| 5a | Pressure volcano plot plus example residual-regression plots. Which genes remain positively or negatively associated with pressure after spatial correction? | `gex_res.csv`; cell IDs, centroids and pressure from `tensionmap_res.csv` | gSEM per gene; BH-adjusted P value versus `beta`; example `r_gene ~ r_pressure` plots | Intracellular pressure | Normalized, log-transformed, imputed single-cell expression supplied in `gex_res.csv`; genes nonzero in >50% of cells | dataset 2 | `05_spatial_regression.ipynb`, cells 6–19; `do_gsem_regression()` and `parallel_gsem_regression()` in `helper_functions.R` |
| 5b | GO terms for genes associated positively and negatively with pressure. Which biological processes are represented? | Significant pressure-associated gene sets plus mouse GO annotation and tested-gene background | `clusterProfiler::enrichGO()` and ranked bar plots | Pressure association sign | Gene symbols from the Figure 5a tests | dataset 2 | Notebook cells 20–22 provide the GO workflow; see discrepancy below |
| 5c | Stress volcano plot plus example residual-regression plots. Which genes remain associated with cellular stress magnitude after spatial correction? | `gex_res.csv`; centroids and stress eigenvalues from `tensionmap_res.csv` | Compute magnitude, run gSEM per gene, BH correction, volcano and example residual plots | Stress-tensor magnitude, defined in code as `eigval1 + eigval2` | Same matrix and >50% filter as 5a | dataset 2 | Notebook cells 7, 9, 12, 14, 17 and 19; helper R functions |
| 5d | GO terms for genes associated positively and negatively with stress magnitude. Which processes are represented? | Significant stress-associated gene sets, mouse GO annotation and background | `enrichGO()` and bar plots | Stress-tensor magnitude | Gene symbols from Figure 5c tests | dataset 2 | Notebook cells 20–22 provide the GO workflow; see discrepancy below |
| 5e | Spatial expression maps of selected pressure-associated genes highlighted in 5a. Where are representative associations located in the embryo section? | Selected gene-expression rows and cell centroids | Map expression at each cell position | Pressure was used to select the genes; the panel itself maps expression | Same `gex_res.csv` | dataset 2 | No exact Figure 5e plotting cell was found in `05_spatial_regression.ipynb` or another pinned public notebook |

### Code-to-paper discrepancies that must be preserved in the audit

1. The notebook defaults to dataset 3, while the main paper panel uses dataset
   2.
2. The notebook randomly samples 100 expressed genes with seed 11235. It says
   to use `expressed_genes` for the full analysis.
3. The demonstration volcano/GO threshold is adjusted P < 0.1. The notebook
   explicitly says the full analysis uses 0.05.
4. Published panels 5b and 5d separate positively and negatively associated
   genes. The public notebook's displayed `enrichGO()` cells combine all
   significant genes for each metric and use the 100-gene demonstration
   universe. Exact sign-separated publication code is not present there.
5. No exact cell generating published panel 5e was found. The underlying
   expression and centroid data are available, but generating a replacement
   would require an explicitly documented reconstruction rather than claiming
   it is an official plotting cell.

## 3. Data Flow

```text
Official processed dataset 2
  reproduce_data/dataset2/gex_res.csv
    rows = genes; columns = cell_* IDs
  reproduce_data/dataset2/tensionmap_res.csv
    rows = the same cell_* IDs
    columns include centroid_x, centroid_y, pressure,
    stresstensor_eigval1 and stresstensor_eigval2
                          |
                          v
05_spatial_regression.ipynb, cell 6
  R read.table(..., row.names = 1)
                          |
                          v
cell-ID matching in helper_functions.R
  gex_res[gene, rownames(tensionmap_res-derived data_df)]
  then transpose to align expression with mechanics-row order
                          |
                          v
notebook cell 7
  stresstensor_magnitude = eigval1 + eigval2
                          |
                          v
notebook cell 9
  keep genes with expression > 0 in more than 50% of cells
  dataset 2: 12,704 of 29,452 genes
                          |
                          v
helper_functions.R: do_gsem_regression()
  log-transform one mechanical variable
  fit a 2D spatial GAM separately to mechanics and expression
  subtract fitted spatial trends
  regress expression residual on mechanics residual
                          |
                          v
helper_functions.R: parallel_gsem_regression()
  repeat for pressure and stress magnitude for every selected gene
  return gene, metric, beta, raw P value and t statistic
                          |
                          v
notebook cell 14
  BH-adjust all returned P values
                          |
                          v
Figure 5
  5a/5c: volcano and example residual regressions
  5b/5d: GO enrichment
  5e: selected spatial expression maps
```

No adjacency matrix, junction-tension matrix, segmentation image or new VMSI
run is needed for Figure 5.

## 4. Required Files

### Minimal dataset-2 input

| File | Biological meaning and structure | Dimensions / size | Panels | Available locally | In downloaded archive | Additional download |
|---|---|---|---|---|---|---|
| `reproduce_data/dataset2/gex_res.csv` | Processed normalized/log-transformed and imputed expression; genes × cells; row names are gene symbols and columns are `cell_*` IDs | 29,452 × 912; 276,590,951 B uncompressed; 86,896,935 B compressed | 5a–5e | **YES, inside the local archive; not extracted** at `data/stage4b_download/Data_Hallou_He_et al_BioRxiv_Aug_2023.zip` | YES | NO |
| `reproduce_data/dataset2/tensionmap_res.csv` | One row per mechanics cell; centroid, pressure, two stress eigenvalues, morphology and tissue/cell annotations | 912 × 25; 355,720 B | 5a, 5c, 5e; supplies IDs/coordinates throughout | **YES, extracted** at `data/stage4b_required/Data_Hallou_He_et al_BioRxiv_Aug_2023/reproduce_data/dataset2/tensionmap_res.csv` | YES | NO |

The `celltype` and `boundary_annotation` fields are present in
`tensionmap_res.csv`, but the official gSEM functions do not use them as
covariates or filters. They are therefore metadata, not additional required
files.

### Execution and annotation assets

| Asset | Role | Availability for audit | Needed for core association | Additional download |
|---|---|---|---|---|
| `notebooks/05_spatial_regression.ipynb` | Reads data, filters genes, calls models, adjusts P values and plots | Inspected from exact pinned upstream commit | The logic is required; execution may use an equivalent R script later | No large-data download; a pinned project copy should be added in Step 5C if authorized |
| `notebooks/helper_functions.R` | Defines gSEM, parallel and naive-regression functions | Inspected from exact pinned upstream commit | YES | Same as above |
| `org.Mm.eg.db` | Mouse symbol-to-GO annotation | Not installed locally | NO for core 5a/5c; YES for 5b/5d | Package installation, not a biological-data download |

## 5. Multimodal Cell-ID Alignment

### Authors' logic

The shared identifier is the string `cell_<integer>`:

- expression cells are column names of `gex_res.csv`;
- mechanics and coordinates use row names of `tensionmap_res.csv`;
- inside `do_gsem_regression()`, the code selects
  `gex_res[gene, rownames(data_df)]`.

This is explicit identifier-based selection. It reorders the expression vector
to the mechanics-row order. The code does **not** merely assume that the two
files are already in the same order, although the supplied files are in fact
ordered identically. Later model vectors then rely on the aligned order created
by this selection.

### Read-only archive audit

| Count | dataset 1 | dataset 2 | dataset 3 |
|---|---:|---:|---:|
| Expression cells | 1,163 | 912 | 917 |
| Mechanics cells | 1,163 | 912 | 917 |
| Coordinate cells | 1,163 | 912 | 917 |
| Matched cells | 1,163 | 912 | 917 |
| Expression-only cells | 0 | 0 | 0 |
| Mechanics-only cells | 0 | 0 | 0 |
| Duplicate cell IDs | 0 | 0 | 0 |
| Final cells used by gSEM | 1,163 | **912** | 917 |

For the Figure 5 dataset-2 route, no cells are removed by the notebook after
loading. All 912 have finite, nonmissing `centroid_x`, `centroid_y`, `pressure`,
`stresstensor_eigval1` and `stresstensor_eigval2` values. Cell removal and
expression remapping that followed segmentation correction occurred upstream
when the authors created these processed tables; it is not repeated by the
Figure 5 notebook.

All dataset-2 values sent to `log()` are positive: pressure ranges from
0.0257123 to 11.2879 and the summed stress eigenvalues range from 0.000587885
to 0.632372. The official log transformation therefore does not introduce
`NaN` or negative infinity for this dataset.

## 6. Gene-expression Preprocessing

The table distinguishes operations performed **inside the Figure 5 notebook**
from properties already present in the supplied processed expression matrix.

| Check | Official Figure 5 code does this? | Exact location and interpretation |
|---|---|---|
| Gene filtering | **YES** | Notebook cell 9 retains genes with values >0 in more than 50% of cells. Dataset 2 retains 12,704 of 29,452 genes. |
| Highly variable gene selection | **NO** | `02_sc_analysis.ipynb` creates a top-3,000 HVG list for the later scHOT analysis, but Figure 5 does not read it. |
| Expression normalization | **NO, not in this notebook** | `gex_res.csv` is already supplied as normalized, imputed expression according to the paper. Figure 5 reads it unchanged. |
| Expression log transformation | **NO, not in this notebook** | The paper describes the input as log-transformed normalized expression. No second log is applied in notebook 05 or the gSEM helper. |
| Expression scaling / z-scoring | **NO** | No scaling is applied before gSEM. |
| Zero filtering | **YES, at gene level only** | The >50%-nonzero gene filter is applied. Cells with zero expression for a retained gene are not removed. |
| Cell filtering | **NO** | All matching dataset-2 cells enter each fit. |
| Stress construction | **YES** | Notebook cell 7 defines magnitude as the sum of the two stress-tensor eigenvalues. It is not a Euclidean/Frobenius norm. |
| Mechanics log transformation | **YES** | `do_gsem_regression()` applies natural `log()` separately to pressure and stress magnitude before spatial fitting. |
| Mechanics centering/scaling | **NO explicit global scaling** | Spatial fitted values are subtracted to make residuals, but no z-score or min–max normalization is used. |
| Pressure normalization | **Log only** | No additional pressure normalization is present. |
| Stress normalization | **Sum eigenvalues, then log only** | No additional stress normalization is present. |
| Demo gene sampling | **YES in checked-in notebook; not paper-scale** | Cell 11 uses seed 11235 to sample 100 genes. Full analysis must use all `expressed_genes`, exactly as the notebook note instructs. |

## 7. gSEM Explained in Plain Language

For one gene and one mechanics variable:

1. **Response/dependent variable:** that gene's processed expression value in
   each cell.
2. **Predictor/independent variable:** log intracellular pressure or log
   stress-tensor magnitude in the same cell.
3. **Spatial information:** each cell's `centroid_x` and `centroid_y`.
4. **Controlled effect:** smooth regional variation in expression and mechanics
   that can arise because cells occupy different tissue locations.
5. **Role of `mgcv`:** `mgcv::gam()` fits a flexible two-dimensional smooth
   surface over the centroids. The official call uses `s(x, y, k=300,
   fx=TRUE)` and `method='REML'`; `s()` defaults to a thin-plate regression
   spline in this setting.
6. The fitted spatial value is subtracted from each observation. A positive
   mechanics residual means the cell's mechanics value is higher than the
   smooth spatial expectation at that location. The gene residual has the
   analogous meaning.
7. A standard linear model then asks whether these residuals move together.

This is more informative than raw Pearson or Spearman correlation because a
raw correlation cannot distinguish a within-region gene–mechanics association
from both variables merely being high in the same anatomical region. gSEM
removes the smooth spatial component represented by the specified model.
However, it does not guarantee removal of cell type or every unmeasured
confounder, and it does not establish causality.

The returned association statistics are:

- `beta`: slope of mechanics residual in `lm(r_Y ~ r_X)`;
- `stat`: t statistic for that slope;
- `pval`: two-sided t-test P value for the slope;
- `padj`: Benjamini–Hochberg-adjusted P value.

The notebook applies `p.adjust(..., method='BH')` to the whole combined result
table after both metrics are tested. For the publication-scale analysis, the
documented significance threshold is adjusted P ≤ 0.05.

A positive `beta` means cells with mechanics above their location-specific
expectation tend to express the gene above its location-specific expectation.
A negative `beta` means the opposite. This is an association statement; it
does not say whether the gene changes mechanics or mechanics changes the gene.

## 8. Exact Official Model / Formula

For cell *i*, the paper first models the spatial component of a variable *x*:

```text
x_i = f^x(c_i) + epsilon_i^x
```

Here, `x_i` is either gene expression or a log-transformed mechanical value,
`c_i = (centroid_x, centroid_y)` is the cell position, `f^x` is the smooth
two-dimensional spatial surface, and `epsilon` is the remaining variation.

The exact helper-code fits are:

```r
f_X_hat <- gam(
  force_metric ~ s(centroid_x, centroid_y, k=k_sp, fx=model_fx),
  data=data_df, method=method
)$fitted.values

f_Y_hat <- gam(
  gene ~ s(centroid_x, centroid_y, k=k_sp, fx=model_fx),
  data=data_df, method=method
)$fitted.values

r_X <- X - f_X_hat
r_Y <- Y - f_Y_hat
mod <- lm(r_Y ~ r_X)
```

The publication association model is therefore:

```text
r_i^gene = beta_spatial * r_i^mechanics + epsilon_i
```

The Figure 5 notebook calls the parallel function with `model_fx=TRUE`; the
helper defaults are `k_sp=300` and `method='REML'`. These settings are
scientifically material and should remain fixed in the reproduction unless a
compatibility problem is first documented.

## 9. Dependency Audit

### Python and notebook-host dependencies

Python is not part of the gSEM calculation itself. A direct `Rscript` core run
can avoid Python. The official notebook workflow still needs Jupyter plus an R
kernel, and Scanpy is useful for upstream expression inspection but **not**
required for the minimal Figure 5 model because `gex_res.csv` is already
processed.

| Package | Authors' version | Available in `tensionmap-minimal-repro` | Required for minimal Figure 5 | Intel macOS risk |
|---|---|---|---|---|
| Python | 3.9.12 | YES, 3.9.12 | NO for direct R execution | LOW |
| JupyterLab / Jupyter | 3.0.0 / unspecified | NO in the minimal environment | NO for `Rscript`; YES to execute the notebook interactively | MEDIUM because the pinned stack is old |
| Scanpy | Unpinned in `tensionmap-full.yml` | NO | NO | MEDIUM; only needed if regenerating upstream expression/HVG steps |
| PhenoGraph | 1.5.7 | NO | NO | MEDIUM; upstream cell analysis only |

**Python readiness: PARTIAL.** The core statistical method is R-only, but the
official notebook/preprocessing environment is not present.

### R dependencies

The current machine has system R 4.2.1, matching the authors. Versions in the
authors' saved `sessionInfo()` are listed where available.

| Package | Authors' version | Available locally | Minimal core | Panels / role | Intel macOS risk |
|---|---:|---|---|---|---|
| R | 4.2.1 | YES, 4.2.1 | YES | Runtime | MEDIUM: old ecosystem but exact R exists |
| mgcv | 1.9-0 | YES, 1.8-40 | YES | Spatial GAM fits | **HIGH**: local version differs from saved official version |
| nlme | 3.1-163 | YES, 3.1-157 | YES indirectly | GAM support | MEDIUM; version differs |
| parallel | 4.2.1 | YES, 4.2.1 | YES | Parallel backend support | LOW |
| doParallel | 1.0.17 | NO | YES for official parallel function | Core modeling | MEDIUM |
| foreach | 1.5.2 | NO | YES through doParallel | Gene loop | MEDIUM |
| iterators | 1.0.14 | NO | YES through doParallel | `icount()` | MEDIUM |
| dplyr | 1.1.1 | YES, 1.0.9 | YES for the official result/plot workflow | Result selection/manipulation | MEDIUM; version differs |
| ggplot2 | 3.4.3 | YES, 3.3.6 | YES for the core plots | Figures | MEDIUM; version differs |
| progress | 1.2.2 | NO | NO | Notebook dependency; not used in core helper shown | LOW |
| ggpubr | 0.6.0 | NO | NO | Plotting support | MEDIUM |
| ggExtra | 0.10.1 | NO | NO | Marginal histograms in example residual plot | MEDIUM |
| stringr | 1.5.0 | YES, 1.4.1 | NO | GO label formatting | LOW |
| BuenColors | 0.5.6 | NO | NO | Publication palette | **HIGH**: less common package |
| grid | 4.2.1 | YES, 4.2.1 | NO | Plot annotation | LOW |

### Bioconductor dependencies and external resources

| Package/resource | Authors' version | Available locally | Minimal core | Panels / role | Intel macOS risk |
|---|---:|---|---|---|---|
| EnhancedVolcano | 1.16.0 | NO | YES for the core 5a/5c plots | 5a/5c volcano plots | MEDIUM |
| clusterProfiler | 4.6.0 | NO | NO | 5b/5d GO overrepresentation | HIGH |
| org.Mm.eg.db | 3.16.0 | NO | NO | Mouse gene/GO annotation | HIGH; version-sensitive result |
| AnnotationDbi | 1.60.0 | NO | NO | Annotation dependency | HIGH |
| GO.db | 3.16.0 | NO | NO | GO dependency | HIGH |
| Mouse GO/background | Package-backed; tested universe should be the full expressed-gene set for the paper route | NO | NO | 5b/5d | HIGH; results can drift with annotation versions |

**R readiness: PARTIAL.** The correct R major version exists, but the exact
`mgcv` version and the official parallel/plotting/Bioconductor stack do not.
Nothing was installed during this audit.

## 10. Minimal Reproduction Route

### CORE

The smallest scientifically meaningful Figure 5 reproduction is:

1. use dataset 2 only;
2. extract the authors' existing `gex_res.csv` without altering it;
3. load it with the existing `tensionmap_res.csv`;
4. verify the 912 exact cell-ID matches again in the execution environment;
5. retain all 12,704 genes expressed in >50% of cells;
6. compute stress magnitude as the sum of the two eigenvalues;
7. run the official gSEM settings for both pressure and stress magnitude;
8. apply BH correction exactly as the official notebook does;
9. save the complete association table and reproduce the two main volcano
   summaries for pressure and stress.

This core route addresses the central Figure 5 claim without GO analysis,
selected-gene maps or comparison to naive regression.

### OPTIONAL

- example residual regressions beside panels 5a and 5c;
- sign-separated GO analysis for panels 5b and 5d, after resolving the public
  notebook/publication discrepancy;
- panel 5e spatial expression maps, clearly documented as reconstructed if no
  exact official plotting code is found;
- ordinary linear-regression comparison in notebook cells 23–29;
- dataset 3 / Supplementary Figure 8 and cross-dataset comparisons.

### Resource estimate for the core route

| Item | Estimate / verified value |
|---|---|
| Required biological files | 2: dataset-2 `gex_res.csv` and `tensionmap_res.csv` |
| Required core packages | R 4.2.1, exact-compatible `mgcv`, `nlme`, `doParallel`, `foreach`, `iterators`, `dplyr`, `ggplot2`, `EnhancedVolcano`, and base R dependencies |
| Cells | 912, verified |
| Genes | 12,704 after the official >50% filter, verified |
| Model tests | 25,408 gene–mechanics combinations |
| Runtime | **Estimated 6–12 hours** on this 4-core 1.4 GHz Intel MacBook Pro, based on the notebook's approximately 10 seconds per gene on an M1 and allowing for limited parallelism; must be benchmarked on a small fixed subset before the full run |
| Memory | **Estimated 4–8 GB working requirement**, potentially higher with parallel workers; the machine has 8 GB total, so aggressive parallelism risks swapping or failure |

**Feasibility on the current machine and downloaded data: PARTIAL.** All
required biological data are already local and the cell count is moderate.
The exact R dependencies are incomplete, `mgcv` differs from the authors'
version, and 8 GB RAM makes the official eight-worker setting inappropriate
without a controlled benchmark. The full run may be possible with fewer
workers and more time, but that must be tested rather than assumed.

## 11. Risks and Missing Pieces

- **Publication code gap:** sign-separated GO generation and the exact panel
  5e plotting cell are not present in the pinned public Figure 5 notebook.
- **Demo/full ambiguity:** executing the notebook unchanged produces a seeded
  100-gene dataset-3 demonstration, not the paper's full dataset-2 analysis.
- **Version drift:** local `mgcv` 1.8-40 differs from the authors' 1.9-0;
  plotting and annotation packages are missing or older.
- **Memory pressure:** R's dense import of a 276.6 MB CSV and process-based
  parallelism can approach or exceed the machine's 8 GB RAM.
- **Runtime:** 12,704 genes and two mechanics variables require 25,408 gSEM
  tests. A short benchmark is required before committing to a full run.
- **Annotation drift:** GO terms and P values can change with
  `org.Mm.eg.db`/GO database versions and the chosen gene universe.
- **Statistical interpretation:** gSEM controls the modeled smooth spatial
  trend, not all possible confounding. Associations remain observational and
  cannot establish gene-to-mechanics or mechanics-to-gene causality.
- **Definition of stress magnitude:** the official implementation is the sum
  of eigenvalues. It must not be silently replaced with a conventional tensor
  norm.

## 12. Recommendation for Step 5C

Proceed with a **controlled environment-and-smoke-test step**, not the full
Figure 5 run:

1. preserve the current minimal environment and create a separate
   Figure-5-specific environment from the pinned `tensionmap-full.yml`;
2. prefer the authors' R/Bioconductor versions and document any unavailable
   Intel macOS build before making the smallest compatibility change;
3. add exact pinned copies of notebook 05 and `helper_functions.R` for
   provenance;
4. extract only dataset-2 `gex_res.csv` into a Git-ignored location and verify
   its checksum/shape and 912-cell match;
5. run import checks and a deterministic **very small gene subset** to measure
   per-gene time and peak memory, without claiming Figure 5 reproduction;
6. use the benchmark to choose a safe worker count for 8 GB RAM and decide
   whether the paper-scale run should remain local or move to a larger machine;
7. resolve or explicitly document the missing sign-split GO and panel 5e code
   before attempting those optional panels.
