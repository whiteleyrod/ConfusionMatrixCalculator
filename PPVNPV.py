import pandas as pd
import streamlit as st
import itertools

def calculate_ppvnpv(ppv, npv, n, tolerance=1e-6, n_pathology=None):
    """
    Estimate confusion matrix values from PPV, NPV, and sample size n.
    Returns a DataFrame of possible confusion matrices.
    """
    results = []
    for tp in range(n + 1):
        for tn in range(n + 1):
            for fp in range(n + 1):
                for fn in range(n + 1):
                    if (tp + tn + fp + fn) != n:
                        continue
                    if n_pathology is not None and (tp + fn) != n_pathology:
                        continue
                    calc_ppv = tp / (tp + fp) if (tp + fp) else 0.0
                    calc_npv = tn / (tn + fn) if (tn + fn) else 0.0
                    ppv_error = abs(ppv - calc_ppv)
                    npv_error = abs(npv - calc_npv)
                    total_error = ppv_error + npv_error
                    results.append({
                        'TP': tp,
                        'TN': tn,
                        'FP': fp,
                        'FN': fn,
                        'Calculated_PPV': calc_ppv,
                        'Calculated_NPV': calc_npv,
                        'PPV_Error': ppv_error,
                        'NPV_Error': npv_error,
                        'Total_Error': total_error,
                        'Exact_Match': total_error <= tolerance
                    })
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('Total_Error').reset_index(drop=True)
    return results_df

def main():
    st.title("Confusion Matrix Estimation from PPV, NPV, n")
    ppv = st.number_input("Positive Predictive Value (PPV, 0-1)", min_value=0.0, max_value=1.0, value=0.9)
    npv = st.number_input("Negative Predictive Value (NPV, 0-1)", min_value=0.0, max_value=1.0, value=0.9)
    n = st.number_input("Sample Size (n)", min_value=1, value=100)
    n_pathology = st.number_input("Pathology Sample Size (TP + FN, optional)", min_value=0, value=0)
    if st.button("Estimate Confusion Matrix"):
        with st.spinner("Calculating..."):
            results = calculate_ppvnpv(ppv, npv, int(n), n_pathology=int(n_pathology) if n_pathology > 0 else None)
        st.write(results.head(10))
        st.success("Done!")

if __name__ == "__main__":
    main()
