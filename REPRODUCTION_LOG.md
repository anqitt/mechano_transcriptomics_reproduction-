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
