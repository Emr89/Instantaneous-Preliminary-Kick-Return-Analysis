# Instantaneous Preliminary Kick Return Analysis

Historical research by Eric Matthew Rupinski. Reconstruction status: **partial; original empirical findings have not been re-estimated**. Original research history is preserved.

## Research question and value

How much information about a kick return is already visible at reception? Distinguish return-yardage prediction from terminal-field-position modeling.

## Data and methodology

Original files remain the source of historical methodology. `data/requirements.json` inventories detected input filenames and packages; it is an incomplete static manifest, not a locked environment. Raw files are absent from this repository; authorized local source recovery is now in progress. Reacquire them through their original authorized sources; competition and third-party licenses must be checked before reuse.

## Audit and implemented changes

Saved Model LLO output gives Rsquared=0.5290068 for KR_X, the terminal x-coordinate, not return yardage. CAST groups by player role TKOP, allowing players from the same play into different folds. Console prose prevents parsing.

Commented console output; retained exact result in docs. Added identity-anchored reception features, a season holdout baseline workflow, and conventional held-out R²/MAE/RMSE.

## Metric provenance

The saved Model LLO output reports RMSE 5.896435, Rsquared 0.5290068 and MAE 3.050775 across 35,576 player rows. Its response is `KR_X`, derived from the returner x-coordinate at the tackle event. These are not 35,576 independent kick returns. The code calls `CreateSpacetimeFolds(..., spacevar="TKOP", k=3)`: this holds out role categories, not complete plays or games. The same play can cross folds. The console heading says ten folds, while the supplied fold index is built with k=3.

`caret` ordinarily reports squared correlation, which is not necessarily conventional held-out `1-SSE/SST` R². Preserve 0.529 as an archived metric, never prediction accuracy, a causal effect, or a newly validated return-yardage benchmark. See [caret metric definition](https://topepo.github.io/caret/measuring-performance.html).

The new reception baseline is a separate, deliberately simple analysis with one row per play, no actual return-direction predictors, train seasons 2018–2019 and test season 2020. It uses distances to all other tracked players, without inventing opponent assignments. Its results remain unavailable until licensed data are supplied.

## Findings and validation

No new empirical finding or revised performance score is asserted. Unit checks use small constructed inputs to verify the repaired mathematics and data contracts. Parsing verifies syntax only; it does not execute an analysis. Available original illustrations are historical outputs, not independently regenerated evidence.

## Reproduce the supported checks

R 4.5.2 was used for the base-R checks.

```sh
Rscript --vanilla tests/test_snapshot.R
BDB_DATA_DIR=/path/to/authorized/data Rscript --vanilla scripts/evaluate_reception.R
```

The original dependency set is not fully available or version locked. Successful helper tests do not establish successful execution of the original model.

## Practical applications and limits

Historical model not re-run. Test fixtures validate logic only. Missing licensed tracking/PFF inputs; old role-based CV is not independent-play validation.

## Next work

Recover input data with provenance and variable timing; declare the observational unit; isolate complete games/matches chronologically; fit transformations on training folds; compare against a simple baseline; regenerate figures and revise findings from held-out evidence. Retain old conclusions as historical until then.

## Executed local historical extension

`scripts/evaluate_local_2018.py` streams authorized local 2018 tracking data, calls the tested identity-anchored R feature helper, trains on Weeks 1–12 and evaluates only Weeks 13–17. It compares a training-mean baseline, linear regression and a fixed random forest. It records source hashes, eligibility/coverage, held-out metrics and complete-game bootstrap ranges. The full pipeline was executed after local source recovery. Results remain in the private owner review package; they are a new one-season return-yardage extension and do not re-estimate the archived terminal-position metric.

Run with `BDB_DATA_DIR=/path/to/authorized/2018/data RESEARCH_OUTPUT_DIR=/private/output python scripts/evaluate_local_2018.py`. Python dependencies are pinned in `requirements-reconstruction.txt`; Rscript and the base-R helper are also required. No source dataset or empirical result is committed to this public branch.
