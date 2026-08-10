"""
CQF Final Project - TS: Pairs Trading
Visualization Module
Author: CQF Candidate
Date: 2026
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.gridspec import GridSpec
import os

# Set Chinese font support
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['savefig.bbox'] = 'tight'


def plot_price_series(df, save_path=None):
    """Plot RB and HC price series."""
    fig, ax = plt.subplots(figsize=(12, 5))
    
    ax.plot(df['date'], df['rb_close'], label='RB (螺纹钢)', color='#1f77b4', linewidth=1)
    ax.plot(df['date'], df['hc_close'], label='HC (热轧板)', color='#ff7f0e', linewidth=1)
    
    ax.set_title('RB vs HC Futures Price (2023-2025)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price (RMB/ton)')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()


def plot_log_prices(df, save_path=None):
    """Plot log prices."""
    fig, ax = plt.subplots(figsize=(12, 5))
    
    ax.plot(df['date'], df['rb_log'], label='RB Log Price', color='#1f77b4', linewidth=1)
    ax.plot(df['date'], df['hc_log'], label='HC Log Price', color='#ff7f0e', linewidth=1)
    
    ax.set_title('Log Price Series', fontsize=12, fontweight='bold')
    ax.set_xlabel('Date')
    ax.set_ylabel('Log Price')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()


def plot_spread(df, eg_result, save_path=None):
    """Plot the cointegration spread/residuals."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    
    # Price spread
    ax1.plot(df['date'], df['spread_price'], color='#2ca02c', linewidth=1)
    ax1.axhline(y=np.mean(df['spread_price']), color='red', linestyle='--', alpha=0.7, label='Mean')
    ax1.set_title('Price Spread (RB - HC)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Spread (RMB/ton)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Cointegration residuals
    residuals = eg_result['residuals']
    zscore = (residuals - np.mean(residuals)) / np.std(residuals)
    
    ax2.plot(df['date'], residuals, color='#9467bd', linewidth=1)
    ax2.axhline(y=eg_result['alpha'], color='red', linestyle='--', alpha=0.7, label='Equilibrium')
    ax2.axhline(y=eg_result['alpha'] + eg_result['residual_std'], color='orange', linestyle=':', alpha=0.7, label='+1σ')
    ax2.axhline(y=eg_result['alpha'] - eg_result['residual_std'], color='orange', linestyle=':', alpha=0.7, label='-1σ')
    ax2.axhline(y=eg_result['alpha'] + 2*eg_result['residual_std'], color='red', linestyle=':', alpha=0.5, label='+2σ')
    ax2.axhline(y=eg_result['alpha'] - 2*eg_result['residual_std'], color='red', linestyle=':', alpha=0.5, label='-2σ')
    ax2.set_title('Cointegration Residuals (Engle-Granger)', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Residual')
    ax2.legend(loc='best', fontsize=8)
    ax2.grid(True, alpha=0.3)
    
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()


def plot_zscore(zscore, dates, entry_z=2.0, exit_z=0.0, save_path=None):
    """Plot z-score with entry/exit thresholds."""
    fig, ax = plt.subplots(figsize=(12, 5))
    
    ax.plot(dates, zscore, color='#17becf', linewidth=1, label='Z-score')
    ax.axhline(y=entry_z, color='red', linestyle='--', alpha=0.7, label=f'Entry (+{entry_z}σ)')
    ax.axhline(y=-entry_z, color='red', linestyle='--', alpha=0.7, label=f'Entry (-{entry_z}σ)')
    ax.axhline(y=exit_z, color='green', linestyle='--', alpha=0.7, label=f'Exit ({exit_z}σ)')
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    
    # Shade entry zones
    ax.fill_between(dates, entry_z, max(zscore), where=zscore > entry_z, 
                    color='red', alpha=0.1, label='Short Zone')
    ax.fill_between(dates, min(zscore), -entry_z, where=zscore < -entry_z, 
                    color='green', alpha=0.1, label='Long Zone')
    
    ax.set_title('Z-Score of Cointegration Residuals', fontsize=12, fontweight='bold')
    ax.set_xlabel('Date')
    ax.set_ylabel('Z-Score')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()


def plot_backtest_results(bt_result, dates, save_path=None):
    """Plot backtest results: portfolio value, drawdown, daily P&L."""
    fig = plt.figure(figsize=(14, 10))
    gs = GridSpec(3, 1, height_ratios=[3, 1, 1], hspace=0.3)
    
    # Portfolio value
    ax1 = fig.add_subplot(gs[0])
    portfolio_val = bt_result['portfolio_value']
    ax1.plot(dates, portfolio_val, color='#1f77b4', linewidth=1.2, label='Portfolio Value')
    ax1.axhline(y=bt_result['initial_capital'], color='red', linestyle='--', alpha=0.5, label='Initial Capital')
    ax1.set_title('Portfolio Value', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Value (RMB)')
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    
    # Drawdown
    ax2 = fig.add_subplot(gs[1], sharex=ax1)
    drawdown = bt_result['drawdown'] * 100
    ax2.fill_between(dates, drawdown, 0, color='red', alpha=0.3)
    ax2.plot(dates, drawdown, color='red', linewidth=0.8)
    ax2.set_title('Drawdown', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Drawdown (%)')
    ax2.grid(True, alpha=0.3)
    
    # Daily P&L
    ax3 = fig.add_subplot(gs[2], sharex=ax1)
    daily_pnl = bt_result['daily_pnl']
    colors = ['green' if p >= 0 else 'red' for p in daily_pnl]
    ax3.bar(dates, daily_pnl, color=colors, alpha=0.6, width=1)
    ax3.set_title('Daily P&L', fontsize=12, fontweight='bold')
    ax3.set_xlabel('Date')
    ax3.set_ylabel('P&L (RMB)')
    ax3.grid(True, alpha=0.3)
    
    plt.setp(ax1.get_xticklabels(), rotation=45)
    plt.setp(ax2.get_xticklabels(), rotation=45)
    plt.setp(ax3.get_xticklabels(), rotation=45)
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()


def plot_trade_signals(signals, dates, save_path=None):
    """Plot z-score with entry/exit signals marked."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(dates, signals['zscore'], color='#17becf', linewidth=1, label='Z-score', alpha=0.8)
    ax.axhline(y=2, color='red', linestyle='--', alpha=0.5)
    ax.axhline(y=-2, color='red', linestyle='--', alpha=0.5)
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    
    # Mark entry and exit points
    entry_long = signals[signals['trade_type'] == 'entry_long']
    entry_short = signals[signals['trade_type'] == 'entry_short']
    exit_long = signals[signals['trade_type'].str.startswith('exit') & (signals['position'].shift(1) == 1)]
    exit_short = signals[signals['trade_type'].str.startswith('exit') & (signals['position'].shift(1) == -1)]
    
    if len(entry_long) > 0:
        ax.scatter(dates[entry_long.index], entry_long['zscore'], 
                   color='green', marker='^', s=80, label='Entry Long', zorder=5)
    if len(entry_short) > 0:
        ax.scatter(dates[entry_short.index], entry_short['zscore'], 
                   color='red', marker='v', s=80, label='Entry Short', zorder=5)
    
    # Shade position periods
    position = signals['position'].values
    ax.fill_between(dates, ax.get_ylim()[0], ax.get_ylim()[1], 
                    where=position != 0, color='yellow', alpha=0.1, label='In Position')
    
    ax.set_title('Trading Signals on Z-Score', fontsize=12, fontweight='bold')
    ax.set_xlabel('Date')
    ax.set_ylabel('Z-Score')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()


def plot_rolling_beta(rolling_result, dates, save_path=None):
    """Plot rolling beta over time."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    
    valid_idx = ~np.isnan(rolling_result['rolling_beta'])
    valid_dates = dates[valid_idx]
    valid_beta = rolling_result['rolling_beta'][valid_idx]
    
    ax1.plot(valid_dates, valid_beta, color='#9467bd', linewidth=1.2)
    ax1.axhline(y=np.mean(valid_beta), color='red', linestyle='--', alpha=0.7, label=f'Mean = {np.mean(valid_beta):.4f}')
    ax1.set_title('Rolling Cointegration Beta (8-month window)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Beta (Hedge Ratio)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Cointegration stability
    valid_pvalue = rolling_result['rolling_adf_pvalue'][valid_idx]
    ax2.plot(valid_dates, valid_pvalue, color='#d62728', linewidth=1)
    ax2.axhline(y=0.05, color='green', linestyle='--', alpha=0.7, label='5% Significance')
    ax2.fill_between(valid_dates, 0, 0.05, where=valid_pvalue < 0.05, 
                     color='green', alpha=0.1, label='Cointegrated')
    ax2.fill_between(valid_dates, 0.05, 1, where=valid_pvalue >= 0.05, 
                     color='red', alpha=0.1, label='Not Cointegrated')
    ax2.set_title('Rolling ADF Test P-Value', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('P-Value')
    ax2.set_ylim(0, 0.5)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()


def plot_threshold_heatmap(opt_result, save_path=None):
    """Plot threshold optimization heatmap."""
    results_df = opt_result['all_results']
    
    # Pivot data for heatmap
    pivot_sharpe = results_df.pivot(index='entry_z', columns='exit_z', values='sharpe_ratio')
    pivot_return = results_df.pivot(index='entry_z', columns='exit_z', values='total_return')
    pivot_trades = results_df.pivot(index='entry_z', columns='exit_z', values='num_trades')
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    # Sharpe ratio heatmap
    im1 = axes[0].imshow(pivot_sharpe.values, cmap='RdYlGn', aspect='auto')
    axes[0].set_title('Sharpe Ratio', fontsize=11, fontweight='bold')
    axes[0].set_xlabel('Exit Z-Score')
    axes[0].set_ylabel('Entry Z-Score')
    axes[0].set_xticks(range(len(pivot_sharpe.columns)))
    axes[0].set_xticklabels([f'{x:.1f}' for x in pivot_sharpe.columns])
    axes[0].set_yticks(range(len(pivot_sharpe.index)))
    axes[0].set_yticklabels([f'{x:.1f}' for x in pivot_sharpe.index])
    plt.colorbar(im1, ax=axes[0])
    
    # Mark best
    best_entry = opt_result['best_entry_z']
    best_exit = opt_result['best_exit_z']
    entry_idx = list(pivot_sharpe.index).index(best_entry)
    exit_idx = list(pivot_sharpe.columns).index(best_exit)
    axes[0].plot(exit_idx, entry_idx, 'k*', markersize=15, label='Best')
    
    # Total return heatmap
    im2 = axes[1].imshow(pivot_return.values * 100, cmap='RdYlGn', aspect='auto')
    axes[1].set_title('Total Return (%)', fontsize=11, fontweight='bold')
    axes[1].set_xlabel('Exit Z-Score')
    axes[1].set_ylabel('Entry Z-Score')
    axes[1].set_xticks(range(len(pivot_return.columns)))
    axes[1].set_xticklabels([f'{x:.1f}' for x in pivot_return.columns])
    axes[1].set_yticks(range(len(pivot_return.index)))
    axes[1].set_yticklabels([f'{x:.1f}' for x in pivot_return.index])
    plt.colorbar(im2, ax=axes[1])
    
    # Number of trades heatmap
    im3 = axes[2].imshow(pivot_trades.values, cmap='YlOrRd', aspect='auto')
    axes[2].set_title('Number of Trades', fontsize=11, fontweight='bold')
    axes[2].set_xlabel('Exit Z-Score')
    axes[2].set_ylabel('Entry Z-Score')
    axes[2].set_xticks(range(len(pivot_trades.columns)))
    axes[2].set_xticklabels([f'{x:.1f}' for x in pivot_trades.columns])
    axes[2].set_yticks(range(len(pivot_trades.index)))
    axes[2].set_yticklabels([f'{x:.1f}' for x in pivot_trades.index])
    plt.colorbar(im3, ax=axes[2])
    
    plt.suptitle('Threshold Optimization Grid Search', fontsize=13, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()


def plot_ou_fit(residuals, ou_params, save_path=None):
    """Plot OU process fit diagnostics."""
    from ou_process import ou_simulate
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Residuals vs OU simulation
    ax1 = axes[0, 0]
    ax1.plot(residuals, color='#1f77b4', linewidth=0.8, alpha=0.7, label='Actual Residuals')
    
    # Simulate OU with fitted parameters
    n_sim = len(residuals)
    sim = ou_simulate(ou_params['theta_mle'], ou_params['mu_mle'], ou_params['sigma_mle'],
                      residuals[0], n_sim, seed=42)
    ax1.plot(sim, color='red', linewidth=0.8, alpha=0.7, label='OU Simulation')
    ax1.set_title('Actual vs OU Simulated Residuals', fontsize=11, fontweight='bold')
    ax1.set_xlabel('Time (days)')
    ax1.set_ylabel('Residual')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Distribution of residuals
    ax2 = axes[0, 1]
    ax2.hist(residuals, bins=50, density=True, alpha=0.6, color='#2ca02c', label='Empirical')
    
    # Theoretical stationary distribution
    from scipy.stats import norm
    x_range = np.linspace(min(residuals), max(residuals), 200)
    pdf = norm.pdf(x_range, loc=ou_params['mu_mle'], scale=ou_params['std_stationary'])
    ax2.plot(x_range, pdf, 'r-', linewidth=2, label='OU Stationary Dist.')
    ax2.set_title('Residual Distribution', fontsize=11, fontweight='bold')
    ax2.set_xlabel('Residual')
    ax2.set_ylabel('Density')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Autocorrelation
    ax3 = axes[1, 0]
    from statsmodels.graphics.tsaplots import plot_acf
    plot_acf(residuals, lags=50, ax=ax3, alpha=0.05)
    ax3.set_title('Autocorrelation Function', fontsize=11, fontweight='bold')
    ax3.set_xlabel('Lag (days)')
    ax3.grid(True, alpha=0.3)
    
    # Mean reversion speed visualization
    ax4 = axes[1, 1]
    half_life = ou_params['half_life_mle']
    distances = np.linspace(0.1, 3, 100)
    times = np.log(distances / 0.01) / ou_params['theta_mle']
    
    ax4.plot(distances, times, color='#9467bd', linewidth=2)
    ax4.axhline(y=half_life, color='red', linestyle='--', alpha=0.7, 
                label=f'Half-life = {half_life:.1f} days')
    ax4.set_title('Expected Mean Reversion Time', fontsize=11, fontweight='bold')
    ax4.set_xlabel('Distance from Mean (σ)')
    ax4.set_ylabel('Expected Time (days)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()


def plot_comparison_static_vs_dynamic(static_bt, dynamic_bt, dates, save_path=None):
    """Compare static vs dynamic cointegration strategies."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    
    # Portfolio value comparison
    ax1.plot(dates, static_bt['portfolio_value'], label='Static Beta', color='#1f77b4', linewidth=1.2)
    ax1.plot(dates, dynamic_bt['portfolio_value'], label='Dynamic Rolling Beta', color='#ff7f0e', linewidth=1.2)
    ax1.axhline(y=static_bt['initial_capital'], color='red', linestyle='--', alpha=0.5, label='Initial Capital')
    ax1.set_title('Static vs Dynamic Cointegration: Portfolio Value', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Value (RMB)')
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)
    
    # Drawdown comparison
    ax2.plot(dates, static_bt['drawdown'] * 100, label='Static Beta', color='#1f77b4', linewidth=1)
    ax2.plot(dates, dynamic_bt['drawdown'] * 100, label='Dynamic Rolling Beta', color='#ff7f0e', linewidth=1)
    ax2.set_title('Static vs Dynamic Cointegration: Drawdown', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Drawdown (%)')
    ax2.legend(loc='best')
    ax2.grid(True, alpha=0.3)
    
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()


def generate_all_figures(df, eg_result, ou_result, zscore, signals, bt_result,
                         opt_result, rolling_result, dyn_bt_result, output_dir):
    """Generate all figures for the report."""
    os.makedirs(output_dir, exist_ok=True)
    dates = df['date']
    
    figures = {}
    
    # 1. Price series
    path = os.path.join(output_dir, 'fig1_price_series.png')
    plot_price_series(df, save_path=path)
    figures['price_series'] = path
    
    # 2. Log prices
    path = os.path.join(output_dir, 'fig2_log_prices.png')
    plot_log_prices(df, save_path=path)
    figures['log_prices'] = path
    
    # 3. Spread and residuals
    path = os.path.join(output_dir, 'fig3_spread_residuals.png')
    plot_spread(df, eg_result, save_path=path)
    figures['spread_residuals'] = path
    
    # 4. Z-score
    path = os.path.join(output_dir, 'fig4_zscore.png')
    plot_zscore(zscore, dates, entry_z=2.0, exit_z=0.0, save_path=path)
    figures['zscore'] = path
    
    # 5. OU fit
    path = os.path.join(output_dir, 'fig5_ou_fit.png')
    plot_ou_fit(eg_result['residuals'], ou_result, save_path=path)
    figures['ou_fit'] = path
    
    # 6. Trading signals
    path = os.path.join(output_dir, 'fig6_trade_signals.png')
    plot_trade_signals(signals, dates, save_path=path)
    figures['trade_signals'] = path
    
    # 7. Backtest results
    path = os.path.join(output_dir, 'fig7_backtest_results.png')
    plot_backtest_results(bt_result, dates, save_path=path)
    figures['backtest_results'] = path
    
    # 8. Threshold optimization
    path = os.path.join(output_dir, 'fig8_threshold_optimization.png')
    plot_threshold_heatmap(opt_result, save_path=path)
    figures['threshold_optimization'] = path
    
    # 9. Rolling beta
    path = os.path.join(output_dir, 'fig9_rolling_beta.png')
    plot_rolling_beta(rolling_result, dates, save_path=path)
    figures['rolling_beta'] = path
    
    # 10. Static vs dynamic comparison
    path = os.path.join(output_dir, 'fig10_static_vs_dynamic.png')
    plot_comparison_static_vs_dynamic(bt_result, dyn_bt_result, dates, save_path=path)
    figures['static_vs_dynamic'] = path
    
    return figures


if __name__ == "__main__":
    print("Visualization module loaded successfully.")
