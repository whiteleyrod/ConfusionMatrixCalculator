import pandas as pd
import streamlit as st
import itertools

def calculate_likelihoodratios(plr, nlr, n, tolerance=1e-6, n_pathology=None):
    """
    Estimate confusion matrix values from positive and negative likelihood ratios and sample size n.
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
                    # Avoid division by zero
                    sens = tp / (tp + fn) if (tp + fn) else 0.0
                    spec = tn / (tn + fp) if (tn + fp) else 0.0
                    calc_plr = sens / (1 - spec) if (1 - spec) else float('inf')
                    calc_nlr = (1 - sens) / spec if spec else float('inf')
                    plr_error = abs(plr - calc_plr)
                    nlr_error = abs(nlr - calc_nlr)
                    total_error = plr_error + nlr_error
                    results.append({
                        'TP': tp,
                        'TN': tn,
                        'FP': fp,
                        'FN': fn,
                        'Calculated_PLR': calc_plr,
                        'Calculated_NLR': calc_nlr,
                        'PLR_Error': plr_error,
                        'NLR_Error': nlr_error,
                        'Total_Error': total_error,
                        'Exact_Match': total_error <= tolerance
                    })
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('Total_Error').reset_index(drop=True)
    return results_df

def main():
    st.title("Confusion Matrix Estimation from Likelihood Ratios and n")
    plr = st.number_input("Positive Likelihood Ratio (PLR)", min_value=0.0, value=5.0)
    nlr = st.number_input("Negative Likelihood Ratio (NLR)", min_value=0.0, value=0.2)
    n = st.number_input("Sample Size (n)", min_value=1, value=100)
    n_pathology = st.number_input("Pathology Sample Size (TP + FN)", min_value=0, value=0)
    if st.button("Estimate Confusion Matrix"):
        with st.spinner("Calculating..."):
            results = calculate_likelihoodratios(plr, nlr, int(n), n_pathology=int(n_pathology))
        st.write(results.head(10))
        st.success("Done!")

if __name__ == "__main__":
    main()
