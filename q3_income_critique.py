import numpy as np
import pandas as pd

def calculate_gini(income_array):
    """Calculates the Gini Coefficient of a 1D NumPy array."""
    # Elements must be sorted
    sorted_income = np.sort(income_array)
    n = len(income_array)
    # Construct index coefficients
    coefs = 2 * np.arange(1, n + 1) - n - 1
    # Standard Gini formulation
    gini = np.sum(coefs * sorted_income) / (n * np.sum(sorted_income))
    return gini

def robust_income_analysis(incomes):
    """Computes and compares standard statistics with robust metrics."""
    incomes = np.array(incomes)
    
    # 1. Classical Metrics
    mean = np.mean(incomes)
    std_dev = np.std(incomes)
    lower_bound_classical = mean - (2 * std_dev)
    
    # 2. Robust Metrics
    median = np.median(incomes)
    q1 = np.percentile(incomes, 25)
    q3 = np.percentile(incomes, 75)
    iqr = q3 - q1
    
    # 3. Structural Inequality Metrics
    gini = calculate_gini(incomes)
    
    # Palma Ratio: Top 10% total income / Bottom 40% total income
    sorted_inc = np.sort(incomes)
    n = len(sorted_inc)
    top_10_boundary = int(n * 0.90)
    bottom_40_boundary = int(n * 0.40)
    
    top_10_share = np.sum(sorted_inc[top_10_boundary:])
    bottom_40_share = np.sum(sorted_inc[:bottom_40_boundary])
    palma_ratio = top_10_share / bottom_40_share if bottom_40_share != 0 else np.nan
    
    return {
        "Mean": mean, "Std_Dev": std_dev, "Classical_2SD_Bound": lower_bound_classical,
        "Median": median, "Q1": q1, "Q3": q3, "IQR": iqr,
        "Gini_Index": gini, "Palma_Ratio": palma_ratio
    }

# --- Execution Setup ---
if __name__ == "__main__":
    # Generate Pareto-distributed income data (Shape alpha=1.16, representing highly skewed wealth)
    # High shape value mirrors typical urban economies
    np.random.seed(10)
    simulated_population = 10000
    # Minimum wage offset parameter
    min_wage = 15000 
    raw_incomes = (np.random.pareto(a=1.16, size=simulated_population) + 1) * min_wage
    
    metrics = robust_income_analysis(raw_incomes)
    
    print("=== Income Distribution Analysis Report ===")
    print("\n--- Standard Statistics (Non-Robust) ---")
    print(f"Mean Income:         ${metrics['Mean']:,.2f}")
    print(f"Standard Deviation:  ${metrics['Std_Dev']:,.2f}")
    print(f"Classical Lower Bound (Mean - 2*SD): ${metrics['Classical_2SD_Bound']:,.2f} (Nonsensical value)")
    
    print("\n--- Robust Statistics (Proposed Framework) ---")
    print(f"Median Income:       ${metrics['Median']:,.2f}")
    print(f"IQR (Q1 to Q3):      ${metrics['Q1']:,.2f} to ${metrics['Q3']:,.2f} (Spread: ${metrics['IQR']:,.2f})")
    
    print("\n--- Structural Inequality Metrics ---")
    print(f"Gini Coefficient:    {metrics['Gini_Index']:.4f} (Ideal equality: 0, Extreme: 1)")
    print(f"Palma Ratio:         {metrics['Palma_Ratio']:.4f} (Wealth concentrated in top 10% vs bottom 40%)")