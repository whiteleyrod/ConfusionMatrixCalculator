import streamlit as st
import importlib.util
import sys
from pathlib import Path
import pandas as pd  # Import pandas to fix NameError for pd.DataFrame

# Dynamically import calculate_snspn from SnSpn.py
snspn_path = Path(__file__).parent / "SnSpn.py"
spec_snspn = importlib.util.spec_from_file_location("SnSpn", snspn_path)
snspn = importlib.util.module_from_spec(spec_snspn)
sys.modules["SnSpn"] = snspn
spec_snspn.loader.exec_module(snspn)

# Dynamically import calculate_ppvnpv from PPVNPV.py
ppvnpv_path = Path(__file__).parent / "PPVNPV.py"
spec_ppvnpv = importlib.util.spec_from_file_location("PPVNPV", ppvnpv_path)
ppvnpv = importlib.util.module_from_spec(spec_ppvnpv)
sys.modules["PPVNPV"] = ppvnpv
spec_ppvnpv.loader.exec_module(ppvnpv)

# Dynamically import calculate_likelihoodratios from LikelihoodRatios.py
lr_path = Path(__file__).parent / "LikelihoodRatios.py"
spec_lr = importlib.util.spec_from_file_location("LikelihoodRatios", lr_path)
lr = importlib.util.module_from_spec(spec_lr)
sys.modules["LikelihoodRatios"] = lr
spec_lr.loader.exec_module(lr)

# Dynamically import calculate_metrics_from_counts from CountsToMetrics.py
counts_path = Path(__file__).parent / "CountsToMetrics.py"
spec_counts = importlib.util.spec_from_file_location("CountsToMetrics", counts_path)
counts = importlib.util.module_from_spec(spec_counts)
sys.modules["CountsToMetrics"] = counts
spec_counts.loader.exec_module(counts)

st.title("Diagnostic Calculator App")

# Move all input fields to the sidebar for best layout
with st.sidebar:
    st.header("Input Options")
    # Place n and n_pathology at the top
    n = st.text_input("Sample Size (n)", value="")
    n_path = st.text_input("n Pathology (number with disease) [optional]", value="")
    st.markdown("<b>Sensitivity & Specificity</b>", unsafe_allow_html=True)
    sensitivity = st.text_input("Sensitivity (0-1)", value="")
    specificity = st.text_input("Specificity (0-1)", value="")
    st.markdown("<b>PPV & NPV</b>", unsafe_allow_html=True)
    ppv = st.text_input("Positive Predictive Value (PPV, 0-1)", value="")
    npv = st.text_input("Negative Predictive Value (NPV, 0-1)", value="")
    st.markdown("<b>+LR & -LR</b>", unsafe_allow_html=True)
    plr = st.text_input("Positive Likelihood Ratio (PLR)", value="")
    nlr = st.text_input("Negative Likelihood Ratio (NLR)", value="")
    st.markdown("<b>Confusion Matrix Counts</b>", unsafe_allow_html=True)
    tp = st.text_input("True Positives (TP)", value="")
    tn = st.text_input("True Negatives (TN)", value="")
    fp = st.text_input("False Positives (FP)", value="")
    fn = st.text_input("False Negatives (FN)", value="")
    threshold = st.number_input("Exact Match Threshold (error <)", min_value=0.0, max_value=1.0, value=0.001, step=0.001, format="%f")
    if st.button("Show Usage Instructions"):
        st.markdown("""
        <b>How to use this app:</b><br><br>
        <span style='color:green'><b>Sensitivity, Specificity, n</b></span>:<br>
        Enter values for Sensitivity, Specificity, and n only. Leave all other fields blank.<br><br>
        <span style='color:blue'><b>PPV, NPV, n</b></span>:<br>
        Enter values for PPV, NPV, and n only. Leave all other fields blank.<br><br>
        <span style='color:orange'><b>+LR, -LR, n</b></span>:<br>
        Enter values for PLR, NLR, and n only. Leave all other fields blank.<br><br>
        <span style='color:purple'><b>TP, TN, FP, FN</b></span>:<br>
        Enter values for TP, TN, FP, and FN only. Leave all other fields blank.<br><br>
        <b>Threshold:</b> Use the 'Exact Match Threshold' to set the error tolerance for flagging exact matches.<br><br>
        Only one set of inputs should be filled at a time. The app will automatically detect which calculation to perform.
        """, unsafe_allow_html=True)

# Store previous results in session state
if 'history' not in st.session_state:
    st.session_state['history'] = []

