# Diagnostic Calculator App

This Streamlit app allows you to calculate and estimate diagnostic test statistics from various input types:
- Sensitivity, Specificity, and n
- PPV, NPV, and n
- Positive/Negative Likelihood Ratios and n
- Confusion matrix counts (TP, TN, FP, FN)

## Usage
- Fill in only one set of input fields at a time in the sidebar.
- Click the appropriate button to run the calculation.
- Results and a history of previous runs will be displayed in the main area.

## Deployment
- This app is ready for deployment on Streamlit Cloud.
- All dependencies are listed in `requirements.txt`.

## Files
- `app.py` — Main Streamlit app
- `SnSpn.py`, `PPVNPV.py`, `LikelihoodRatios.py`, `CountsToMetrics.py` — Calculation modules
- `requirements.txt` — Python dependencies

---

For questions or issues, contact the developer.
