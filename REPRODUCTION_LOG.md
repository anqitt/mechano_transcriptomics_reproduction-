# Reproduction log

This file is the cumulative experimental record for the TensionMap reproduction.

## Step 2 — GitHub initialization and minimal environment

- **Date:** 2026-09-06 (Asia/Shanghai)
- **System:** macOS 15.7.9 (Darwin 24.6.0), Intel x86_64
- **Git status:** local workspace initialized on `main`, tracking `origin/main` at
  `https://github.com/anqitt/mechano_transcriptomics_reproduction-.git`; the
  pre-existing remote `README.md` and `LICENSE` were preserved.
- **TensionMap upstream:**
  `https://github.com/Computational-Morphogenomics-Group/TensionMap`, commit
  `1a3ed8e940059d9e3574f21b67f340917f1bf049`.
- **Source layout:** minimal vendored, commit-pinned upstream snapshot in
  `TensionMap/`; attribution and included files are recorded in
  `TensionMap/UPSTREAM.md`.
- **Conda:** Anaconda Conda 4.12.0; environment
  `tensionmap-minimal-repro`.
- **Verified packages:** Python 3.9.12; NumPy 1.23.5; SciPy 1.11.2;
  pandas 1.4.1; matplotlib 3.5.1; scikit-image 0.19.2;
  scikit-learn 1.3.1; NLopt 2.7.1.
- **Commands used:** `git init -b main`; `git remote add origin <URL>`;
  `git fetch origin main`; `git checkout --track origin/main`;
  commit-specific downloads from the upstream raw URLs;
  `conda env create -f environment.yml`; direct environment-Python import test.
- **Import test:** `import src.VMSI` and
  `from src.VMSI import run_VMSI` both succeeded. `run_VMSI()` was not called.
- **Errors/fixes:** full and shallow Git submodule clones failed because of
  network timeout/HTTP2 framing errors, so a minimal commit-pinned vendored
  snapshot was used. The initial three-channel Conda solve stalled under Conda
  4.12.0; retrying with only `conda-forge` completed successfully.
- **GitHub authentication and push (2026-09-07):** installed the checksum-
  verified official GitHub CLI 2.100.0 binary and authenticated account
  `anqitt` with `gh auth login --web`; credentials are held by the system
  keyring and the remote URL contains no credentials. After the earlier
  unauthenticated HTTPS attempt failed, `git push origin main` completed as a
  normal non-force push. The remote commit and expected top-level files were
  verified with `git ls-remote` and the GitHub API.
- **Deviations from authors' minimal environment:** omitted `mamba` and
  `cyipopt` as requested; used only `conda-forge` instead of the three listed
  channels. All requested core package versions remain identical to the
  authors' file. MATLAB and the full transcriptomics/R environment were not
  installed.

## Step 3 — Official synthetic TensionMap tutorial

- **Date:** 2026-09-07 (Asia/Shanghai)
- **Input:** `TensionMap/example_data/synthetic/test.tiff`; shape
  935×1098, `uint8`, with 123 foreground labels plus background 0.
- **Environment/command:** `tensionmap-minimal-repro`;
  `conda run -n tensionmap-minimal-repro python run_stage3_synthetic.py`.
  The script follows the notebook's `run_VMSI(img)` call with the default
  NLopt optimizer and does not change scientific parameters.
- **Runtime/result:** 29.85 s; `run_VMSI` completed without an exception and
  analyzed 83 cells. The upstream API discards NLopt termination codes, so a
  specific convergence tolerance cannot be independently confirmed.
- **Output dimensions:** cell results 83×20; adjacency/tension matrix 83×83;
  219 edge-tension entries.
- **Validity checks:** tension, pressure, stress summary fields, and adjacency
  matrix contain no NaN or infinity values. No obviously invalid values or
  runtime warnings were observed.
- **Generated files:** `outputs/stage3_synthetic/{tension.png,pressure.png,
  stress.png,cell_results.csv,adjacency_tension.csv,edge_tensions.csv,
  run_summary.json}`. Temporary optimizer trace files were not retained.
