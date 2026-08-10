"""
CQF Final Project - TS: Pairs Trading
Trading Strategy and Threshold Optimization Module
Author: CQF Candidate
Date: 2026
"""

import numpy as np
import pandas as pd


class PairsTradingStrategy:
    """
    Pairs trading strategy based on cointegration residuals and z-score.
    
    Entry: z-score crosses entry threshold (open position)
    Exit: z-score reverts to mean / exit threshold (close position)
    Stop-loss: z-score exceeds stop-loss threshold (risk management)
    """
    
    def __init__(self, entry_z=2.0, exit_z=0.0, stop_loss_z=3.0, 
                 max_holding_days=30, transaction_cost=0.0005):
        """
        Initialize pairs trading strategy.
        
        Args:
            entry_z: Z-score entry threshold (open position when |z| > entry_z)
            exit_z: Z-score exit threshold (close position when |z| < exit_z)
            stop_loss_z: Z-score stop-loss threshold
            max_holding_days: Maximum holding period for a position
            transaction_cost: Transaction cost per trade (fraction of notional)
        """
        self.entry_z = entry_z
        self.exit_z = exit_z
        self.stop_loss_z = stop_loss_z
        self.max_holding_days = max_holding_days
        self.transaction_cost = transaction_cost
        
    def generate_signals(self, zscore, rb_price, hc_price, beta):
        """
        Generate trading signals from z-score series.
        
        Position types:
        - 0: No position
        - 1: Long RB, Short HC (spread is low, expect it to widen)
        - -1: Short RB, Long HC (spread is high, expect it to narrow)
        
        Args:
            zscore: Z-score of cointegration residuals
            rb_price: RB price series
            hc_price: HC price series
            beta: Hedge ratio (beta from cointegration regression)
            
        Returns:
            DataFrame with signals and positions
        """
        n = len(zscore)
        signals = pd.DataFrame({
            'zscore': zscore,
            'rb_price': rb_price.values if hasattr(rb_price, 'values') else rb_price,
            'hc_price': hc_price.values if hasattr(hc_price, 'values') else hc_price,
        })
        
        position = 0  # 0: flat, 1: long spread, -1: short spread
        entry_z_val = 0
        holding_days = 0
        positions = np.zeros(n)
        entry_dates = [None] * n
        exit_dates = [None] * n
        trade_types = [''] * n
        
        for i in range(n):
            z = zscore[i]
            
            if position == 0:
                # Look for entry signals
                if z > self.entry_z:
                    # Spread is too high: short RB, long HC
                    position = -1
                    entry_z_val = z
                    holding_days = 0
                    trade_types[i] = 'entry_short'
                elif z < -self.entry_z:
                    # Spread is too low: long RB, short HC
                    position = 1
                    entry_z_val = z
                    holding_days = 0
                    trade_types[i] = 'entry_long'
            else:
                holding_days += 1
                
                # Check exit conditions
                should_exit = False
                exit_reason = ''
                
                # Mean reversion exit
                if position == -1 and z < self.exit_z:
                    should_exit = True
                    exit_reason = 'mean_reversion'
                elif position == 1 and z > -self.exit_z:
                    should_exit = True
                    exit_reason = 'mean_reversion'
                
                # Stop loss
                if position == -1 and z > self.stop_loss_z:
                    should_exit = True
                    exit_reason = 'stop_loss'
                elif position == 1 and z < -self.stop_loss_z:
                    should_exit = True
                    exit_reason = 'stop_loss'
                
                # Max holding period
                if holding_days >= self.max_holding_days:
                    should_exit = True
                    exit_reason = 'max_holding'
                
                if should_exit:
                    trade_types[i] = f'exit_{exit_reason}'
                    position = 0
                    holding_days = 0
            
            positions[i] = position
        
        signals['position'] = positions
        signals['trade_type'] = trade_types
        signals['holding_days'] = 0
        
        # Calculate holding days for each position
        current_hold = 0
        for i in range(n):
            if positions[i] != 0:
                current_hold += 1
                signals.loc[i, 'holding_days'] = current_hold
            else:
                current_hold = 0
        
        return signals


def optimize_threshold(zscore, rb_price, hc_price, beta, 
                       entry_range=(1.0, 3.0), exit_range=(0.0, 1.0),
                       step=0.1, metric='sharpe'):
    """
    Grid search for optimal entry and exit z-score thresholds.
    
    Args:
        zscore: Z-score series
        rb_price: RB price series
        hc_price: HC price series
        beta: Hedge ratio
        entry_range: Range of entry thresholds to test
        exit_range: Range of exit thresholds to test
        step: Step size for grid search
        metric: Optimization metric ('sharpe', 'total_return', 'win_rate')
        
    Returns:
        Dictionary with optimization results
    """
    from backtest import BacktestEngine
    
    entry_values = np.arange(entry_range[0], entry_range[1] + step, step)
    exit_values = np.arange(exit_range[0], exit_range[1] + step, step)
    
    results = []
    
    for entry_z in entry_values:
        for exit_z in exit_values:
            if exit_z >= entry_z:
                continue
                
            strategy = PairsTradingStrategy(
                entry_z=entry_z, 
                exit_z=exit_z,
                stop_loss_z=entry_z + 1.0,
                max_holding_days=60
            )
            
            signals = strategy.generate_signals(zscore, rb_price, hc_price, beta)
            
            engine = BacktestEngine(initial_capital=1000000, transaction_cost=0.0005)
            bt_result = engine.run_backtest(signals, beta)
            
            results.append({
                'entry_z': entry_z,
                'exit_z': exit_z,
                'total_return': bt_result['total_return'],
                'sharpe_ratio': bt_result['sharpe_ratio'],
                'max_drawdown': bt_result['max_drawdown'],
                'num_trades': bt_result['num_trades'],
                'win_rate': bt_result['win_rate'],
                'profit_factor': bt_result['profit_factor'],
            })
    
    results_df = pd.DataFrame(results)
    
    # Find best parameters
    if metric == 'sharpe':
        best_idx = results_df['sharpe_ratio'].idxmax()
    elif metric == 'total_return':
        best_idx = results_df['total_return'].idxmax()
    elif metric == 'win_rate':
        best_idx = results_df['win_rate'].idxmax()
    else:
        best_idx = results_df['sharpe_ratio'].idxmax()
    
    best_params = results_df.iloc[best_idx].to_dict()
    
    return {
        'all_results': results_df,
        'best_params': best_params,
        'best_entry_z': best_params['entry_z'],
        'best_exit_z': best_params['exit_z'],
        'metric': metric,
    }


