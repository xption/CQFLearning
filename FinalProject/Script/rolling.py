"""
CQF Final Project - TS: Pairs Trading
Rolling Window Dynamic Cointegration Module
Author: CQF Candidate
Date: 2026
"""

import numpy as np
import pandas as pd
from cointegration import engle_granger_cointegration, adf_test
from ou_process import calculate_zscore


class RollingCointegration:
    """
    Rolling window cointegration analysis for dynamic pairs trading.
    
    Features:
    - Rolling estimation of cointegration beta
    - Rolling ADF test for cointegration stability
    - Dynamic z-score calculation
    - Cointegration break detection
    """
    
    def __init__(self, window_size=168, step=1):
        """
        Initialize rolling cointegration analyzer.
        
        Args:
            window_size: Rolling window size in days (default 168 ≈ 8 months)
            step: Step size for rolling window (default 1 day)
        """
        self.window_size = window_size
        self.step = step
        
    def fit(self, rb_log, hc_log, dates=None):
        """
        Run rolling cointegration analysis.
        
        Args:
            rb_log: RB log price series (array or Series)
            hc_log: HC log price series (array or Series)
            dates: Date index (optional)
            
        Returns:
            DataFrame with rolling cointegration results
        """
        n = len(rb_log)
        rb_arr = np.asarray(rb_log, dtype=float)
        hc_arr = np.asarray(hc_log, dtype=float)
        
        results = []
        
        for i in range(self.window_size, n, self.step):
            start_idx = i - self.window_size
            end_idx = i
            
            window_rb = rb_arr[start_idx:end_idx]
            window_hc = hc_arr[start_idx:end_idx]
            
            try:
                eg_result = engle_granger_cointegration(window_rb, window_hc)
                
                result = {
                    'end_idx': end_idx,
                    'end_date': dates.iloc[end_idx] if dates is not None else end_idx,
                    'alpha': eg_result['alpha'],
                    'beta': eg_result['beta'],
                    'residual_std': eg_result['residual_std'],
                    'adf_statistic': eg_result['adf_statistic'],
                    'adf_pvalue': eg_result['adf_pvalue'],
                    'is_cointegrated_5pct': eg_result['is_cointegrated_5pct'],
                    'r_squared': eg_result['r_squared'],
                }
                results.append(result)
            except Exception as e:
                print(f"Warning: Rolling window at index {i} failed: {e}")
                continue
        
        results_df = pd.DataFrame(results)
        
        return results_df
    
    def generate_dynamic_signals(self, rb_log, hc_log, rb_price, hc_price,
                                  entry_z=2.0, exit_z=0.0, stop_loss_z=3.0,
                                  max_holding_days=30, transaction_cost=0.0005):
        """
        Generate trading signals using dynamically estimated beta and z-score.
        
        Args:
            rb_log: RB log price series
            hc_log: HC log price series
            rb_price: RB price series
            hc_price: HC price series
            entry_z: Entry z-score threshold
            exit_z: Exit z-score threshold
            stop_loss_z: Stop loss z-score threshold
            max_holding_days: Maximum holding days
            transaction_cost: Transaction cost
            
        Returns:
            Dictionary with signals and rolling results
        """
        n = len(rb_log)
        rb_arr = np.asarray(rb_log, dtype=float)
        hc_arr = np.asarray(hc_log, dtype=float)
        rb_price_arr = np.asarray(rb_price, dtype=float)
        hc_price_arr = np.asarray(hc_price, dtype=float)
        
        # Initialize arrays
        rolling_beta = np.full(n, np.nan)
        rolling_alpha = np.full(n, np.nan)
        rolling_residual_std = np.full(n, np.nan)
        rolling_zscore = np.full(n, np.nan)
        rolling_adf_pvalue = np.full(n, np.nan)
        is_cointegrated = np.full(n, False)
        
        position = 0
        positions = np.zeros(n)
        holding_days_arr = np.zeros(n)
        trade_types = [''] * n
        current_hold = 0
        
        for i in range(self.window_size, n):
            start_idx = i - self.window_size
            window_rb = rb_arr[start_idx:i]
            window_hc = hc_arr[start_idx:i]
            
            try:
                eg_result = engle_granger_cointegration(window_rb, window_hc)
                
                rolling_beta[i] = eg_result['beta']
                rolling_alpha[i] = eg_result['alpha']
                rolling_residual_std[i] = eg_result['residual_std']
                rolling_adf_pvalue[i] = eg_result['adf_pvalue']
                is_cointegrated[i] = eg_result['is_cointegrated_5pct']
                
                # Calculate current z-score using rolling parameters
                current_residual = rb_arr[i] - eg_result['alpha'] - eg_result['beta'] * hc_arr[i]
                rolling_zscore[i] = current_residual / eg_result['residual_std']
                
            except Exception as e:
                rolling_zscore[i] = np.nan
                continue
            
            z = rolling_zscore[i]
            if np.isnan(z):
                positions[i] = position
                if position != 0:
                    current_hold += 1
                    holding_days_arr[i] = current_hold
                continue
            
            if position == 0:
                # Only enter if cointegrated
                if is_cointegrated[i]:
                    if z > entry_z:
                        position = -1
                        current_hold = 0
                        trade_types[i] = 'entry_short'
                    elif z < -entry_z:
                        position = 1
                        current_hold = 0
                        trade_types[i] = 'entry_long'
            else:
                current_hold += 1
                holding_days_arr[i] = current_hold
                
                should_exit = False
                exit_reason = ''
                
                # Mean reversion exit
                if position == -1 and z < exit_z:
                    should_exit = True
                    exit_reason = 'mean_reversion'
                elif position == 1 and z > -exit_z:
                    should_exit = True
                    exit_reason = 'mean_reversion'
                
                # Stop loss
                if position == -1 and z > stop_loss_z:
                    should_exit = True
                    exit_reason = 'stop_loss'
                elif position == 1 and z < -stop_loss_z:
                    should_exit = True
                    exit_reason = 'stop_loss'
                
                # Max holding period
                if current_hold >= max_holding_days:
                    should_exit = True
                    exit_reason = 'max_holding'
                
                # If cointegration breaks, exit
                if not is_cointegrated[i]:
                    should_exit = True
                    exit_reason = 'cointegration_break'
                
                if should_exit:
                    trade_types[i] = f'exit_{exit_reason}'
                    position = 0
                    current_hold = 0
            
            positions[i] = position
        
        signals = pd.DataFrame({
            'zscore': rolling_zscore,
            'rb_price': rb_price_arr,
            'hc_price': hc_price_arr,
            'position': positions,
            'holding_days': holding_days_arr,
            'trade_type': trade_types,
            'rolling_beta': rolling_beta,
            'rolling_alpha': rolling_alpha,
            'rolling_residual_std': rolling_residual_std,
            'rolling_adf_pvalue': rolling_adf_pvalue,
            'is_cointegrated': is_cointegrated,
        })
        
        return {
            'signals': signals,
            'rolling_beta': rolling_beta,
            'rolling_alpha': rolling_alpha,
            'rolling_residual_std': rolling_residual_std,
            'rolling_adf_pvalue': rolling_adf_pvalue,
            'rolling_zscore': rolling_zscore,
            'is_cointegrated': is_cointegrated,
        }


