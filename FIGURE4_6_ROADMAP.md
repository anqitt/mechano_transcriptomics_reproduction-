# Figures 4–6 Reproduction Roadmap

## Scope and source basis

This is a planning document only. No Figure 4–6 analysis was executed. The
roadmap was checked against the [published article and Methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC11978512/),
the supplementary information, and the official notebooks at upstream commit
`1a3ed8e940059d9e3574f21b67f340917f1bf049`.

The paper uses E8.5 mouse-embryo sagittal sections profiled by seqFISH. Its
processed expression matrices contain the measured genes plus expression
imputed from a mouse-gastrulation single-cell RNA-seq atlas. Thus the
transcriptomic variable in Figures 4–6 is processed/imputed single-cell gene
expression, not a new RNA-seq experiment performed by TensionMap.

## Figure 4

### Biological Question

**Directly supported:** after Figure 3 establishes elevated tension at tissue
boundaries, Figure 4 asks which spatially patterned ligand–receptor (LR)
signals could help generate that boundary phenotype. The main panel studies
the cranial mesoderm (CM)–forebrain/midbrain/hindbrain (FMH) boundary in
dataset 2; the midbrain–hindbrain analysis is in Supplementary Figure 7.

**Why it follows Figure 3:** Figure 3 identifies a physical observation but
does not identify a molecular mechanism. Figure 4 searches for candidate
cell–cell signals on the two sides of the high-tension interface.

### Data and Modalities

- `dataset2/gex_res.csv`: cell-by-gene normalized/imputed expression.
- `dataset2/adj_mat.csv`: cell-pair adjacency and inferred junction tension.
- `dataset2/tensionmap_res.csv`: cell identity, compartment, centroid and
  mechanics metadata.
- `notebooks/temp_data/distance_to_boundary.csv` and
  `boundary_tensions.csv`: boundary-derived tables made by
  `01_biophysical_analysis.ipynb`.
- `reproduce_data/omnipath_cellchatdb.txt`: mouse CellChatDB LR annotations
  obtained through OmniPath.

The modalities are spatial transcriptomics, cell/tissue annotations, spatial
coordinates, cell adjacency and precomputed junctional mechanics. Importantly,
the official LR score itself uses expression and adjacency; inferred tension
provides the independently observed boundary phenotype and its spatial
profile, rather than entering the LR interaction-potential formula.

### Method

For every known LR pair and directed heterotypic cell pair, the notebook uses
an interaction potential `ligand_expression × receptor_expression`. It
compares cross-boundary potentials with within-tissue distributions using
rank-based statistics, ranks positive directional interaction likelihoods,
and performs GO overrepresentation on the leading LR genes. It also plots 2D
expression maps and 1D profiles relative to the boundary. The definition and
directionality are described in the paper's [LR signaling Methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC11978512/).

### Output and Biological Meaning

