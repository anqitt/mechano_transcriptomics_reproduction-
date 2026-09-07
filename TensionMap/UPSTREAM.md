# Upstream attribution

The files in this directory are a minimal vendored snapshot of the official
TensionMap project. They are not original work of this reproduction repository.

- Upstream project: TensionMap
- Authors/maintainers: Computational Morphogenomics Group and TensionMap contributors
- Repository: https://github.com/Computational-Morphogenomics-Group/TensionMap
- Upstream branch inspected: `main`
- Pinned commit: `1a3ed8e940059d9e3574f21b67f340917f1bf049`
- Upstream license: MIT; see the upstream repository for the authoritative license

## Included files

Only the files required for the minimal import check and later synthetic tutorial
are included at this stage:

- `src/VMSI.py`
- `src/segment.py`
- `src/bwmorph.py`
- `tensionmap-minimal.yml`
- `README.md`
- `example_data/synthetic/test.tiff`
- `notebooks/tensionmap_example.ipynb` (added unchanged from the pinned commit
  for source verification and comparison with its saved synthetic outputs only;
  it is not executed as part of the vendored snapshot)

The files were downloaded from commit-specific `raw.githubusercontent.com` URLs.
The full paper dataset and full transcriptomics environment are deliberately not
included.

## Why this is a vendored snapshot

The preferred approach was a Git submodule, but repeated GitHub clone attempts
failed because of network timeouts/HTTP2 framing errors while retrieving the
large upstream repository. Pinning commit-specific raw files retains provenance
and reproducibility while including only the one upstream notebook needed for
the official synthetic-example reference.
