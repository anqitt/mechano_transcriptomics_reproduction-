# Figure 3c Real Data Guide

## 1. Biological sample

The data describe three brain regions from sagittal sections of E8.5 mouse
embryos profiled by seqFISH. The Figure 3 analysis studies these compartment
pairs:

- dataset 1, embryo 1: neural crest (NC) versus the combined
  forebrain/midbrain/hindbrain compartment (FMH);
- dataset 2, embryo 2: cranial mesoderm (CM) versus FMH;
- dataset 3, embryo 2: midbrain versus hindbrain (MHB).

The six files inspected here are processed tables from the authors' [Zenodo
record](https://doi.org/10.5281/zenodo.13975708). The archive is
`Data_Hallou_He_et al_BioRxiv_Aug_2023.zip`, exactly 278,248,511 bytes, with
MD5 `14da2772d0bdcfd28e2e91379e6010aa`. This matches the checksum published by
Zenodo. Only the six Figure 3c Route A files (13,397,009 extracted bytes) were
extracted into the Git-ignored `data/stage4b_required/` directory.

## 2. Required files

Each dataset has the same two-file design. The unnamed first CSV column is
read as the row index (`index_col=0`) and contains the cell ID.

| File | Size | Shape | Data structure and role |
|---|---:|---:|---|
| `dataset1/tensionmap_res.csv` | 326,440 B | 1,163 × 25 | One row per cell; identity, position, annotation, pressure, stress and morphology |
| `dataset1/adj_mat.csv` | 5,519,565 B | 1,163 × 1,163 | Symmetric cell-by-cell matrix; nonzero upper-triangle entries are junction tensions |
| `dataset2/tensionmap_res.csv` | 355,720 B | 912 × 25 | One row per cell, same schema |
| `dataset2/adj_mat.csv` | 3,410,497 B | 912 × 912 | Symmetric adjacency/tension matrix |
| `dataset3/tensionmap_res.csv` | 340,202 B | 917 × 25 | One row per cell, same schema |
| `dataset3/adj_mat.csv` | 3,444,585 B | 917 × 917 | Symmetric adjacency/tension matrix |

The 25 per-cell columns are: `pressure`, `perimeter`,
`feret_d`, `area`, `centroid_x`, `centroid_y`, `stresstensor_eigval1`,
`stresstensor_eigval2`, `stresstensor_orientation`,
`stresstensor_anisotropy`, `inertiatensor_eigval1`,
`inertiatensor_eigval2`, `inertiatensor_orientation`,
`inertiatensor_anisotropy`, `moments_hu_1`, `moments_hu_3`, `bbox_x`,
`bbox_y`, `celltype`, `celltype_conf`, `cluster`, `cluster_conf`,
`phenograph_clusters`, `boundary_annotation`, and `polygon_perimeter`.

Representative leading rows, restricted to the columns most useful for this
audit, are:

| Dataset | Cell ID | `centroid_x` | `centroid_y` | `boundary_annotation` | `pressure` |
|---|---|---:|---:|---|---:|
| 1 | `cell_0` | 6375.198 | 274.819 | Neural Crest | 1.53122 |
| 1 | `cell_1` | 6093.346 | 322.744 | Neural Crest | 0.373211 |
| 2 | `cell_0` | 3054.066 | 321.178 | Forebrain/Midbrain/Hindbrain | 0.348869 |
| 2 | `cell_1` | 8081.225 | 444.657 | Forebrain/Midbrain/Hindbrain | 0.131239 |
| 3 | `cell_1` | 2450.251 | 1742.629 | Other | 0.926638 |
| 3 | `cell_2` | 2674.191 | 1771.088 | Other | 0.630024 |

Representative first nonzero upper-triangle matrix entries are:

| Dataset | Row cell | Column cell | Stored tension |
|---|---|---|---:|
| 1 | `cell_0` | `cell_1` | 117.2487 |
| 1 | `cell_0` | `cell_2` | 270.5048 |
| 1 | `cell_0` | `cell_3` | 230.1556 |
| 2 | `cell_0` | `cell_2` | 97.4741 |
| 2 | `cell_0` | `cell_3` | 64.1654 |
| 2 | `cell_0` | `cell_6` | 137.5817 |
| 3 | `cell_1` | `cell_2` | 189.6916 |
| 3 | `cell_1` | `cell_3` | 33.6662 |
| 3 | `cell_1` | `cell_4` | 265.5754 |

All three matrices have cell IDs that exactly match the corresponding per-cell
table in both membership and order. They are symmetric, their diagonals are
zero, and all entries are finite. There are 3,088, 2,348 and 2,263 unique
undirected junctions in datasets 1, 2 and 3, respectively.

## 3. What one cell looks like in the data

In dataset 1, `cell_31` is one concrete cell. Its centroid is
(`centroid_x` = 3436.817, `centroid_y` = 883.242), its detailed `celltype` is
`Forebrain/Midbrain/Hindbrain`, its Figure 3 compartment is
`boundary_annotation = Forebrain/Midbrain/Hindbrain`, and its inferred
`pressure` is 0.449386.

The row index is the cell's identity. `celltype` is a more detailed cell-type
label, while `boundary_annotation` is the coarser compartment label that the
official Figure 3 code actually uses. The centroid columns provide spatial
position. `pressure` and the stress-tensor columns are already inferred
mechanical quantities; pressure is not stored in `adj_mat.csv`.

## 4. What one junction looks like in the data

Dataset 1 cells `cell_31` and `cell_51` illustrate one real junction:

| Cell | `centroid_x` | `centroid_y` | `boundary_annotation` |
|---|---:|---:|---|
| `cell_31` | 3436.817 | 883.242 | Forebrain/Midbrain/Hindbrain |
| `cell_51` | 3260.771 | 968.571 | Neural Crest |

At matrix row `cell_31`, column `cell_51`, `adj_mat.csv` contains
`223.1215633631377`. Because the entry is nonzero, the cells form a junction;
the stored number is its precomputed inferred tension. The symmetric entry at
row `cell_51`, column `cell_31` contains the same value, so the analysis reads
only the upper triangle to avoid counting the junction twice.

## 5. How cell → tissue → junction → tension are connected

The connection is entirely through the same `cell_*` identifiers:

```text
tensionmap_res.csv row index (for example, cell_31)
  → boundary_annotation: its Figure 3 tissue compartment
  → centroid_x + centroid_y: its spatial position
  → pressure: its inferred intracellular pressure

adj_mat.csv row cell ID + column cell ID
  → value = 0: no junction represented
  → value ≠ 0: the cell pair forms a junction
  → that nonzero value: the junction's inferred tension
```

The pinned official notebook verifies this interpretation by selecting
neighbors with `adj_mat.loc[cell, :] != 0`, looking up their
`boundary_annotation` values in `tensionmap_res.csv`, and constructing a
three-column junction table named `cell_1`, `cell_2`, `tension` from the
nonzero upper triangle.

## 6. Homotypic vs heterotypic

For the two non-`Other` compartment labels in a dataset:

- **Homotypic** means both endpoint cells have the same
  `boundary_annotation`.
- **Heterotypic** means one endpoint has the first compartment annotation and
  the other has the second.

The official code adds an important spatial condition. It computes a
cell-level boundary likelihood from neighboring annotations, converts this to
graph distance from the detected boundary, and calls a cross-compartment
junction `heterotypic` only when the minimum endpoint distance is 0. For the
eventual Figure 3c comparison, it retains same-compartment junctions whose
minimum distance is 1–5 as the two `*_awayfrom_boundary` homotypic reference
groups. Cells annotated `Other` are removed before this classification.

Thus `cell_31`–`cell_51` is structurally cross-compartment, but the official
code will call it Figure 3c `heterotypic` only if it also lies at graph distance
0. That final grouping and its statistics were deliberately not calculated in
Step 4B.

## 7. What Figure 3c will eventually compare

Figure 3c will compare the distributions of precomputed tension values for:

1. cross-compartment junctions at the inferred tissue boundary; and
2. same-compartment junctions one to five graph steps away from that boundary,
   separately for each tissue and each of the three datasets.

Step 4B does not generate those groups, perform tests, or make the Figure 3c
plot. Its figures are only structural previews:

- `real_embryo_cells.png`: centroid positions colored by
  `boundary_annotation`;
- `real_embryo_junctions.png`: nonzero matrix entries drawn between centroids;
- `real_embryo_tension_preview.png`: the same network colored directly by its
  precomputed tension values.

## 8. Remaining uncertainties

- The six-file route has centroid-to-centroid network geometry, not the exact
  physical curve of each cell-cell interface; generating true junction
  contours would require the segmentation TIFFs, which are unnecessary for
  the Figure 3c statistics.
- The CSVs do not include physical-unit metadata for centroid coordinates or
  inferred tensions. The official notebook divides centroids by two only when
  aligning them to its downsampled segmentation image; this audit preserves
  the stored coordinates.
- The public notebook makes a mean-and-SEM bar plot in the relevant cell,
  whereas the published Figure 3c is described as violin plots. The future
  reproduction must document that presentation discrepancy.
- Exact boundary detection and the final homotypic/heterotypic subsets remain
  intentionally uncomputed until the Figure 3c reproduction step.