Outputs include the boundary tension/expression profiles, ranked LR pairs in
each direction, GO terms, selected junction interaction-potential
distributions, and spatial expression maps. The paper reports enrichment for
adhesion, response to mechanical stimulus, morphogenesis and ephrin-receptor
signaling. High-ranked examples include Wnt5a–Fzd5, Efna1–Epha5 and
Efnb1–Ephb1, with complementary expression across the interface. The paper
therefore proposes ephrin and other directional signals as candidate molecular
determinants of elevated interfacial tension ([Figure 4 and Results](https://pmc.ncbi.nlm.nih.gov/articles/PMC11978512/)).

**What this directly shows:** expression-compatible LR pairs are spatially and
directionally enriched across the high-tension boundary.

**What it does not prove:** it does not measure receptor activation, signaling
flux, protein abundance or contractility, and it does not demonstrate that any
LR pair causes the elevated tension. Perturbation experiments would be needed
for causality. Diffusible signaling between nonadjacent cells is also not
modeled.

### Official Code

- Primary: `notebooks/03_lr_analysis.ipynb`
- Required upstream preparation: `notebooks/01_biophysical_analysis.ipynb`
- Expression preprocessing/HVG context: `notebooks/02_sc_analysis.ipynb`
- Plotting/helper functions: `notebooks/helper_functions.py`

### Dependencies and Reproduction Difficulty

**Difficulty: MEDIUM.** The analysis is mainly Python/pandas/SciPy plotting,
but it joins large expression matrices to boundary and adjacency information
and has several prepared-table dependencies.

Not yet ready locally: the large `gex_res.csv` files and LR annotation table
are not extracted into the working data subset, although the expression files
are present inside the already downloaded, Git-ignored official archive. The
current minimal Conda environment does not provide the complete Python stack
in the authors' `tensionmap-full.yml` (notably Scanpy/PhenoGraph and ancillary
packages). No new biological download appears necessary if the archive is
complete; this must be verified before reproduction.

## Figure 5

### Biological Question

**Directly supported:** Figure 5 asks which genes have expression levels
associated with a cell's mechanical state after removing broad spatial
patterns shared by both expression and mechanics.

**Why it follows Figure 3:** Figures 3–4 focus on a predefined tissue boundary
and candidate signaling mechanism. Figure 5 broadens the question to an
unbiased, gene-by-gene search across cells for coordinated transcriptional and
mechanical states.

### Data and Modalities

- `gex_res.csv`: normalized/imputed single-cell transcriptomics; this is where
  transcriptomics directly becomes the response variable.
- `tensionmap_res.csv`: cell centroids plus inferred intracellular pressure
  and stress-tensor eigenvalues.
- Dataset 2 supplies the main Figure 5 panels; other datasets provide
  comparison/supplementary evidence.

The mechanics predictors are log-transformed **intracellular pressure** and
**stress-tensor magnitude**, implemented as
`stresstensor_eigval1 + stresstensor_eigval2`. Junction tension is not the
gene-level predictor in this figure.

### Method

The geoadditive structural equation model (gSEM) first fits a two-dimensional
thin-plate spline of spatial coordinates separately to each mechanical
predictor and each gene. It subtracts the fitted spatial trends, then regresses
the gene-expression residual on the mechanical residual. In plain language,
it asks whether cells that are more or less mechanical than expected for their
location also express a gene more or less than expected for that location.
The implementation is in `do_gsem_regression()` in
`notebooks/helper_functions.R`, using `mgcv::gam`; regression P values are BH
adjusted. This is the paper's explicit treatment of spatial confounding
([Structural equation regression Methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC11978512/)).

### Output and Biological Meaning

The main outputs are pressure- and stress-association coefficients and
adjusted P values, volcano plots, example residual regressions, spatial maps,
and GO enrichment for positively and negatively associated genes. Accounting
for space produces fewer significant genes than ordinary linear regression,
and many associations are tissue/context specific. Reported enriched themes
include adhesion-dependent spreading, morphogenesis/differentiation, actin
cytoskeleton organization and migration ([Figure 5 Results](https://pmc.ncbi.nlm.nih.gov/articles/PMC11978512/)).

**What this directly shows:** statistically significant linear covariation
between residualized gene expression and residualized pressure or stress,
beyond the smooth spatial trends modeled by the chosen spline.

**What it does not prove:** gSEM does not establish whether gene expression
causes mechanics, mechanics causes expression, or a third unmodeled variable
causes both. It does not guarantee removal of every spatial or cell-type
confounder, and an inferred mechanical quantity is not a direct force
measurement.

### Official Code

- Primary: `notebooks/05_spatial_regression.ipynb`
- Model functions: `notebooks/helper_functions.R`
- Expression/HVG inspection: `notebooks/02_sc_analysis.ipynb`

### Dependencies and Reproduction Difficulty

**Difficulty: HIGH.** The notebook states that fitting one gene takes about
10 seconds on an M1 MacBook Pro and uses a 100-gene demonstration subset by
default. A paper-scale run must replace that subset with the full expressed
gene list and will require careful parallel-runtime and result validation.

Missing locally: R 4.2.1 and the authors' full R/Bioconductor environment,
including `mgcv`, `sp`, `doParallel`, `dplyr`, `ggplot2`, `ggpubr`,
`EnhancedVolcano`, `clusterProfiler`, `org.Mm.eg.db`, `stringr` and
`BuenColors`; also the unextracted large `gex_res.csv` matrices. The current
minimal environment was intentionally not changed.

## Figure 6

### Biological Question

**Directly supported:** Figure 6 asks whether gene expression responds to
mechanical state in shapes that a straight-line model cannot capture—for
example, thresholds, sigmoid responses, or expression restricted to an
intermediate mechanical range.

**Why it follows Figure 5:** Figure 5 tests one linear coefficient per gene.
Figure 6 asks what is missed when expression changes only after a threshold or
changes direction across the mechanical range.

### Data and Modalities

- `dataset2/gex_res.csv` for the main figure (dataset 3 is supplementary).
- `dataset2/tensionmap_res.csv` for pressure and stress eigenvalues.
- `notebooks/temp_data/highly_variable.txt`, containing the top 3,000 highly
  variable genes selected with Scanpy (`flavor='seurat_v3'`).

As in Figure 5, the tested mechanics variables are pressure and stress-tensor
magnitude (`eigval1 + eigval2`), not junction tension. Cells are ranked by each
mechanical variable.

### Method

The notebook computes locally weighted-median expression along the ranked
mechanical axis. scHOT tests whether that local statistic varies more than
expected under permutation (200 permutations per gene in the paper), followed
by BH correction at adjusted P ≤ 0.1. Significant z-normalized profiles are
hierarchically clustered, the number of clusters is chosen with
`dynamicTreeCut`, and clusters receive GO overrepresentation analysis. Here,
“nonlinear association” means the expression-versus-mechanics profile is not
restricted to a constant-slope line; it may be monotonic but curved, sigmoid,
thresholded or nonmonotonic/band-pass-like ([nonlinear-association Methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC11978512/)).

### Output and Biological Meaning

Figure 6 reports seven pressure-associated and four stress-associated profile
clusters in dataset 2, with example spatial maps and GO terms. Reported
pressure profiles include opposite sigmoid behaviors around mechanical
thresholds; their gene sets include developmental regulators (for example,
Wnt7b, Lhx2, Pax3 and En1) and adhesion/contractility genes (for example,
Epha7 and Shroom3). The authors interpret this as evidence that distinct gene
programs are associated with different ranges of mechanical state
([Figure 6 Results](https://pmc.ncbi.nlm.nih.gov/articles/PMC11978512/)).

**What this directly shows:** significant, reproducible-in-permutation
patterns of local expression along ranked inferred pressure or stress within
the analyzed section, plus groups of similarly shaped profiles.

**What it does not prove:** the curve shape is not a dose–response experiment,
does not identify causal direction or a molecular sensor, and does not by
itself demonstrate feedback, thresholds or band-pass circuitry. Cluster count
and interpretation depend on smoothing, ranking, filtering, permutation and
tree-cut choices.

### Official Code

- Primary: `notebooks/04_nonlinear_schot.ipynb`
- Required HVG generation: `notebooks/02_sc_analysis.ipynb`
- Helper/GO functions: `notebooks/helper_functions.R`

### Dependencies and Reproduction Difficulty

**Difficulty: HIGH.** Testing 3,000 genes with 200 permutations and clustering
full profiles is computationally heavy, and the official notebook defaults to
a small demonstration subset unless edited for a paper-scale run.

Missing locally: the R/Bioconductor stack in the authors'
`tensionmap-full.yml`, especially `scHOT` 1.10, `doParallel`, `dplyr`,
`ggplot2`, `stringr`, `BuenColors`, `dynamicTreeCut`, `clusterProfiler` and
`org.Mm.eg.db`; Scanpy/Seurat-v3-compatible HVG preprocessing; the generated
`highly_variable.txt`; and the unextracted large expression matrix.

## Overall Storyline

```text
Figure 3: Where is mechanics different?
  High junctional tension marks tissue-compartment boundaries.
      ↓ New question: which molecular signals could produce that boundary tension?
Figure 4: What signaling candidates sit across the boundary?
  Directional LR analysis highlights ephrin and other adhesion/mechanosignaling pairs.
      ↓ New question: beyond a chosen boundary, which genes track cell mechanics globally?
Figure 5: Which expression–mechanics links remain after accounting for space?
  gSEM identifies linear gene–pressure/stress associations after spatial residualization.
      ↓ New question: are important relationships curved or threshold-like rather than linear?
Figure 6: What nonlinear response patterns are present?
  scHOT identifies and clusters nonlinear expression profiles along mechanical rankings.
```

## Recommended Reproduction Order

**Recommendation B: prioritize Figure 5 first, then Figure 4, then Figure 6.**

1. **Figure 5** is the most direct match to the project's spatial-multi-omics
   and computational-biology goal: a clear biological question, paired
   cell-level transcriptomic/mechanical data, an explicit method for spatial
   confounding, interpretable coefficients, and comparison with ordinary
   regression. Begin with the official demonstration subset before any
   paper-scale run.
2. **Figure 4** is biologically compelling and technically lighter. It then
   adds a boundary-specific signaling interpretation and an independent
   cross-check against the Figure 3 mechanical phenotype.
3. **Figure 6** adds the most methodological nuance but also the largest
   computational and dependency burden. It is easiest to interpret after the
   linear gSEM baseline is understood.

This is a reproduction-priority ranking, not a claim that Figure 5 is more
important biologically than the boundary mechanism in Figure 4.

| Figure | Biological importance | Spatial multi-omics relevance | Computational-biology relevance | Validation clarity | Technical/dependency burden |
|---|---|---|---|---|---|
| 4 | High | High | Medium–high | Candidate LR enrichment plus spatial directionality; no perturbation | Medium |
| 5 | High | Very high | Very high | Spatially adjusted versus naive regression, cross-dataset/GO context | High |
| 6 | High | Very high | Very high | Permutation testing and profile clustering; parameter-sensitive | Very high |

## Missing Dependencies / Risks

- The current `tensionmap-minimal-repro` environment is intentionally
  insufficient for these notebooks. The pinned full environment combines
  Python 3.9.12, R 4.2.1, Scanpy and older Bioconductor packages; solving it on
  the current Intel macOS system may require a small compatibility audit.
- The official archive is available locally, but only Figure 3's six small
  processed files have been extracted. The three `gex_res.csv` members total
  roughly 864 MB uncompressed; they must remain Git-ignored.
- Figure 4 depends on intermediate tables produced by notebook 01 and a pinned
  LR database snapshot. Regenerating from a live OmniPath query could change
  results, so the authors' snapshot should be preferred.
- Notebooks 04 and 05 deliberately run small random/demo subsets by default.
  Reproducing the paper requires switching to the documented full gene sets,
  fixing random seeds where possible, recording parallel settings, and
  distinguishing demo output from publication output.
- Figure 5's spline basis (`k=300`, fixed smooth in the shown call) and Figure
  6's smoothing/permutation/clustering choices are scientifically material and
  should not be modernized silently.
- GO results depend on annotation-package versions and the stated background
  gene universe. Current annotation databases may not reproduce the paper's
  exact terms or P values.
- All results are observational associations based on inferred mechanics in
  2D sections. Spatial correction, cross-section consistency and permutation
  tests strengthen evidence but do not replace perturbational validation.