# Determine which module to use based on input
use_snspn = sensitivity.strip() != "" and specificity.strip() != "" and ppv.strip() == "" and npv.strip() == "" and plr.strip() == "" and nlr.strip() == "" and n.strip() != "" and tp.strip() == "" and tn.strip() == "" and fp.strip() == "" and fn.strip() == ""
use_ppvnpv = ppv.strip() != "" and npv.strip() != "" and sensitivity.strip() == "" and specificity.strip() == "" and plr.strip() == "" and nlr.strip() == "" and n.strip() != "" and tp.strip() == "" and tn.strip() == "" and fp.strip() == "" and fn.strip() == ""
use_lr = plr.strip() != "" and nlr.strip() != "" and sensitivity.strip() == "" and specificity.strip() == "" and ppv.strip() == "" and npv.strip() == "" and n.strip() != "" and tp.strip() == "" and tn.strip() == "" and fp.strip() == "" and fn.strip() == ""
use_counts = tp.strip() != "" and tn.strip() != "" and fp.strip() != "" and fn.strip() != "" and sensitivity.strip() == "" and specificity.strip() == "" and ppv.strip() == "" and npv.strip() == "" and plr.strip() == "" and nlr.strip() == "" and n.strip() == ""

# Set up two columns in the main area: results and history
col2, col3 = st.columns([2, 1])

# In each calculation module, if n_path is provided, force TP + FN = n_path
# Example for SnSpn:
if use_snspn:
    with col2:
        st.header("Confusion Matrix Estimation from Sensitivity, Specificity, n")
        if st.button("Estimate Confusion Matrix"):
            try:
                sens_val = float(sensitivity)
                spec_val = float(specificity)
                n_val = int(float(n))
                n_path_val = int(float(n_path)) if n_path.strip() else None
                with st.spinner("Calculating using SnSpn module..."):
                    results = snspn.calculate_snspn(sens_val, spec_val, n_val, tolerance=threshold, show_progress=False, n_pathology=n_path_val)
                st.write(results.head(10))
                st.success("Done!")
                # Save only the first row as a dict with string keys
                st.session_state['history'].append(results.iloc[0].to_dict())
            except Exception as e:
                st.error(f"Error: {e}")
elif use_ppvnpv:
    with col2:
        st.header("Confusion Matrix Estimation from PPV, NPV, n")
        if st.button("Estimate Confusion Matrix"):
            try:
                ppv_val = float(ppv)
                npv_val = float(npv)
                n_val = int(float(n))
                n_path_val = int(float(n_path)) if n_path.strip() else None
                with st.spinner("Calculating using PPVNPV module..."):
                    results = ppvnpv.calculate_ppvnpv(ppv_val, npv_val, n_val, tolerance=threshold, n_pathology=n_path_val)
                st.write(results.head(10))
                st.success("Done!")
                # Save only the first row as a dict with string keys
                st.session_state['history'].append(results.iloc[0].to_dict())
            except Exception as e:
                st.error(f"Error: {e}")
elif use_lr:
    with col2:
        st.header("Confusion Matrix Estimation from Likelihood Ratios and n")
        if st.button("Estimate Confusion Matrix"):
            try:
                plr_val = float(plr)
                nlr_val = float(nlr)
                n_val = int(float(n))
                n_path_val = int(float(n_path)) if n_path.strip() else None
                with st.spinner("Calculating using LikelihoodRatios module..."):
                    results = lr.calculate_likelihoodratios(plr_val, nlr_val, n_val, tolerance=threshold, n_pathology=n_path_val)
                st.write(results.head(10))
                st.success("Done!")
                # Save only the first row as a dict with string keys
                st.session_state['history'].append(results.iloc[0].to_dict())
            except Exception as e:
                st.error(f"Error: {e}")
elif use_counts:
    with col2:
        st.header("Diagnostic Metrics from Confusion Matrix Counts")
        if st.button("Calculate Metrics"):
            try:
                tp_val = int(float(tp))
                tn_val = int(float(tn))
                fp_val = int(float(fp))
                fn_val = int(float(fn))
                with st.spinner("Calculating metrics from counts..."):
                    metrics = counts.calculate_metrics_from_counts(tp_val, tn_val, fp_val, fn_val)
                st.write(pd.DataFrame([metrics]))
                st.success("Done!")
                # Save metrics dict directly
                st.session_state['history'].append(metrics)
            except Exception as e:
                st.error(f"Error: {e}")
else:
    st.info("Please enter either Sensitivity & Specificity & n, or PPV & NPV & n, or PLR & NLR & n, or TP, TN, FP, FN. Leave the other fields blank.")

# In col3, display history as confusion matrix table
with col3:
    st.markdown("<b>Previous Results</b>", unsafe_allow_html=True)
    if 'history' in st.session_state and st.session_state['history']:
        for i, res in enumerate(st.session_state['history'][-5:][::-1], 1):
            st.markdown(f"<b>Run {len(st.session_state['history'])-i+1}</b>", unsafe_allow_html=True)
            if isinstance(res, dict):
                # Convert int keys to str for DataFrame
                res_str = {str(k): v for k, v in res.items()}
                st.write(pd.DataFrame([res_str]))
            else:
                st.write(pd.DataFrame(res))
    else:
        st.info("No previous results yet.")