def structural_break_analysis(residuals, dates=None, window_size=60):
    """
    Analyze structural breaks in the cointegration relationship.
    
    Args:
        residuals: Full sample residuals
        dates: Date index
        window_size: Rolling window for break detection
        
    Returns:
        Dictionary with structural break analysis results
    """
    res_series = pd.Series(residuals)
    n = len(res_series)
    
    # Rolling ADF test
    rolling_adf = []
    rolling_pvalues = []
    
    for i in range(window_size, n):
        window = res_series.iloc[i-window_size:i]
        try:
            adf_result = adf_test(window)
            rolling_adf.append(adf_result['adf_statistic'])
            rolling_pvalues.append(adf_result['p_value'])
        except:
            rolling_adf.append(np.nan)
            rolling_pvalues.append(np.nan)
    
    # Rolling mean and std
    rolling_mean = res_series.rolling(window=window_size).mean()
    rolling_std = res_series.rolling(window=window_size).std()
    
    # Detect breaks: periods where cointegration fails (p > 0.05)
    pvalue_series = pd.Series(rolling_pvalues, index=res_series.index[window_size:])
    break_periods = pvalue_series[pvalue_series > 0.05]
    
    results = {
        'rolling_adf': rolling_adf,
        'rolling_pvalues': rolling_pvalues,
        'rolling_mean': rolling_mean.values,
        'rolling_std': rolling_std.values,
        'break_periods': break_periods,
        'num_break_days': len(break_periods),
        'break_ratio': len(break_periods) / (n - window_size) if n > window_size else 0,
    }
    
    return results


