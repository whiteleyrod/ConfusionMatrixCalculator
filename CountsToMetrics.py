import streamlit as st
import pandas as pd

def calculate_metrics_from_counts(tp, tn, fp, fn):
    """
    Calculate diagnostic metrics from confusion matrix counts.
    Returns a dictionary with sensitivity, specificity, PPV, NPV, +LR, -LR.
    """
    sensitivity = tp / (tp + fn) if (tp + fn) else 0.0
    specificity = tn / (tn + fp) if (tn + fp) else 0.0
    ppv = tp / (tp + fp) if (tp + fp) else 0.0
    npv = tn / (tn + fn) if (tn + fn) else 0.0
    plr = sensitivity / (1 - specificity) if (1 - specificity) else float('inf')
    nlr = (1 - sensitivity) / specificity if specificity else float('inf')
    return {
        'Sensitivity': sensitivity,
        'Specificity': specificity,
        'PPV': ppv,
        'NPV': npv,
        '+LR': plr,
        '-LR': nlr
    }

def main():
    st.title("Diagnostic Metrics from Confusion Matrix Counts")
    tp = st.number_input("True Positives (TP)", min_value=0, value=10)
    tn = st.number_input("True Negatives (TN)", min_value=0, value=10)
    fp = st.number_input("False Positives (FP)", min_value=0, value=5)
    fn = st.number_input("False Negatives (FN)", min_value=0, value=5)
    if st.button("Calculate Metrics"):
        metrics = calculate_metrics_from_counts(tp, tn, fp, fn)
        st.write(pd.DataFrame(metrics, index=[0]))
        st.success("Done!")

if __name__ == "__main__":
    main()
