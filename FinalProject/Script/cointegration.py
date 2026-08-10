"""
CQF Final Project - TS: Pairs Trading
Cointegration Analysis Module (Engle-Granger Two-Step Method)
Author: CQF Candidate
Date: 2026
"""

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.tsa.stattools import adfuller
from statsmodels.regression.linear_model import OLS
import statsmodels.api as sm


def engle_granger_cointegration(y, x):
    """
    Engle-Granger two-step cointegration test.
    
    Step 1: Estimate long-run equilibrium relationship using OLS
            y_t = alpha + beta * x_t + epsilon_t
    Step 2: Test if residuals epsilon_t are stationary using ADF test
    
    Args:
        y: Dependent variable (RB log price)
        x: Independent variable (HC log price)
        
    Returns:
        Dictionary with cointegration results
    """
    # Convert to numpy arrays for robustness
    y_arr = np.asarray(y, dtype=float)
    x_arr = np.asarray(x, dtype=float)
    
    # Step 1: OLS regression - manually add constant
    n = len(y_arr)
    x_with_const = np.column_stack([np.ones(n), x_arr])
    model = OLS(y_arr, x_with_const)
    results = model.fit()
    
    alpha = results.params[0]
    beta = results.params[1]
    residuals = results.resid
    
    # Step 2: ADF test on residuals
    adf_result = adfuller(residuals, autolag='AIC')
    
    results_dict = {
        'alpha': alpha,
        'beta': beta,
        'residuals': np.asarray(residuals),
        'residual_mean': np.mean(residuals),
        'residual_std': np.std(residuals),
        'adf_statistic': adf_result[0],
        'adf_pvalue': adf_result[1],
        'adf_critical_values': adf_result[4],
        'r_squared': results.rsquared,
        't_stat_alpha': results.tvalues[0],
        't_stat_beta': results.tvalues[1],
        'is_cointegrated_1pct': adf_result[1] < 0.01,
        'is_cointegrated_5pct': adf_result[1] < 0.05,
        'is_cointegrated_10pct': adf_result[1] < 0.10,
    }
    
    return results_dict


def adf_test(series, name='Series'):
    """
    Perform Augmented Dickey-Fuller test for stationarity.
    
    Null hypothesis: Series has a unit root (non-stationary)
    Alternative hypothesis: Series is stationary
    
    Args:
        series: Time series data
        name: Name of the series for reporting
        
    Returns:
        Dictionary with ADF test results
    """
    result = adfuller(series.dropna(), autolag='AIC')
    
    results_dict = {
        'name': name,
        'adf_statistic': result[0],
        'p_value': result[1],
        'critical_values': result[4],
        'is_stationary_1pct': result[1] < 0.01,
        'is_stationary_5pct': result[1] < 0.05,
        'is_stationary_10pct': result[1] < 0.10,
    }
    
    return results_dict


def johansen_cointegration_test(df, variables, det_order=0, k_ar_diff=1):
    """
    Johansen cointegration test (simplified version using statsmodels).
    For multivariate cointegration analysis.
    
    Args:
        df: DataFrame with the variables
        variables: List of column names to test
        det_order: Order of deterministic terms
        k_ar_diff: Number of lags
        
    Returns:
        Dictionary with Johansen test results
    """
    from statsmodels.tsa.vector_ar.vecm import coint_johansen
    
    data = df[variables].dropna()
    result = coint_johansen(data, det_order=det_order, k_ar_diff=k_ar_diff)
    
    results_dict = {
        'trace_stat': result.trace_stat,
        'trace_crit_vals': result.trace_stat_crit_vals,
        'max_eig_stat': result.max_eig_stat,
        'max_eig_crit_vals': result.max_eig_stat_crit_vals,
        'eigenvalues': result.eig,
        'eigenvectors': result.evec,
    }
    
    return results_dict


def half_life(residuals):
    """
    Calculate half-life of mean reversion from residuals.
    
    Half-life = ln(2) / theta, where theta is the speed of mean reversion
    from the AR(1) process: delta_epsilon_t = theta * epsilon_{t-1} + noise
    
    Args:
        residuals: Residual series from cointegration regression
        
    Returns:
        Half-life in number of periods
    """
    # Estimate AR(1) coefficient
    res_series = pd.Series(residuals).dropna()
    res_lag = res_series.shift(1).dropna()
    res_diff = res_series.diff().dropna()
    
    # Align lengths
    common_idx = res_lag.index.intersection(res_diff.index)
    x = res_lag.loc[common_idx].values
    y = res_diff.loc[common_idx].values
    
    # OLS: delta_epsilon = theta * epsilon_{t-1} + error
    x_with_const = sm.add_constant(x)
    model = OLS(y, x_with_const)
    results = model.fit()
    
    theta = results.params[1]  # theta should be negative for mean reversion
    
    if theta >= 0:
        half_life_val = float('inf')  # No mean reversion
    else:
        half_life_val = -np.log(2) / theta
    
    return {
        'theta': theta,
        'half_life': half_life_val,
        'ar_coeff': 1 + theta,  # phi = 1 + theta
        'r_squared': results.rsquared,
    }


