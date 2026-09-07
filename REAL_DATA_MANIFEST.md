# Real-data manifest for Figure 3c

This audit targets only Figure 3c of Hallou *et al.* and is pinned to
TensionMap commit `1a3ed8e940059d9e3574f21b67f340917f1bf049`. No biological
dataset was downloaded during this step.

## Verified figure target

Figure 3c asks whether junctions that cross a transcriptomically defined
tissue boundary have higher inferred tension than junctions between cells of
the same tissue away from that boundary. It uses three E8.5 mouse-embryo brain
comparisons:

1. dataset 1 (embryo 1): neural crest (NC) versus
   forebrain/midbrain/hindbrain (FMH);
2. dataset 2 (embryo 2): cranial mesoderm (CM) versus FMH;
3. dataset 3 (embryo 2): midbrain versus hindbrain (MHB).

The paper reports that homotypic junctional tensions are approximately
12–35% lower than heterotypic boundary tensions, with the smallest separation
in dataset 1 and the largest in dataset 3. These statements and the three
comparisons are directly supported by the [paper](https://www.nature.com/articles/s41592-025-02618-1).

The pinned [`01_biophysical_analysis.ipynb`](https://github.com/Computational-Morphogenomics-Group/TensionMap/blob/1a3ed8e940059d9e3574f21b67f340917f1bf049/notebooks/01_biophysical_analysis.ipynb)
provides the executable classification path. It treats a junction as being at
the boundary when its graph distance is zero, then compares heterotypic
junctions there with tissue-specific homotypic junctions at graph distances
1–5. The paper presents violin plots; the public notebook's corresponding
cell uses a bar plot of group means with standard-error bars. This plotting
difference does not change the source tension values or the grouping rules.

## Download manifest

All named files are distributed in the authors' [Hallou *et al.* Zenodo data
record](https://doi.org/10.5281/zenodo.13975707) and through the public
[Dropbox mirror](https://www.dropbox.com/scl/fo/turadztaz0bhf8is9wgtk/h?rlkey=1890jxtbwvrclz7ofm1oydlv7&dl=0)
referenced by each upstream `data_access.txt`. Individual file sizes are not
published in the notebook or repository; the complete Zenodo ZIP is 278.2 MB.

| File | Biological meaning | Format | Source | Approx size | Required for Fig 3c? |
|---|---|---|---|---:|---|
| `reproduce_data/dataset1/adj_mat.csv` | Embryo 1 cell adjacency matrix; nonzero entries contain inferred junction tensions | CSV, processed VMSI output | Hallou Zenodo/Dropbox | Not individually published | **Yes — Route A** |
| `reproduce_data/dataset1/tensionmap_res.csv` | Embryo 1 per-cell results, including `boundary_annotation` and centroid coordinates | CSV, processed table | Hallou Zenodo/Dropbox | Not individually published | **Yes — Route A** |
| `reproduce_data/dataset2/adj_mat.csv` | Embryo 2 CM–FMH adjacency and inferred junction tensions | CSV, processed VMSI output | Hallou Zenodo/Dropbox | Not individually published | **Yes — Route A** |
| `reproduce_data/dataset2/tensionmap_res.csv` | Embryo 2 CM–FMH per-cell results and boundary annotations | CSV, processed table | Hallou Zenodo/Dropbox | Not individually published | **Yes — Route A** |
| `reproduce_data/dataset3/adj_mat.csv` | Embryo 2 MHB adjacency and inferred junction tensions | CSV, processed VMSI output | Hallou Zenodo/Dropbox | Not individually published | **Yes — Route A** |
| `reproduce_data/dataset3/tensionmap_res.csv` | Embryo 2 MHB per-cell results and boundary annotations | CSV, processed table | Hallou Zenodo/Dropbox | Not individually published | **Yes — Route A** |
| `reproduce_data/dataset1/segmentation_final.tif` | Manually corrected instance segmentation of the embryo 1 brain region | TIFF, processed image | Hallou Zenodo/Dropbox | Not individually published | Route B only |
| `reproduce_data/dataset2/segmentation_final.tif` | Manually corrected instance segmentation of the embryo 2 CM–FMH region | TIFF, processed image | Hallou Zenodo/Dropbox | Not individually published | Route B only |
| `reproduce_data/dataset3/segmentation_final.tif` | Manually corrected instance segmentation of the embryo 2 MHB region | TIFF, processed image | Hallou Zenodo/Dropbox | Not individually published | Route B only |
| `reproduce_data/dataset1/gex_res.csv` | Spatial gene-expression results loaded by the general notebook | CSV, processed table | Hallou Zenodo/Dropbox | Not individually published | No; unused by the Fig. 3c calculation |
| `reproduce_data/dataset2/gex_res.csv` | Spatial gene-expression results loaded by the general notebook | CSV, processed table | Hallou Zenodo/Dropbox | Not individually published | No; unused by the Fig. 3c calculation |
| `reproduce_data/dataset3/gex_res.csv` | Spatial gene-expression results loaded by the general notebook | CSV, processed table | Hallou Zenodo/Dropbox | Not individually published | No; unused by the Fig. 3c calculation |
| Raw membrane/DAPI image channels | E-cadherin, N-cadherin, pan-cadherin or beta-catenin membrane signal and DAPI nuclei used to make/correct masks | Raw microscopy images | Underlying seqFISH study, [Lohoff *et al.*](https://doi.org/10.1038/s41587-021-01006-2); not referenced as an input by the Fig. 3c notebook | Not established | No |

No separate spatial-coordinate file is needed: the processed per-cell table
contains `centroid_x` and `centroid_y`. Likewise, no raw membrane image is read
by either the Figure 3 analysis notebook or the pinned VMSI-running notebook.

## Minimum reproducible dataset

### Route A — processed-data reproduction (recommended first)

Download the six bold Route A files: `adj_mat.csv` and
`tensionmap_res.csv` for each of datasets 1–3. The former supplies the
authors' inferred junction tensions, while the latter supplies the tissue
annotation needed to label junctions as heterotypic or homotypic. Therefore,
VMSI does **not** have to be rerun to reproduce the Figure 3c comparison.

The exact selective-download total cannot be verified from the public
metadata. If using the standard Zenodo package, the expected download is one
278.2 MB ZIP; the six extracted files will be a subset of that archive.

### Route B — full mechanics reproduction

Use the three `segmentation_final.tif` masks as VMSI inputs, following the
pinned [`00_run_tensionmap.ipynb`](https://github.com/Computational-Morphogenomics-Group/TensionMap/blob/1a3ed8e940059d9e3574f21b67f340917f1bf049/notebooks/00_run_tensionmap.ipynb),
and retain the three `tensionmap_res.csv` files for the authors' tissue-boundary
annotations. Recompute an adjacency/tension matrix for each dataset before
running the Figure 3c grouping. The notebook hard-codes the MATLAB optimizer,
so an NLopt-only rerun will require a carefully documented optimizer choice
later. Matching newly inferred cells to the supplied annotations is a
reasonable route inferred from the file contents, but must be validated when
Route B is attempted.

## Download decision

- **Absolutely necessary for the recommended route:** six CSV files (two for
  each of the three comparisons).
- **Can be skipped for Figure 3c processed-data reproduction:** all three
  segmentation TIFFs, all `gex_res.csv` files, raw membrane/DAPI images,
  transcriptomics matrices beyond the supplied boundary annotations, and all
  other paper datasets.
- **Expected download:** 278.2 MB when acquiring the complete official Zenodo
  archive; the exact size of a selective six-file Dropbox download is not
  publicly itemized and should be measured before downloading.
