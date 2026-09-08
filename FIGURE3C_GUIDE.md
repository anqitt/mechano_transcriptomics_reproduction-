# Figure 3c Reproduction Guide

## 1. Biological question

Figure 3c asks whether cell-cell junctions crossing a transcriptomically
defined tissue-compartment boundary carry higher inferred tension than
junctions connecting cells within either neighboring compartment. The three
comparisons are analyzed independently:

- dataset 1: embryo 1, neural crest (NC) versus
  forebrain/midbrain/hindbrain (FMH);
- dataset 2: embryo 2, cranial mesoderm (CM) versus FMH;
- dataset 3: embryo 2, midbrain versus hindbrain.

The reproduction follows the pinned official
`notebooks/01_biophysical_analysis.ipynb` at commit
`1a3ed8e940059d9e3574f21b67f340917f1bf049`.

## 2. What is a homotypic junction?

A homotypic junction connects two cells with the same
`boundary_annotation`. The official Figure 3 code additionally requires the
junction's minimum endpoint graph distance from the detected boundary to be
between 1 and 5, inclusive. Same-tissue junctions directly at the boundary
(distance 0), junctions farther than five steps away and unreachable
junctions are not part of Figure 3c.

A real example from dataset 1 is `cell_6`–`cell_16`: both cells are annotated
`Forebrain/Midbrain/Hindbrain`, their minimum boundary distance is 5, and
their inferred junction tension is 11.4417 a.u.

## 3. What is a heterotypic junction?

A heterotypic junction connects one cell from each of the two non-`Other`
compartments. The official code requires its minimum endpoint graph distance
to be 0, meaning that it lies at the detected boundary.

A real example from dataset 1 is `cell_31`–`cell_51`:
`cell_31` is FMH, `cell_51` is Neural Crest, the distance is 0, and the
precomputed tension is 223.1216 a.u.

## 4. What exactly is being compared?

For each dataset separately, the code:

1. identifies its two non-`Other` compartment labels;
2. computes each cell's boundary likelihood as the fraction of neighbors from
   tissue 1 multiplied by the fraction from tissue 2;
3. sets likelihoods below 0.15 to zero and calls positive cells boundary cells;
4. propagates graph distance outward through the nonzero adjacency network;
5. takes nonzero entries from the matrix's upper triangle, so each undirected
   junction appears once;
6. excludes every cell annotated `Other` and all junction categories not
   specified in sections 2–3;
7. compares each tissue's distance-1-to-5 homotypic tensions separately with
   the distance-0 heterotypic boundary tensions.

The matrix values are used directly. The notebook performs **no tension
normalization or transformation** before grouping, plotting or testing. It
calculates group mean, median, SEM and number of observations. Its plotting
cell uses means with SEM bars; the published panel displays violin
distributions with SEM bars. The reproduction uses the published violin form
and overlays mean ± SEM.

## 5. Results for dataset1, dataset2, dataset3

| Dataset | Group | Junctions | Mean | Median | SEM |
|---|---|---:|---:|---:|---:|
| 1 | FMH homotypic | 1,106 | 146.002 | 100.794 | 5.008 |
| 1 | NC homotypic | 505 | 158.831 | 107.960 | 8.227 |
| 1 | Heterotypic boundary | 151 | 168.863 | 117.033 | 12.354 |
| 2 | CM homotypic | 99 | 151.872 | 125.508 | 12.475 |
| 2 | FMH homotypic | 756 | 148.595 | 128.511 | 4.167 |
| 2 | Heterotypic boundary | 51 | 182.303 | 157.928 | 16.411 |
| 3 | Hindbrain homotypic | 272 | 160.635 | 142.349 | 7.406 |
| 3 | Midbrain homotypic | 222 | 140.020 | 123.808 | 6.737 |
| 3 | Heterotypic boundary | 29 | 199.079 | 206.512 | 18.785 |

Combined homotypic counts are 1,611, 855 and 494 for datasets 1–3,
respectively. The official analysis, however, keeps the two homotypic tissues
as separate plotted and tested groups rather than pooling them.

