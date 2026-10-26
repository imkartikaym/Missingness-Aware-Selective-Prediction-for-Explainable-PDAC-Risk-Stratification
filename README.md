# PDAC-GUARD 🧬
### Missingness-Aware Selective Prediction for Explainable Pancreatic Ductal Adenocarcinoma (PDAC) Risk Stratification

PDAC-GUARD is a research-focused machine learning and analytics dashboard designed to investigate pancreatic cancer biomarker data, missing-data robustness, selective prediction, cohort shift, and model calibration.

Built using Python and Streamlit, the project explores how incomplete biomarker measurements and differences between patient cohorts can affect model performance and reliability.

> **Disclaimer:** PDAC-GUARD is an academic research prototype, not a clinically validated diagnostic tool. It must not be used to diagnose cancer or guide medical decisions.

## Key Features

- **Model Benchmarking:** Compare Logistic Regression, Random Forest, XGBoost, and Soft Voting models.
- **Missingness Analysis:** Investigate missing biomarker patterns and evaluate performance under simulated missing-data scenarios.
- **Selective Prediction:** Explore confidence-based and biomarker-availability-based abstention strategies.
- **Cohort-Shift Evaluation:** Assess model performance across available dataset groups.
- **Calibration Analysis:** Examine probability calibration using metrics such as Brier score and Expected Calibration Error (ECE).
- **Interactive Dashboard:** Explore research results and dataset characteristics through a Streamlit interface.
- **Dataset Auditing:** Review data completeness, class distribution, and cohort-level patterns.

## Research Objectives

1. Evaluate machine learning approaches for PDAC biomarker-based risk stratification.
2. Investigate the effect of missing biomarker measurements on predictive performance.
3. Explore selective prediction strategies that allow a model to abstain when evidence is insufficient.
4. Compare model performance across different dataset cohorts.
5. Examine calibration and reliability alongside discrimination metrics.

## Dataset

The project uses the Debernardi pancreatic cancer biomarker dataset, containing urine biomarker measurements and clinical variables.

**Selected features:**
- CA19-9
- LYVE1
- REG1B
- TFF1
- Age
- Creatinine

The analysed dataset contains 590 labelled records after excluding records with missing diagnoses. CA19-9 has substantial missingness, making it a key variable in the missing-data analysis.

Use the original dataset source and comply with its licensing and usage conditions when redistributing data. Do not upload sensitive or restricted patient information.

## Technology Stack

- **Language:** Python
- **Dashboard:** Streamlit
- **Data processing:** Pandas, NumPy
- **Machine learning:** Scikit-learn, XGBoost
- **Visualisation:** Matplotlib, Plotly
- **Development:** Visual Studio Code, Git, GitHub

## Project Structure

```text
PDAC-GUARD/
├── app.py
├── requirements.txt
├── README.md
└── data/
    └── Place permitted dataset files here
```

*The structure above is a suggested layout. Adjust it to match the files actually included in your repository.*

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/PDAC-GUARD.git
cd PDAC-GUARD
```

Replace `YOUR-USERNAME` with your GitHub username.

### 2. Create a virtual environment

```bash
py -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run the dashboard

```bash
streamlit run app.py
```

Open the local URL displayed in the terminal, usually `http://localhost:8501`.

## Evaluation Approach

The research investigates several complementary dimensions:

| Evaluation area | Purpose |
|---|---|
| Discrimination | Evaluate the ability to rank PDAC and non-PDAC cases |
| Missingness robustness | Assess performance when biomarker measurements are unavailable |
| Selective prediction | Study abstention and coverage-risk trade-offs |
| Cohort shift | Examine performance differences across dataset groups |
| Calibration | Assess the reliability of predicted probabilities |

Results should be interpreted in the context of cohort size, class prevalence, missingness patterns, and evaluation design. Group-held-out evaluation within this dataset does not constitute independent external clinical validation.

## Current Project Status

**Status: Research prototype**

The dashboard supports research exploration and analysis of pre-generated experimental results. A verified, serialized predictive model is not currently integrated into the frontend as a live clinical prediction system.

Future work may include:
- Independent external validation on an appropriate dataset.
- Improved missingness-aware evaluation methods.
- More robust calibration assessment.
- Transparent abstention policies and coverage-risk analysis.
- Reproducible experiments and expanded documentation.

## Ethical Considerations

Pancreatic cancer prediction is a high-stakes application. Model performance can be affected by dataset composition, missing measurements, cohort differences, and class imbalance. Results presented by this project are experimental and must not be interpreted as medical advice or evidence of clinical readiness.

## Author

**Kartikay Mathur**  
B.Tech Biotechnology & Chemical Engineering  
Manipal University Jaipur

GitHub: [@imkartikaym](https://github.com/imkartikaym)

## Contributions

Suggestions, issues, and research discussions are welcome. Please open an issue to discuss potential improvements or methodological questions.

## License

Choose and add an appropriate open-source license before distributing the repository. Ensure that the dataset and any third-party components permit your intended use.

---

*PDAC-GUARD — Exploring reliable, explainable, and missingness-aware machine learning for biomedical research.*