- **Errors/compatibility fixes:** none.
- **Qualitative comparison:** tension and pressure patterns and ranges match
  the official notebook outputs; stress ellipses are also consistent, with
  fitted boundaries overlaid as requested by the current tutorial's
  `plot(['stress', 'cap'])` call.
- **Input-mask inspection:** saved the unchanged 935×1098 label geometry as
  `outputs/stage3_synthetic/input_test_mask.png` using a discrete categorical
  palette. The visualization contains all 123 foreground labels; the source
  TIFF retained SHA-256
  `4586890d7aaa297e14c5f9d75639fb30a0bb6609fccc1e0bdcd4d2e493fc2968`.

## Step 3b — Why 123 labels become 83 analyzed cells

- `segment.py` merges 38 original labels that touch the image boundary into
  one external region, leaving 85 individually represented cells.
- `VMSI.classify_cells()` identifies 52 bulk cells and 33 cells adjacent to
  the external region. It retains 31 of the latter as external constraint
  cells because they share a vertex with a bulk cell. Original labels 108 and
  110 do not touch any bulk-cell vertex and are excluded. Thus, 52 + 31 = 83
  cells participate in inference, while 38 + 2 = 40 original labels do not.
- No original label is disconnected, no internal cell is flagged as a hole or
  invalid topology, and there are no vertices with degree greater than three.
  The 33 vertices marked `fourfold` reflect the code's broad `degree != 3`
  flag; `remove_fourfold()` only acts on internal degree >3 vertices, so it
  removes no cells here. Concave vertices are repositioned, not excluded.
- The official pinned notebook's saved result table also has 83 rows, matching
  this preprocessing audit and the Step 3 run.
- Per-label decisions are recorded in
  `outputs/stage3_synthetic/cell_inclusion_audit.csv`; labels are mapped back
  to the original TIFF by pixel overlap after TensionMap relabeling.

## Step 4A — Real embryo data audit for Figure 3c

- **Date:** 2026-09-07 (Asia/Shanghai); data audit only, with no biological
  dataset downloaded.
- **Target:** Figure 3c compares heterotypic boundary-junction tension with
  homotypic within-tissue tension in three E8.5 mouse-embryo brain datasets:
  NC–FMH (embryo 1), CM–FMH (embryo 2), and MHB (embryo 2).
- **Minimum processed-data route:** six files—`adj_mat.csv` and
  `tensionmap_res.csv` for each of datasets 1–3. The pinned analysis notebook
  obtains junction tensions from the former and boundary annotations from the
  latter, so VMSI need not be rerun for this route.
- **Full-mechanics route:** the three `segmentation_final.tif` masks are the
  VMSI inputs in the pinned upstream run notebook. This is optional for Figure
  3c and was not attempted.
- **Data source/size:** DOI `10.5281/zenodo.13975707` and the public Dropbox
  mirror listed in upstream `data_access.txt`; the complete Zenodo ZIP is
  278.2 MB. Individual file sizes are not published in the notebook/repository.
- **Not required for processed Figure 3c:** `gex_res.csv`, segmentation TIFFs,
  raw membrane/DAPI images, and other paper datasets.
- **Source note:** the paper shows violin plots, whereas the pinned public
  analysis notebook's corresponding plotting cell uses group means with SEM
  bars; its junction classification and source values remain traceable.
- **Manifest:** `REAL_DATA_MANIFEST.md` records the required and optional
  files, provenance, and route distinction.

## Step 4B — Real embryo data acquisition and inspection

- **Date:** 2026-09-08 (Asia/Shanghai).
- **Source:** official Hallou *et al.* Zenodo record
  `10.5281/zenodo.13975708`; archive
  `Data_Hallou_He_et al_BioRxiv_Aug_2023.zip` was downloaded manually after
  both official network endpoints were inaccessible to the automated client.
- **Integrity:** 278,248,511 bytes; MD5
  `14da2772d0bdcfd28e2e91379e6010aa`, matching Zenodo; `unzip -t` reported no
  errors.
