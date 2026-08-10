"""
CQF Final Project - TS: Pairs Trading
Ornstein-Uhlenbeck Process Fitting Module
Author: CQF Candidate
Date: 2026
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import norm


def fit_ou_process(residuals, dt=1.0):
    """
    Fit an Ornstein-Uhlenbeck process to the residual series.
    
    OU SDE: dX_t = theta * (mu - X_t) * dt + sigma * dW_t
    
    Discrete form: X_{t+dt} - X_t = theta * (mu - X_t) * dt + sigma * sqrt(dt) * Z_t
    
    Args:
        residuals: Residual series from cointegration
        dt: Time step (default 1 day)
        
    Returns:
        Dictionary with OU parameters
    """
    x = np.array(residuals, dtype=float)
    n = len(x)
    
    # Method 1: Maximum Likelihood Estimation (MLE)
    # Log-likelihood function for OU process
    def neg_log_likelihood(params):
        theta, mu, sigma = params
        if theta <= 0 or sigma <= 0:
            return 1e10
        
        # Transition density is Gaussian
        # E[X_{t+dt} | X_t] = X_t * exp(-theta*dt) + mu * (1 - exp(-theta*dt))
        # Var[X_{t+dt} | X_t] = sigma^2 / (2*theta) * (1 - exp(-2*theta*dt))
        
        exp_theta_dt = np.exp(-theta * dt)
        mean = x[:-1] * exp_theta_dt + mu * (1 - exp_theta_dt)
        var = sigma**2 / (2 * theta) * (1 - np.exp(-2 * theta * dt))
        
        if var <= 0:
            return 1e10
        
        log_lik = -0.5 * np.sum(np.log(2 * np.pi * var) + (x[1:] - mean)**2 / var)
        return -log_lik
    
    # Initial guess from simple regression
    dx = np.diff(x)
    x_lag = x[:-1]
    beta_0 = np.mean(dx)
    beta_1 = np.cov(x_lag, dx)[0, 1] / np.var(x_lag)
    theta_init = -beta_1 / dt
    mu_init = beta_0 / (theta_init * dt) if theta_init != 0 else 0
    sigma_init = np.std(dx) / np.sqrt(dt)
    
    if theta_init <= 0:
        theta_init = 0.1
    if mu_init == 0:
        mu_init = np.mean(x)
    
    # MLE optimization
    x0 = [theta_init, mu_init, sigma_init]
    bounds = [(1e-6, None), (None, None), (1e-6, None)]
    
    result = minimize(neg_log_likelihood, x0, method='L-BFGS-B', bounds=bounds)
    
    theta_mle, mu_mle, sigma_mle = result.x
    
    # Method 2: Analytical solution (least squares)
    # dx_t = a + b * x_t + epsilon_t
    # where a = theta*mu*dt, b = -theta*dt
    x_with_const = np.column_stack([np.ones(n-1), x[:-1]])
    beta = np.linalg.lstsq(x_with_const, dx, rcond=None)[0]
    
    a_ls = beta[0]
    b_ls = beta[1]
    
    theta_ls = -b_ls / dt
    mu_ls = a_ls / (theta_ls * dt) if theta_ls != 0 else np.mean(x)
    residuals_ls = dx - (a_ls + b_ls * x[:-1])
    sigma_ls = np.std(residuals_ls) / np.sqrt(dt)
    
    # Calculate half-life
    if theta_mle > 0:
        half_life_mle = np.log(2) / theta_mle
    else:
        half_life_mle = float('inf')
    
    if theta_ls > 0:
        half_life_ls = np.log(2) / theta_ls
    else:
        half_life_ls = float('inf')
    
    # Long-term mean and equilibrium
    # Mean of stationary distribution = mu
    # Variance of stationary distribution = sigma^2 / (2*theta)
    if theta_mle > 0:
        var_stationary = sigma_mle**2 / (2 * theta_mle)
    else:
        var_stationary = np.var(x)
    
    std_stationary = np.sqrt(var_stationary)
    
    return {
        'theta_mle': theta_mle,
        'mu_mle': mu_mle,
        'sigma_mle': sigma_mle,
        'theta_ls': theta_ls,
        'mu_ls': mu_ls,
        'sigma_ls': sigma_ls,
        'half_life_mle': half_life_mle,
        'half_life_ls': half_life_ls,
        'mean_stationary': mu_mle,
        'std_stationary': std_stationary,
        'var_stationary': var_stationary,
        'log_likelihood': -result.fun,
        'converged': result.success,
    }


def ou_simulate(theta, mu, sigma, x0, n_steps, dt=1.0, seed=None):
    """
    Simulate an Ornstein-Uhlenbeck process.
    
    Args:
        theta: Speed of mean reversion
        mu: Long-term mean
        sigma: Volatility
        x0: Initial value
        n_steps: Number of time steps
        dt: Time step
        seed: Random seed
        
    Returns:
        Simulated OU process array
    """
    if seed is not None:
        np.random.seed(seed)
    
    x = np.zeros(n_steps)
    x[0] = x0
    
    exp_theta_dt = np.exp(-theta * dt)
    std_increment = sigma * np.sqrt((1 - np.exp(-2 * theta * dt)) / (2 * theta))
    
    for i in range(1, n_steps):
        x[i] = x[i-1] * exp_theta_dt + mu * (1 - exp_theta_dt) + std_increment * np.random.randn()
    
    return x


def ou_crossing_probability(x, threshold, theta, mu, sigma, dt=1.0):
    """
    Calculate probability of crossing threshold within one time step
    using the OU transition density.
    
    Args:
        x: Current value
        threshold: Threshold level
        theta: Speed of mean reversion
        mu: Long-term mean
        sigma: Volatility
        dt: Time step
        
    Returns:
        Probability of crossing threshold
    """
    exp_theta_dt = np.exp(-theta * dt)
    mean_next = x * exp_theta_dt + mu * (1 - exp_theta_dt)
    std_next = sigma * np.sqrt((1 - np.exp(-2 * theta * dt)) / (2 * theta))
    
    if x < threshold:
        prob = 1 - norm.cdf(threshold, loc=mean_next, scale=std_next)
    else:
        prob = norm.cdf(threshold, loc=mean_next, scale=std_next)
    
    return prob


def ou_expected_time_to_mean(x, theta, mu):
    """
    Expected time to reach mean level from current value.
    
    For OU process, expected time to reach mu from x is approximately:
    E[T] ≈ ln(|x - mu| / epsilon) / theta  (for small epsilon)
    
    More precisely, we use the first passage time approximation.
    
    Args:
        x: Current value
        theta: Speed of mean reversion
        mu: Long-term mean
        
    Returns:
        Expected time to reach mean (in dt units)
    """
    distance = abs(x - mu)
    if distance < 1e-10:
        return 0.0
    
    # Approximate expected time to revert to within 1% of distance
    epsilon = distance * 0.01
    expected_time = np.log(distance / epsilon) / theta
    
    return expected_time


def calculate_zscore(residuals, window=None):
    """
    Calculate z-score of residuals.
    
    Args:
        residuals: Residual series
        window: Rolling window size (None = use full sample)
        
    Returns:
        Z-score series
    """
    res_series = pd.Series(residuals)
    
    if window is None:
        mu = res_series.mean()
        sigma = res_series.std()
        zscore = (res_series - mu) / sigma
    else:
        rolling_mean = res_series.rolling(window=window).mean()
        rolling_std = res_series.rolling(window=window).std()
        zscore = (res_series - rolling_mean) / rolling_std
    
    return zscore.values


if __name__ == "__main__":
    from data_loader import load_pair_data
    from cointegration import engle_granger_cointegration
    import os
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rb_path = os.path.join(base_dir, 'data', 'rb-2023-2025.csv')
    hc_path = os.path.join(base_dir, 'data', 'hc-2023-2025.csv')
    
    df = load_pair_data(rb_path, hc_path)
    eg_result = engle_granger_cointegration(df['rb_log'], df['hc_log'])
    
    print("=== OU Process Fitting ===")
    ou_result = fit_ou_process(eg_result['residuals'])
    
    print(f"MLE Results:")
    print(f"  Theta (speed of reversion): {ou_result['theta_mle']:.6f}")
    print(f"  Mu (long-term mean): {ou_result['mu_mle']:.6f}")
    print(f"  Sigma (volatility): {ou_result['sigma_mle']:.6f}")
    print(f"  Half-life (days): {ou_result['half_life_mle']:.2f}")
    print(f"  Stationary std: {ou_result['std_stationary']:.6f}")
    print(f"  Log-likelihood: {ou_result['log_likelihood']:.2f}")
    print(f"  Converged: {ou_result['converged']}")
    
    print(f"\nLeast Squares Results:")
    print(f"  Theta: {ou_result['theta_ls']:.6f}")
    print(f"  Mu: {ou_result['mu_ls']:.6f}")
    print(f"  Sigma: {ou_result['sigma_ls']:.6f}")
    print(f"  Half-life (days): {ou_result['half_life_ls']:.2f}")
    
    # Z-score analysis
    zscore = calculate_zscore(eg_result['residuals'])
    print(f"\n=== Z-Score Statistics ===")
    print(f"Z-score min: {np.min(zscore):.4f}")
    print(f"Z-score max: {np.max(zscore):.4f}")
    print(f"Z-score mean: {np.mean(zscore):.4f}")
    print(f"Z-score std: {np.std(zscore):.4f}")
    print(f"Days |z| > 1: {np.sum(np.abs(zscore) > 1)}")
    print(f"Days |z| > 1.5: {np.sum(np.abs(zscore) > 1.5)}")
    print(f"Days |z| > 2: {np.sum(np.abs(zscore) > 2)}")
    print(f"Days |z| > 2.5: {np.sum(np.abs(zscore) > 2.5)}")
