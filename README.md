# Alpha Traore | Python Storm Data Analysis

A reproducible Python/pandas portfolio translating SAS-style analytics into data ingestion, preparation, validated joins, descriptive statistics, visualization, and automated Excel/CSV reporting.

[Live portfolio](https://python.alphatraore.com) · [GitHub repository](https://github.com/alphatraore/python-storm-data-analysis)

## Verified outcomes

| Evidence | Result |
|---|---:|
| Notebook code cells executed | 80 |
| Combined summary records | 3,172 |
| Detailed observations | 50,764 |
| 2016 wind summaries by season/basin/name | 90 |
| Damage events uniquely linked | 38 of 38 |
| Duplicate complete StormIDs | 0 |

The supplied raw inputs are included. Independently recomputed wind statistics and damage results agree with regenerated outputs. See [QC evidence](qc-results.json) and [execution evidence](output/tables/notebook_execution.json).

## Analytical purpose

- Compare 2016 storm activity across basins to guide geographic review.
- Identify storm groups with stronger recorded winds for closer examination.
- Rank reported damage costs among the supplied historical events.

These results support historical exploration. They are descriptive, not forecasts or causal estimates. Costs are not adjusted for inflation, exposure, or differences in reporting.

## Reproduce the analysis

Use Python 3.12. From the repository root:

```bash
python -m venv .venv
```

Activate the environment on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Or on macOS/Linux:

```bash
source .venv/bin/activate
```

Then run:

```bash
python -m pip install -r requirements.txt
python run_notebook.py
python validate_portfolio.py .
```

The runner executes every Python code cell sequentially using Matplotlib Agg and a tabular display shim; it does not use a Jupyter kernel. It writes executed cell outputs back to the notebook and regenerates tables, reports, charts, and execution evidence. It records failures with the failing cell, clears previous execution state, and restores the caller's working directory. Notebook plots are saved as PNGs; this runner does not embed plot images into notebook outputs.

The notebook can also be used interactively in a separately installed Jupyter/VS Code notebook environment. Open it from the repository root or `notebooks/`.

## Identity and missing-data policy

Complete summary identifiers combine season, basin, and normalized storm name. The 35 duplicate season/name occurrences were collisions in a weaker identifier; they are not duplicate complete storm records.

- Retain all summary records. Separately audit 80 incomplete identities.
- Exclude 70 ambiguous season/name candidates from damage-link eligibility because the damage input lacks basin; never choose an arbitrary candidate.
- Enforce a many-to-one merge, audit every input damage event, and preserve unmatched/ambiguous statuses if future data introduces them. All 38 supplied events match uniquely.
- Group wind by season, basin, and name. The 60 detail observations with incomplete group identifiers are excluded from these summaries and reported.
- Retain 23 missing summary maximum-wind values without imputation.

Detail `Wind` units are not confirmed; do not label those statistics mph. Summary `MaxWindMPH` is explicitly named in mph. See [data notes](DATA_NOTES.md).

## Repository contents

| Path | Purpose |
|---|---|
| `data/raw/` | Original supplied SAS and Excel inputs |
| `data/processed/` | Prepared summary and matched damage data |
| `notebooks/python-storm-data-analysis.ipynb` | Complete analytical workflow |
| `run_notebook.py` | Headless sequential code-cell runner |
| `validate_portfolio.py` | Independent output checks |
| `output/tables/` | CSV audits, statistical tables, Excel report, execution evidence |
| `output/figures/` | Basin chart and North Atlantic scatter figure |
| `requirements.txt` | Exact dependency versions used in this verification |
| `.github/workflows/validate.yml` | Reproduction and validation on pushes and pull requests |

This repository package contains analysis source; the Hostinger website is a separate static deliverable. Running a web server here does not launch the portfolio website.

## Validation coverage

Validation independently recalculates wind summaries and damage matches from raw inputs, checks durations and export consistency, confirms complete StormID uniqueness and damage-row conservation, and verifies input hashes against the execution record. A failure exits with an error. The GitHub workflow is included but has not been executed on GitHub yet.

## Upload to GitHub

Extract this ZIP and upload its contents at the repository root, preserving the folders. Replace matching files. Include `.github/workflows/validate.yml` to enable automated checks. Do not upload the ZIP itself or add a surrounding project folder.

Suggested commit message: `Make storm analysis reproducible and independently validate outputs`

## Skills demonstrated

Python, pandas, NumPy, Matplotlib, openpyxl, SAS/Excel ingestion, filtering, transformations, grouping, joins, missing-data auditing, validation, and report automation. This project demonstrates Python analytics and translation of SAS concepts; it does not claim a machine-learning model or an implemented SQL pipeline.
