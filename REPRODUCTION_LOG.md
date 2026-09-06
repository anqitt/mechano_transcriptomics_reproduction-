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
- **Deviations from authors' minimal environment:** omitted `mamba` and
  `cyipopt` as requested; used only `conda-forge` instead of the three listed
  channels. All requested core package versions remain identical to the
  authors' file. MATLAB and the full transcriptomics/R environment were not
  installed.