- **Extraction:** only `adj_mat.csv` and `tensionmap_res.csv` from datasets
  1–3 were extracted under Git-ignored `data/stage4b_required/` (six files,
  13,397,009 bytes). The archive remains under Git-ignored
  `data/stage4b_download/`.
- **Inspection:** per-cell tables are 1,163×25, 912×25 and 917×25; their
  matching adjacency/tension matrices are 1,163², 912² and 917². Matrix and
  table cell IDs match exactly. The symmetric finite matrices have zero
  diagonals and 3,088, 2,348 and 2,263 unique undirected junctions.
- **Identifier roles:** cell IDs are CSV row indices; `boundary_annotation`
  supplies the Figure 3 compartment, `centroid_x`/`centroid_y` supply position,
  `pressure` supplies inferred cell pressure, and each nonzero `adj_mat` entry
  links a cell-ID pair to its inferred junction tension.
- **Code verification:** the pinned `01_biophysical_analysis.ipynb` uses these
  identifiers and annotations, requires heterotypic junctions to have boundary
  graph distance 0, and uses same-annotation junctions at distances 1–5 as the
  away-from-boundary homotypic groups. No Figure 3c grouping, statistics or
  final plot was run here.
- **Inspection outputs:** `outputs/stage4b_real_data/{real_embryo_cells.png,
  real_embryo_junctions.png,real_embryo_tension_preview.png}` generated by
  `inspect_stage4b_real_data.py`.
- **Limitations:** centroid networks do not show exact membrane-interface
  curves; those require segmentation masks. The CSVs do not state physical
  units for coordinates or tension. No new environment was installed.

## Step 4C — Figure 3c homotypic versus heterotypic tension

- **Date:** 2026-09-08 (Asia/Shanghai).
- **Source/method:** authors' processed `tensionmap_res.csv` and `adj_mat.csv`
  for datasets 1–3; grouping follows pinned
  `notebooks/01_biophysical_analysis.ipynb` at upstream commit
  `1a3ed8e940059d9e3574f21b67f340917f1bf049`.
- **Filtering:** excluded `Other`; boundary likelihood threshold 0.15;
  heterotypic junctions cross the two compartments at graph distance 0;
  homotypic groups join equal annotations at graph distances 1–5. Only the
  nonzero matrix upper triangle was used. Tensions were not normalized.
- **Counts:** dataset 1 = 1,611 homotypic and 151 heterotypic; dataset 2 = 855
  and 51; dataset 3 = 494 and 29. The two homotypic tissues remain separate in
  official summaries/tests.
- **Statistics:** group mean, median, SEM and n; one-sided pairwise
  Mann–Whitney U tests (`homotypic < heterotypic`). P values were dataset 1:
  0.007875 and 0.052046; dataset 2: 0.031676 and 0.013625; dataset 3: 0.005954
  and 0.000553. Dataset 1's P = 0.052 agrees with the published panel.
- **Percent comparison:** conventional tissue-specific mean decreases were
  5.94–29.67%. The notebook does not calculate a percentage or document the
  arithmetic behind the paper's approximate 12–35% statement. A median-based
  dataset summary gives 10.81%, 19.58% and 35.56%, close to that wording, but
  this is recorded as an inference rather than substituted into the analysis.
- **Sanity checks:** zero duplicated undirected junctions, self-junctions,
  missing annotations, NaN/Inf tensions or mixed-dataset rows.
- **Outputs:** `outputs/stage4c_figure3c/{junction_tension_analysis.csv,
  group_summary.csv,pairwise_tests.csv,run_summary.json,
  figure3c_reproduction.png,figure3c_simple_explanation.png}` and
  `FIGURE3C_GUIDE.md`, generated by `reproduce_figure3c.py`.
- **Compatibility:** the existing environment lacks seaborn, so the published
  violin form was drawn with matplotlib. No environment or scientific method
  was changed; VMSI was not rerun.
