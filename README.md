# PDAC-GUARD Frontend Upgrade

A modern Streamlit research dashboard for the PDAC-GUARD end-semester project. It visualizes the project's consolidated evaluation tables and provides a local dataset-audit workflow.

## What's included

- Research overview and baseline model comparison
- Case-input completeness audit (not a disease prediction)
- CSV/Excel dataset upload and schema/missingness audit
- Baseline model benchmark page
- Random-masking and biomarker-outage stress-test visuals
- Cohort-held-out and sample-origin-held-out metrics
- Calibration estimates with bootstrap confidence intervals
- Methods, reference, and limitations page
- Consolidated tables and figures from the current project report

## Important safety boundary

No verified serialized model artifact is bundled. Therefore the app **does not generate PDAC risk probabilities or a diagnosis**. The Case Readiness page only checks numeric input validity and missing-input counts. Do not use this application for clinical decisions. This is a research visualization prototype.

## Run on Windows

1. Extract the ZIP to a folder, e.g. `C:\Projects\PDAC_GUARD_Frontend_Upgrade`.
2. Open PowerShell in that folder.
3. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. Install requirements:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. Start the app:

   ```powershell
   streamlit run app.py
   ```

6. Open the local URL printed by Streamlit (normally `http://localhost:8501`).

Or double-click `run_app.bat` after installing Python; the script creates a venv if needed and starts Streamlit.

## Run on macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

## Dataset upload

The Dataset Studio accepts `.csv`, `.xlsx`, `.xlsm`, and `.xls`. For Excel, it reads a sheet named `SAMPLES` if present; otherwise it uses the first sheet. Expected predictors are:

- `Plasma CA19-9`
- `LYVE1`
- `REG1B`
- `TFF1`
- `Age`
- `Creatinine`

It recognizes `is_PDAC` as a binary target, or the common diagnosis-code column `Diagnosis (1=Control, 2=Benign, 3=PDAC)` with code 3 mapped to PDAC and codes 1/2 mapped to non-PDAC. Column names may include common assay units. Audit results are for exploratory review and do not retrain a model.

## Project data

The `data/tables/` and `data/figures/` folders contain copies of the consolidated result tables and supporting figures. If you update model results, replace the relevant CSVs with fresh outputs after reconciling column names and definitions.

## Deployment note

For a public deployment, do not upload identifiable patient data. Consider access restrictions and your university's data governance requirements before exposing an upload tool to a shared URL.
