"""
CQF Final Project - TS: Pairs Trading
Main Execution Script
Author: CQF Candidate
Date: 2026

This script runs the complete pairs trading analysis:
1. Data loading and preprocessing
2. Cointegration analysis (Engle-Granger two-step method)
3. OU process fitting
4. Trading strategy and threshold optimization
5. Backtesting
6. Rolling window dynamic cointegration
7. Visualization and report generation
"""

import os
import sys
import json
import numpy as np
import pandas as pd

# Add code directory to path
code_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, code_dir)

from data_loader import load_pair_data, verify_data_quality
from cointegration import (engle_granger_cointegration, adf_test, 
                           half_life, hurst_exponent, variance_ratio_test)
from ou_process import fit_ou_process, calculate_zscore
from strategy import PairsTradingStrategy, optimize_threshold
from backtest import BacktestEngine, calculate_trade_analytics
from rolling import RollingCointegration, structural_break_analysis
from visualization import generate_all_figures


def main():
    """Main execution function."""
    print("=" * 70)
    print("CQF Final Project - TS: Pairs Trading")
    print("RB (螺纹钢) & HC (热轧板) Futures Pairs Trading Strategy")
    print("=" * 70)
    
    # Setup paths
    base_dir = os.path.dirname(code_dir)
    data_dir = os.path.join(base_dir, 'data')
    fig_dir = os.path.join(base_dir, 'figures')
    output_dir = os.path.join(base_dir, 'output')
    
    os.makedirs(fig_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    rb_path = os.path.join(data_dir, 'rb-2023-2025.csv')
    hc_path = os.path.join(data_dir, 'hc-2023-2025.csv')
    
    # ============================================================
    # Step 1: Data Loading and Quality Check
    # ============================================================
    print("\n[Step 1] Data Loading and Quality Check")
    print("-" * 50)
    
    df = load_pair_data(rb_path, hc_path)
    metrics = verify_data_quality(df)
    
    print(f"Date range: {metrics['date_range'][0].date()} to {metrics['date_range'][1].date()}")
    print(f"Total trading days: {metrics['total_days']}")
    print(f"RB missing values: {metrics['rb_missing']}")
    print(f"HC missing values: {metrics['hc_missing']}")
    print(f"Price correlation: {metrics['correlation']:.4f}")
    print(f"Log price correlation: {metrics['log_correlation']:.4f}")
    
    # ============================================================
    # Step 2: Stationarity Tests (ADF)
    # ============================================================
    print("\n[Step 2] Stationarity Tests (ADF)")
    print("-" * 50)
    
    rb_adf_level = adf_test(df['rb_log'], 'RB Log Price (Level)')
    hc_adf_level = adf_test(df['hc_log'], 'HC Log Price (Level)')
    rb_adf_diff = adf_test(df['rb_log'].diff().dropna(), 'RB Log Return (Diff)')
    hc_adf_diff = adf_test(df['hc_log'].diff().dropna(), 'HC Log Return (Diff)')
    
    print("Level series (log prices):")
    print(f"  RB: ADF={rb_adf_level['adf_statistic']:.4f}, p={rb_adf_level['p_value']:.4f}, "
          f"stationary@5%: {rb_adf_level['is_stationary_5pct']}")
    print(f"  HC: ADF={hc_adf_level['adf_statistic']:.4f}, p={hc_adf_level['p_value']:.4f}, "
          f"stationary@5%: {hc_adf_level['is_stationary_5pct']}")
    
    print("\nFirst-differenced series (log returns):")
    print(f"  RB: ADF={rb_adf_diff['adf_statistic']:.4f}, p={rb_adf_diff['p_value']:.4f}, "
          f"stationary@5%: {rb_adf_diff['is_stationary_5pct']}")
    print(f"  HC: ADF={hc_adf_diff['adf_statistic']:.4f}, p={hc_adf_diff['p_value']:.4f}, "
          f"stationary@5%: {hc_adf_diff['is_stationary_5pct']}")
    
    # ============================================================
    # Step 3: Engle-Granger Cointegration Test
    # ============================================================
    print("\n[Step 3] Engle-Granger Cointegration Test")
    print("-" * 50)
    
    eg_result = engle_granger_cointegration(df['rb_log'], df['hc_log'])
    
    print(f"Long-run equilibrium: ln(RB) = {eg_result['alpha']:.6f} + {eg_result['beta']:.6f} * ln(HC)")
    print(f"ADF statistic: {eg_result['adf_statistic']:.4f}")
    print(f"ADF p-value: {eg_result['adf_pvalue']:.6f}")
    print(f"Critical values: 1%={eg_result['adf_critical_values']['1%']:.4f}, "
          f"5%={eg_result['adf_critical_values']['5%']:.4f}, "
          f"10%={eg_result['adf_critical_values']['10%']:.4f}")
    print(f"Cointegrated at 1%: {eg_result['is_cointegrated_1pct']}")
    print(f"Cointegrated at 5%: {eg_result['is_cointegrated_5pct']}")
    print(f"R-squared: {eg_result['r_squared']:.4f}")
    print(f"Residual std: {eg_result['residual_std']:.6f}")
    
    # ============================================================
    # Step 4: Mean Reversion Analysis
    # ============================================================
    print("\n[Step 4] Mean Reversion Analysis")
    print("-" * 50)
    
    # Half-life
    hl_result = half_life(eg_result['residuals'])
    print(f"Half-life of mean reversion: {hl_result['half_life']:.2f} days")
    print(f"AR(1) coefficient: {hl_result['ar_coeff']:.6f}")
    print(f"Theta (speed): {hl_result['theta']:.6f}")
    
    # Hurst exponent
    hurst = hurst_exponent(eg_result['residuals'], max_lag=50)
    print(f"Hurst exponent: {hurst:.4f}")
    if hurst < 0.5:
        print("  -> Mean-reverting (H < 0.5)")
    elif hurst > 0.5:
        print("  -> Trending/persistent (H > 0.5)")
    else:
        print("  -> Random walk (H ≈ 0.5)")
    
    # Variance ratio test
    vr_result = variance_ratio_test(df['rb_log'].values, k=5)
    print(f"Variance ratio (k=5): {vr_result['variance_ratio']:.4f}")
    print(f"  VR < 1: Mean-reverting = {vr_result['is_mean_reverting']}")
    
    # OU process fitting
    print("\nOU Process Fitting (MLE):")
    ou_result = fit_ou_process(eg_result['residuals'])
    print(f"  Theta (speed): {ou_result['theta_mle']:.6f}")
    print(f"  Mu (long-term mean): {ou_result['mu_mle']:.6f}")
    print(f"  Sigma (volatility): {ou_result['sigma_mle']:.6f}")
    print(f"  Half-life: {ou_result['half_life_mle']:.2f} days")
    print(f"  Stationary std: {ou_result['std_stationary']:.6f}")
    
    # ============================================================
    # Step 5: Trading Strategy - Threshold Optimization
    # ============================================================
    print("\n[Step 5] Trading Strategy - Threshold Optimization")
    print("-" * 50)
    
    zscore = calculate_zscore(eg_result['residuals'])
    
    print("Running grid search for optimal entry/exit thresholds...")
    opt_result = optimize_threshold(
        zscore, df['rb_close'], df['hc_close'], eg_result['beta'],
        entry_range=(1.0, 2.5), exit_range=(0.0, 0.8), step=0.2,
        metric='sharpe'
    )
    
    print(f"\nOptimal parameters (max Sharpe):")
    print(f"  Entry z-score: {opt_result['best_entry_z']:.1f}")
    print(f"  Exit z-score: {opt_result['best_exit_z']:.1f}")
    print(f"  Sharpe ratio: {opt_result['best_params']['sharpe_ratio']:.4f}")
    print(f"  Total return: {opt_result['best_params']['total_return']:.2%}")
    print(f"  Max drawdown: {opt_result['best_params']['max_drawdown']:.2%}")
    print(f"  Number of trades: {opt_result['best_params']['num_trades']}")
    print(f"  Win rate: {opt_result['best_params']['win_rate']:.2%}")
    
    # Use optimal parameters for final strategy
    best_entry = opt_result['best_entry_z']
    best_exit = opt_result['best_exit_z']
    
    # ============================================================
    # Step 6: Backtesting with Optimal Parameters
    # ============================================================
    print("\n[Step 6] Backtesting with Optimal Parameters")
    print("-" * 50)
    
    strategy = PairsTradingStrategy(
        entry_z=best_entry, 
        exit_z=best_exit,
        stop_loss_z=best_entry + 1.0,
        max_holding_days=60,
        transaction_cost=0.0005
    )
    
    signals = strategy.generate_signals(zscore, df['rb_close'], df['hc_close'], eg_result['beta'])
    
    engine = BacktestEngine(initial_capital=1000000, transaction_cost=0.0005)
    bt_result = engine.run_backtest(signals, eg_result['beta'])
    
    print(f"Initial capital: ¥{bt_result['initial_capital']:,.0f}")
    print(f"Final capital: ¥{bt_result['final_capital']:,.0f}")
    print(f"Total return: {bt_result['total_return']:.2%}")
    print(f"Annualized return: {bt_result['annualized_return']:.2%}")
    print(f"Annualized volatility: {bt_result['annualized_volatility']:.2%}")
    print(f"Sharpe ratio: {bt_result['sharpe_ratio']:.4f}")
    print(f"Sortino ratio: {bt_result['sortino_ratio']:.4f}")
    print(f"Calmar ratio: {bt_result['calmar_ratio']:.4f}")
    print(f"Max drawdown: {bt_result['max_drawdown']:.2%}")
    print(f"Number of trades: {bt_result['num_trades']}")
    print(f"Win rate: {bt_result['win_rate']:.2%}")
    print(f"Profit factor: {bt_result['profit_factor']:.4f}")
    
    # Trade analytics
    trades_df = calculate_trade_analytics(signals, eg_result['beta'])
    if len(trades_df) > 0:
        print(f"\nTrade statistics:")
        print(f"  Avg holding days: {trades_df['holding_days'].mean():.1f}")
        print(f"  Avg P&L per trade: ¥{trades_df['total_pnl'].mean():,.0f}")
        print(f"  Best trade: ¥{trades_df['total_pnl'].max():,.0f}")
        print(f"  Worst trade: ¥{trades_df['total_pnl'].min():,.0f}")
        print(f"  Exit reasons:")
        for reason, count in trades_df['exit_reason'].value_counts().items():
            print(f"    {reason}: {count}")
    
    # ============================================================
    # Step 7: Rolling Window Dynamic Cointegration
    # ============================================================
    print("\n[Step 7] Rolling Window Dynamic Cointegration")
    print("-" * 50)
    
    print("Window size: 168 trading days (≈8 months)")
    
    rolling = RollingCointegration(window_size=168, step=1)
    
    dyn_result = rolling.generate_dynamic_signals(
        df['rb_log'], df['hc_log'],
        df['rb_close'], df['hc_close'],
        entry_z=best_entry, exit_z=best_exit,
        stop_loss_z=best_entry + 1.0,
        max_holding_days=60
    )
    
    dyn_signals = dyn_result['signals']
    valid_beta = dyn_result['rolling_beta'][~np.isnan(dyn_result['rolling_beta'])]
    
    print(f"\nRolling beta statistics:")
    if len(valid_beta) > 0:
        print(f"  Valid windows: {len(valid_beta)}")
        print(f"  Mean: {np.mean(valid_beta):.4f}")
        print(f"  Std: {np.std(valid_beta):.4f}")
        print(f"  Min: {np.min(valid_beta):.4f}")
        print(f"  Max: {np.max(valid_beta):.4f}")
    else:
        print("  No valid rolling beta values")
    
    valid_coint = dyn_result['is_cointegrated'][~np.isnan(dyn_result['rolling_beta'])]
    print(f"\nCointegration stability:")
    if len(valid_coint) > 0:
        print(f"  Days cointegrated @5%: {np.sum(valid_coint)} / {len(valid_coint)}")
        print(f"  Cointegration ratio: {np.sum(valid_coint)/len(valid_coint):.2%}")
    else:
        print("  No valid cointegration test results")
    
    # Dynamic strategy backtest
    avg_beta = np.nanmean(dyn_result['rolling_beta']) if len(valid_beta) > 0 else eg_result['beta']
    dyn_engine = BacktestEngine(initial_capital=1000000, transaction_cost=0.0005)
    dyn_bt_result = dyn_engine.run_backtest(dyn_signals, avg_beta)
    
    print(f"\nDynamic strategy backtest:")
    print(f"  Total return: {dyn_bt_result['total_return']:.2%}")
    print(f"  Sharpe ratio: {dyn_bt_result['sharpe_ratio']:.4f}")
    print(f"  Max drawdown: {dyn_bt_result['max_drawdown']:.2%}")
    print(f"  Number of trades: {dyn_bt_result['num_trades']}")
    print(f"  Win rate: {dyn_bt_result['win_rate']:.2%}")
    
    # Structural break analysis
    print("\nStructural break analysis:")
    break_analysis = structural_break_analysis(eg_result['residuals'], window_size=60)
    print(f"  Break days (p>0.05): {break_analysis['num_break_days']}")
    print(f"  Break ratio: {break_analysis['break_ratio']:.2%}")
    
    # ============================================================
    # Step 8: Generate All Figures
    # ============================================================
    print("\n[Step 8] Generating All Figures")
    print("-" * 50)
    
    figures = generate_all_figures(
        df, eg_result, ou_result, zscore, signals, bt_result,
        opt_result, dyn_result, dyn_bt_result, fig_dir
    )
    
    for name, path in figures.items():
        print(f"  {name}: {os.path.basename(path)}")
    
    # ============================================================
    # Step 9: Save Results
    # ============================================================
    print("\n[Step 9] Saving Results")
    print("-" * 50)
    
    # Save summary results
    summary = {
        'data': {
            'date_range': [str(metrics['date_range'][0].date()), str(metrics['date_range'][1].date())],
            'total_days': metrics['total_days'],
            'correlation': metrics['correlation'],
        },
        'cointegration': {
            'alpha': eg_result['alpha'],
            'beta': eg_result['beta'],
            'adf_statistic': eg_result['adf_statistic'],
            'adf_pvalue': eg_result['adf_pvalue'],
            'is_cointegrated_5pct': eg_result['is_cointegrated_5pct'],
            'r_squared': eg_result['r_squared'],
            'residual_std': eg_result['residual_std'],
        },
        'mean_reversion': {
            'half_life_days': hl_result['half_life'],
            'hurst_exponent': hurst,
            'ou_theta': ou_result['theta_mle'],
            'ou_mu': ou_result['mu_mle'],
            'ou_sigma': ou_result['sigma_mle'],
            'ou_half_life': ou_result['half_life_mle'],
        },
        'strategy': {
            'optimal_entry_z': best_entry,
            'optimal_exit_z': best_exit,
            'total_return': bt_result['total_return'],
            'annualized_return': bt_result['annualized_return'],
            'annualized_volatility': bt_result['annualized_volatility'],
            'sharpe_ratio': bt_result['sharpe_ratio'],
            'sortino_ratio': bt_result['sortino_ratio'],
            'calmar_ratio': bt_result['calmar_ratio'],
            'max_drawdown': bt_result['max_drawdown'],
            'num_trades': bt_result['num_trades'],
            'win_rate': bt_result['win_rate'],
            'profit_factor': bt_result['profit_factor'],
        },
        'rolling': {
            'window_size': 168,
            'beta_mean': float(np.mean(valid_beta)) if len(valid_beta) > 0 else eg_result['beta'],
            'beta_std': float(np.std(valid_beta)) if len(valid_beta) > 0 else 0,
            'cointegration_ratio': float(np.sum(valid_coint)/len(valid_coint)) if len(valid_coint) > 0 else 0,
            'dynamic_total_return': dyn_bt_result['total_return'],
            'dynamic_sharpe': dyn_bt_result['sharpe_ratio'],
            'dynamic_max_drawdown': dyn_bt_result['max_drawdown'],
        }
    }
    
    # Convert numpy types to Python native types for JSON serialization
    def convert_numpy_types(obj):
        if isinstance(obj, dict):
            return {k: convert_numpy_types(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [convert_numpy_types(item) for item in obj]
        elif isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj
    
    summary = convert_numpy_types(summary)
    
    summary_path = os.path.join(output_dir, 'results_summary.json')
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"  Summary saved: {summary_path}")
    
    # Save signals
    signals_path = os.path.join(output_dir, 'trading_signals.csv')
    signals.to_csv(signals_path, index=False)
    print(f"  Signals saved: {signals_path}")
    
    # Save trades
    if len(trades_df) > 0:
        trades_path = os.path.join(output_dir, 'trade_analytics.csv')
        trades_df.to_csv(trades_path, index=False)
        print(f"  Trade analytics saved: {trades_path}")
    
    # Save backtest results
    bt_df = pd.DataFrame({
        'date': df['date'],
        'portfolio_value': bt_result['portfolio_value'],
        'daily_pnl': bt_result['daily_pnl'],
        'drawdown': bt_result['drawdown'],
        'rb_position': bt_result['rb_position'],
        'hc_position': bt_result['hc_position'],
    })
    bt_path = os.path.join(output_dir, 'backtest_results.csv')
    bt_df.to_csv(bt_path, index=False)
    print(f"  Backtest results saved: {bt_path}")
    
    print("\n" + "=" * 70)
    print("Analysis Complete!")
    print("=" * 70)
    
    return {
        'df': df,
        'eg_result': eg_result,
        'ou_result': ou_result,
        'zscore': zscore,
        'signals': signals,
        'bt_result': bt_result,
        'opt_result': opt_result,
        'rolling_result': dyn_result,
        'dyn_bt_result': dyn_bt_result,
        'trades_df': trades_df,
        'figures': figures,
        'summary': summary,
    }


if __name__ == "__main__":
    results = main()