## 6. What does “12–35% lower” mean?

A conventional tissue-specific mean calculation is:

```text
percent lower = (boundary mean − homotypic mean) / boundary mean × 100
```

It gives:

| Dataset | Homotypic tissue | Percent below boundary mean |
|---|---|---:|
| 1 | FMH | 13.54% |
| 1 | NC | 5.94% |
| 2 | CM | 16.69% |
| 2 | FMH | 18.49% |
| 3 | Hindbrain | 19.31% |
| 3 | Midbrain | 29.67% |

Neither the paper nor the public notebook specifies the exact arithmetic used
to produce the textual “approximately 12–35%” range, and the notebook contains
no percent-difference calculation. The directly reproduced tissue-specific
mean range is therefore 5.94–29.67%, not exactly 12–35%.

For context, pooling both homotypic groups within each dataset gives mean
decreases of 11.16%, 18.28% and 23.96%. An unweighted average of the two
homotypic medians compared with the heterotypic median gives 10.81%, 19.58%
and 35.56%, which is close to the paper's approximate dataset-level wording.
That median-based reconstruction is an inference, not a formula documented by
the authors, and was not substituted for the official group summaries.

## 7. Statistical evidence

The figure caption specifies one-sided pairwise Mann–Whitney U tests. The
alternative tested here is that each homotypic distribution tends to have
lower values than its dataset's heterotypic boundary distribution.

| Dataset | Comparison | U | One-sided P value |
|---|---|---:|---:|
| 1 | FMH < boundary | 73,399 | 0.007875 |
| 1 | NC < boundary | 34,806 | 0.052046 |
| 2 | CM < boundary | 2,056 | 0.031676 |
| 2 | FMH < boundary | 15,720 | 0.013625 |
| 3 | Hindbrain < boundary | 2,823 | 0.005954 |
| 3 | Midbrain < boundary | 2,019 | 0.000553 |

In plain language, five comparisons have P < 0.05 under the stated one-sided
test. Dataset 1's NC comparison is just above that conventional threshold.
Its reproduced P = 0.052 matches the value printed in the published panel,
providing a useful check on the grouping and test direction. A P value is not
the probability that the biological hypothesis is true; it measures how
surprising the observed rank separation would be under the test's null model.

## 8. Biological meaning

The data directly show that the heterotypic boundary group has the highest
mean inferred junction tension in all three datasets. Five of six one-sided
pairwise rank tests meet P < 0.05.

The authors interpret this pattern as high heterotypic interfacial tension
(HIT), which could help neighboring embryonic compartments maintain a sharp
interface by making cross-boundary contacts mechanically unfavorable. That is
a biologically plausible interpretation supported by the paper's additional
modeling, but this observational comparison alone does not establish the
molecular cause or prove that elevated tension is necessary or sufficient for
boundary maintenance in vivo.

Mechanistic validation would require perturbing candidate adhesion or
contractility pathways, directly measuring forces, and showing the predicted
effect on both junction tension and tissue-boundary behavior.

## 9. What Figure 3c does NOT prove

- It does not independently validate the segmentation, cell-type annotation
  or VMSI estimates; Step 4C uses the authors' processed outputs.
- Junctions within a tissue share cells and spatial context, so they are not
  guaranteed to be independent biological replicates.
- Only three selected brain regions from two embryos are analyzed; the three
  datasets are not three independent embryos.
- The one-sided tests assess predefined directional comparisons and do not by
  themselves correct for the six pairwise tests.
- The code-defined graph-distance and boundary-likelihood thresholds affect
  which junctions enter the panel.
- The approximate 12–35% wording lacks an explicit calculation in the public
  code, so alternative summaries can produce somewhat different percentages.

The committed `junction_tension_analysis.csv` is the complete auditable
junction-level input to the summaries above. `group_summary.csv`,
`pairwise_tests.csv` and `run_summary.json` preserve the numerical and sanity
checks generated by `reproduce_figure3c.py`.