if __name__ == "__main__":
    from data_loader import load_pair_data
    from backtest import BacktestEngine
    import os
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rb_path = os.path.join(base_dir, 'data', 'rb-2023-2025.csv')
    hc_path = os.path.join(base_dir, 'data', 'hc-2023-2025.csv')
    
    df = load_pair_data(rb_path, hc_path)
    
    print("=== Rolling Window Cointegration Analysis ===")
    print(f"Window size: 168 days (≈8 months)")
    
    rolling = RollingCointegration(window_size=168, step=1)
    
    # First test with fit() method
    print("\nTesting fit() method...")
    roll_df = rolling.fit(df['rb_log'], df['hc_log'], dates=df['date'])
    print(f"Got {len(roll_df)} rolling windows")
    if len(roll_df) > 0:
        print(f"Beta range: {roll_df['beta'].min():.4f} - {roll_df['beta'].max():.4f}")
        print(f"Beta mean: {roll_df['beta'].mean():.4f}")
        print(f"Cointegrated @5%: {roll_df['is_cointegrated_5pct'].sum()} / {len(roll_df)}")
    
    # Generate dynamic signals
    print("\nGenerating dynamic signals...")
    dyn_result = rolling.generate_dynamic_signals(
        df['rb_log'], df['hc_log'],
        df['rb_close'], df['hc_close'],
        entry_z=2.0, exit_z=0.0, stop_loss_z=3.0,
        max_holding_days=30
    )
    
    signals = dyn_result['signals']
    
    valid_beta = dyn_result['rolling_beta'][~np.isnan(dyn_result['rolling_beta'])]
    print(f"\nRolling beta statistics:")
    print(f"  Valid windows: {len(valid_beta)}")
    if len(valid_beta) > 0:
        print(f"  Mean: {np.mean(valid_beta):.4f}")
        print(f"  Std: {np.std(valid_beta):.4f}")
        print(f"  Min: {np.min(valid_beta):.4f}")
        print(f"  Max: {np.max(valid_beta):.4f}")
    
    print(f"\nCointegration stability:")
    valid_coint = dyn_result['is_cointegrated'][~np.isnan(dyn_result['rolling_beta'])]
    if len(valid_coint) > 0:
        print(f"  Days cointegrated @5%: {np.sum(valid_coint)} / {len(valid_coint)}")
        print(f"  Cointegration ratio: {np.sum(valid_coint)/len(valid_coint):.2%}")
    
    print(f"\nDynamic strategy backtest:")
    if len(valid_beta) > 0:
        avg_beta = np.nanmean(dyn_result['rolling_beta'])
        engine = BacktestEngine(initial_capital=1000000, transaction_cost=0.0005)
        bt_result = engine.run_backtest(signals, avg_beta)
        
        print(f"  Total return: {bt_result['total_return']:.2%}")
        print(f"  Sharpe ratio: {bt_result['sharpe_ratio']:.4f}")
        print(f"  Max drawdown: {bt_result['max_drawdown']:.2%}")
        print(f"  Number of trades: {bt_result['num_trades']}")
        print(f"  Win rate: {bt_result['win_rate']:.2%}")