def hurst_exponent(series, max_lag=20):
    """
    Calculate Hurst exponent to determine if series is
    mean-reverting (H < 0.5), random walk (H = 0.5), or trending (H > 0.5).
    
    Args:
        series: Time series data
        max_lag: Maximum lag for R/S analysis
        
    Returns:
        Hurst exponent value
    """
    lags = range(2, max_lag)
    tau = [np.std(np.subtract(series[lag:], series[:-lag])) for lag in lags]
    
    # Linear regression on log-log scale
    reg = np.polyfit(np.log(lags), np.log(tau), 1)
    hurst = reg[0]
    
    return hurst


def variance_ratio_test(series, k=2):
    """
    Variance ratio test for random walk hypothesis.
    
    VR(k) = Var(r_k) / (k * Var(r_1))
    If VR = 1, series is a random walk
    If VR < 1, series is mean-reverting
    If VR > 1, series is trending
    
    Args:
        series: Price series
        k: Lag period
        
    Returns:
        Variance ratio and test statistic
    """
    returns = np.diff(series)
    n = len(returns)
    
    # 1-period returns
    var_1 = np.var(returns)
    
    # k-period returns
    returns_k = np.array([np.sum(returns[i:i+k]) for i in range(n - k + 1)])
    var_k = np.var(returns_k)
    
    vr = var_k / (k * var_1)
    
    # Lo-MacKinlay test statistic (homoskedastic)
    m = (n - k + 1) * (1 - k / n)
    vr_stat = (vr - 1) / np.sqrt(2 / m)
    
    return {
        'variance_ratio': vr,
        'test_statistic': vr_stat,
        'p_value': 2 * (1 - stats.norm.cdf(abs(vr_stat))),
        'is_mean_reverting': vr < 1,
        'is_trending': vr > 1,
    }


if __name__ == "__main__":
    # Test with sample data
    from data_loader import load_pair_data
    import os
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rb_path = os.path.join(base_dir, 'data', 'rb-2023-2025.csv')
    hc_path = os.path.join(base_dir, 'data', 'hc-2023-2025.csv')
    
    df = load_pair_data(rb_path, hc_path)
    
    # ADF tests on log prices
    print("=== ADF Tests on Log Prices ===")
    rb_adf = adf_test(df['rb_log'], 'RB Log Price')
    hc_adf = adf_test(df['hc_log'], 'HC Log Price')
    print(f"RB: stat={rb_adf['adf_statistic']:.4f}, p={rb_adf['p_value']:.4f}, "
          f"stationary@5%: {rb_adf['is_stationary_5pct']}")
    print(f"HC: stat={hc_adf['adf_statistic']:.4f}, p={hc_adf['p_value']:.4f}, "
          f"stationary@5%: {hc_adf['is_stationary_5pct']}")
    
    # ADF on first differences
    print("\n=== ADF Tests on First Differences (Returns) ===")
    rb_ret_adf = adf_test(df['rb_log'].diff().dropna(), 'RB Log Return')
    hc_ret_adf = adf_test(df['hc_log'].diff().dropna(), 'HC Log Return')
    print(f"RB: stat={rb_ret_adf['adf_statistic']:.4f}, p={rb_ret_adf['p_value']:.4f}, "
          f"stationary@5%: {rb_ret_adf['is_stationary_5pct']}")
    print(f"HC: stat={hc_ret_adf['adf_statistic']:.4f}, p={hc_ret_adf['p_value']:.4f}, "
          f"stationary@5%: {hc_ret_adf['is_stationary_5pct']}")
    
    # Engle-Granger cointegration
    print("\n=== Engle-Granger Cointegration Test ===")
    eg_result = engle_granger_cointegration(df['rb_log'], df['hc_log'])
    print(f"Alpha (intercept): {eg_result['alpha']:.6f}")
    print(f"Beta (hedge ratio): {eg_result['beta']:.6f}")
    print(f"ADF statistic: {eg_result['adf_statistic']:.4f}")
    print(f"ADF p-value: {eg_result['adf_pvalue']:.6f}")
    print(f"Cointegrated at 1%: {eg_result['is_cointegrated_1pct']}")
    print(f"Cointegrated at 5%: {eg_result['is_cointegrated_5pct']}")
    print(f"R-squared: {eg_result['r_squared']:.4f}")
    print(f"Residual mean: {eg_result['residual_mean']:.6f}")
    print(f"Residual std: {eg_result['residual_std']:.6f}")
    
    # Half-life
    print("\n=== Half-Life of Mean Reversion ===")
    hl_result = half_life(eg_result['residuals'])
    print(f"Theta (speed of reversion): {hl_result['theta']:.6f}")
    print(f"AR(1) coefficient: {hl_result['ar_coeff']:.6f}")
    print(f"Half-life (days): {hl_result['half_life']:.2f}")
    
    # Hurst exponent
    print("\n=== Hurst Exponent ===")
    hurst = hurst_exponent(eg_result['residuals'], max_lag=50)
    print(f"Hurst exponent: {hurst:.4f}")
    if hurst < 0.5:
        print("Interpretation: Mean-reverting series")
    elif hurst > 0.5:
        print("Interpretation: Trending / persistent series")
    else:
        print("Interpretation: Random walk")
    
    # Variance ratio test
    print("\n=== Variance Ratio Test (k=5) ===")
    vr_result = variance_ratio_test(df['rb_log'].values, k=5)
    print(f"Variance ratio: {vr_result['variance_ratio']:.4f}")
    print(f"Test statistic: {vr_result['test_statistic']:.4f}")
    print(f"P-value: {vr_result['p_value']:.4f}")
    print(f"Mean-reverting: {vr_result['is_mean_reverting']}")
