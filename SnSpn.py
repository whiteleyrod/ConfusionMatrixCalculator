import itertools
import pandas as pd
import numpy as np
try:
    from tqdm import tqdm
except ImportError:
    tqdm = lambda *a, **k: a[0] if a else None

# Streamlit import is optional for standalone use
try:
    import streamlit as st
except ImportError:
    st = None

def calculate_snspn(sensitivity, specificity, sample_size, tolerance=1e-6, show_progress=True, n_pathology=None):
    """
    Estimate original confusion matrix values from sensitivity, specificity, and sample size.
    Returns a DataFrame of possible confusion matrices.
    """
    results = []
    total_iterations = (sample_size + 1) ** 4
    if show_progress and tqdm:
        progress = tqdm(total=total_iterations, desc="Testing combinations")
    else:
        progress = None
    for tp in range(sample_size + 1):
        for tn in range(sample_size + 1):
            for fp in range(sample_size + 1):
                for fn in range(sample_size + 1):
                    if progress: progress.update(1)
                    if (tp + tn + fp + fn) != sample_size:
                        continue
                    if n_pathology is not None and (tp + fn) != n_pathology:
                        continue
                    calc_sens = tp / (tp + fn) if (tp + fn) else 0.0
                    calc_spec = tn / (tn + fp) if (tn + fp) else 0.0
                    sens_error = abs(sensitivity - calc_sens)
                    spec_error = abs(specificity - calc_spec)
                    total_error = sens_error + spec_error
                    results.append({
                        'TP': tp,
                        'TN': tn,
                        'FP': fp,
                        'FN': fn,
                        'Calculated_Sensitivity': calc_sens,
                        'Calculated_Specificity': calc_spec,
                        'Sensitivity_Error': sens_error,
                        'Specificity_Error': spec_error,
                        'Total_Error': total_error,
                        'Exact_Match': total_error <= tolerance
                    })
    if progress: progress.close()
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('Total_Error').reset_index(drop=True)
    return results_df
    """
    A class to estimate original confusion matrix values from sensitivity, specificity, and sample size.
    """
    
    def __init__(self, sensitivity, specificity, sample_size):
        """
        Initialize the estimator with given parameters.
        
        Args:
            sensitivity (float): True positive rate (0-1)
            specificity (float): True negative rate (0-1)
            sample_size (int): Total number of samples
        """
        self.sensitivity = sensitivity
        self.specificity = specificity
        self.sample_size = sample_size
        self.results = []
        
    def calculate_metrics(self, tp, tn, fp, fn):
        """
        Calculate sensitivity and specificity from confusion matrix values.
        
        Args:
            tp (int): True positives
            tn (int): True negatives
            fp (int): False positives
            fn (int): False negatives
            
        Returns:
            tuple: (calculated_sensitivity, calculated_specificity)
        """
        # Avoid division by zero
        if (tp + fn) == 0:
            calc_sensitivity = 0.0
        else:
            calc_sensitivity = tp / (tp + fn)
            
        if (tn + fp) == 0:
            calc_specificity = 0.0
        else:
            calc_specificity = tn / (tn + fp)
            
        return calc_sensitivity, calc_specificity
    
    def is_valid_combination(self, tp, tn, fp, fn):
        """
        Check if a combination of confusion matrix values is valid.
        
        Args:
            tp, tn, fp, fn (int): Confusion matrix values
            
        Returns:
            bool: True if combination sums to sample_size
        """
        return (tp + tn + fp + fn) == self.sample_size
    
    def calculate_errors(self, calc_sensitivity, calc_specificity):
        """
        Calculate absolute errors between target and calculated metrics.
        
        Args:
            calc_sensitivity (float): Calculated sensitivity
            calc_specificity (float): Calculated specificity
            
        Returns:
            tuple: (sensitivity_error, specificity_error, total_error)
        """
        sens_error = abs(self.sensitivity - calc_sensitivity)
        spec_error = abs(self.specificity - calc_specificity)
        total_error = sens_error + spec_error
        
        return sens_error, spec_error, total_error
    
    def estimate_confusion_matrix(self, tolerance=1e-6):
        """
        Estimate original confusion matrix values by testing all possible combinations.
        
        Args:
            tolerance (float): Tolerance for considering a match "exact"
            
        Returns:
            pd.DataFrame: Results sorted by total error
        """
        self.results = []
        
        # Calculate total iterations for progress bar
        total_iterations = (self.sample_size + 1) ** 4
        
        print(f"Estimating confusion matrix values...")
        print(f"Target Sensitivity: {self.sensitivity:.4f}")
        print(f"Target Specificity: {self.specificity:.4f}")
        print(f"Sample Size: {self.sample_size}")
        print(f"Testing {total_iterations:,} combinations...\n")
        
        # Use tqdm to show progress through all combinations
        with tqdm(total=total_iterations, desc="Testing combinations") as pbar:
            for tp in range(self.sample_size + 1):
                for tn in range(self.sample_size + 1):
                    for fp in range(self.sample_size + 1):
                        for fn in range(self.sample_size + 1):
                            pbar.update(1)
                            
                            # Skip invalid combinations
                            if not self.is_valid_combination(tp, tn, fp, fn):
                                continue
                            
                            # Calculate metrics for this combination
                            calc_sens, calc_spec = self.calculate_metrics(tp, tn, fp, fn)
                            
                            # Calculate errors
                            sens_error, spec_error, total_error = self.calculate_errors(calc_sens, calc_spec)
                            
                            # Store result
                            self.results.append({
                                'TP': tp,
                                'TN': tn,
                                'FP': fp,
                                'FN': fn,
                                'Calculated_Sensitivity': calc_sens,
                                'Calculated_Specificity': calc_spec,
                                'Sensitivity_Error': sens_error,
                                'Specificity_Error': spec_error,
                                'Total_Error': total_error,
                                'Exact_Match': total_error <= tolerance
                            })
        
        # Convert to DataFrame and sort by total error
        results_df = pd.DataFrame(self.results)
        results_df = results_df.sort_values('Total_Error').reset_index(drop=True)
        
        return results_df
    
    def display_results(self, results_df, top_n=10):
        """
        Display the best results in a formatted way.
        
        Args:
            results_df (pd.DataFrame): Results from estimation
            top_n (int): Number of top results to display
        """
        print(f"\n{'='*80}")
        print(f"ESTIMATION RESULTS")
        print(f"{'='*80}")
        
        # Check for exact matches
        exact_matches = results_df[results_df['Exact_Match'] == True]
        
        if len(exact_matches) > 0:
            print(f"\n🎯 EXACT MATCHES FOUND: {len(exact_matches)}")
            print("-" * 50)
            for idx, row in exact_matches.head().iterrows():
                print(f"TP: {row['TP']:3d}, TN: {row['TN']:3d}, FP: {row['FP']:3d}, FN: {row['FN']:3d}")
                print(f"   Sensitivity: {row['Calculated_Sensitivity']:.6f}")
                print(f"   Specificity: {row['Calculated_Specificity']:.6f}")
                print()
        else:
            print(f"\n📊 TOP {top_n} CLOSEST ESTIMATES:")
            print("-" * 50)
            
            for idx, row in results_df.head(top_n).iterrows():
                print(f"Rank {idx+1}:")
                print(f"   TP: {row['TP']:3d}, TN: {row['TN']:3d}, FP: {row['FP']:3d}, FN: {row['FN']:3d}")
                print(f"   Calculated Sensitivity: {row['Calculated_Sensitivity']:.6f} (error: {row['Sensitivity_Error']:.6f})")
                print(f"   Calculated Specificity: {row['Calculated_Specificity']:.6f} (error: {row['Specificity_Error']:.6f})")
                print(f"   Total Error: {row['Total_Error']:.6f}")
                print()
        
        # Summary statistics
        print(f"📈 SUMMARY STATISTICS:")
        print("-" * 50)
        print(f"Total valid combinations tested: {len(results_df):,}")
        print(f"Best total error: {results_df['Total_Error'].min():.8f}")
        print(f"Average total error: {results_df['Total_Error'].mean():.8f}")
        print(f"Median total error: {results_df['Total_Error'].median():.8f}")



def main():
    """
    Main function for standalone or Streamlit use.
    """
    if st:
        st.title("Confusion Matrix Estimator (Sn/Sp/n)")
        sensitivity = st.number_input("Sensitivity (0-1)", min_value=0.0, max_value=1.0, value=0.85)
        specificity = st.number_input("Specificity (0-1)", min_value=0.0, max_value=1.0, value=0.92)
        sample_size = st.number_input("Sample Size (n)", min_value=1, value=100)
        n_pathology = st.number_input("N Pathology (TP+FN, optional)", min_value=0, value=0, step=1)
        if st.button("Estimate Confusion Matrix"):
            with st.spinner("Calculating..."):
                results = calculate_snspn(sensitivity, specificity, int(sample_size), show_progress=False, n_pathology=int(n_pathology) if n_pathology > 0 else None)
            st.write(results.head(10))
            st.success("Done!")
    else:
        # CLI/Notebook usage
        sensitivity = 0.80
        specificity = 0.70588
        sample_size = 37
        print(f"Estimating for Sensitivity={sensitivity}, Specificity={specificity}, n={sample_size}")
        results = calculate_snspn(sensitivity, specificity, sample_size)
        print(results.head(10))
        return results


if __name__ == "__main__":
    main()