def calculate_position_sizing(capital, rb_price, hc_price, beta, position_type):
    """
    Calculate position sizes for both legs of the pair trade.
    
    For a dollar-neutral pair:
    - Value of RB position = capital / 2
    - Value of HC position = capital / 2
    
    Adjusted by hedge ratio beta:
    - Number of RB contracts = (capital / 2) / rb_price
    - Number of HC contracts = beta * (capital / 2) / hc_price
    
    Args:
        capital: Total capital allocated
        rb_price: Current RB price
        hc_price: Current HC price
        beta: Hedge ratio
        position_type: 1 (long RB, short HC) or -1 (short RB, long HC)
        
    Returns:
        Dictionary with position sizes
    """
    capital_per_leg = capital / 2
    
    rb_contracts = capital_per_leg / rb_price
    hc_contracts = beta * capital_per_leg / hc_price
    
    if position_type == 1:
        # Long RB, Short HC
        rb_position = rb_contracts
        hc_position = -hc_contracts
    else:
        # Short RB, Long HC
        rb_position = -rb_contracts
        hc_position = hc_contracts
    
    return {
        'rb_contracts': rb_position,
        'hc_contracts': hc_position,
        'rb_notional': abs(rb_position) * rb_price,
        'hc_notional': abs(hc_position) * hc_price,
        'total_notional': abs(rb_position) * rb_price + abs(hc_position) * hc_price,
    }


if __name__ == "__main__":
    from data_loader import load_pair_data
    from cointegration import engle_granger_cointegration
    from ou_process import calculate_zscore
    import os
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rb_path = os.path.join(base_dir, 'data', 'rb-2023-2025.csv')
    hc_path = os.path.join(base_dir, 'data', 'hc-2023-2025.csv')
    
    df = load_pair_data(rb_path, hc_path)
    eg_result = engle_granger_cointegration(df['rb_log'], df['hc_log'])
    zscore = calculate_zscore(eg_result['residuals'])
    
    print("=== Strategy Signal Generation ===")
    strategy = PairsTradingStrategy(entry_z=2.0, exit_z=0.0, stop_loss_z=3.0, max_holding_days=30)
    signals = strategy.generate_signals(zscore, df['rb_close'], df['hc_close'], eg_result['beta'])
    
    print(f"Total days: {len(signals)}")
    print(f"Days in position: {(signals['position'] != 0).sum()}")
    print(f"Days flat: {(signals['position'] == 0).sum()}")
    
    # Count trades
    entry_trades = signals[signals['trade_type'].str.startswith('entry')]
    print(f"Total entry trades: {len(entry_trades)}")
    print(f"Long entries: {(entry_trades['trade_type'] == 'entry_long').sum()}")
    print(f"Short entries: {(entry_trades['trade_type'] == 'entry_short').sum()}")
    
    # Exit reasons
    exit_trades = signals[signals['trade_type'].str.startswith('exit')]
    print(f"\nExit reasons:")
    for reason in ['mean_reversion', 'stop_loss', 'max_holding']:
        count = exit_trades['trade_type'].str.contains(reason).sum()
        print(f"  {reason}: {count}")
    
    print("\n=== Threshold Optimization ===")
    print("Running grid search... (this may take a moment)")
    
    opt_result = optimize_threshold(
        zscore, df['rb_close'], df['hc_close'], eg_result['beta'],
        entry_range=(1.0, 2.5), exit_range=(0.0, 0.8), step=0.2,
        metric='sharpe'
    )
    
    print(f"\nBest parameters (optimized for Sharpe ratio):")
    print(f"  Entry z-score: {opt_result['best_entry_z']:.1f}")
    print(f"  Exit z-score: {opt_result['best_exit_z']:.1f}")
    print(f"  Sharpe ratio: {opt_result['best_params']['sharpe_ratio']:.4f}")
    print(f"  Total return: {opt_result['best_params']['total_return']:.2%}")
    print(f"  Max drawdown: {opt_result['best_params']['max_drawdown']:.2%}")
    print(f"  Number of trades: {opt_result['best_params']['num_trades']}")
    print(f"  Win rate: {opt_result['best_params']['win_rate']:.2%}")
