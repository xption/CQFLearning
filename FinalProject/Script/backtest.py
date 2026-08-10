"""
CQF Final Project - TS: Pairs Trading
Backtesting Engine Module (Revised)
Author: CQF Candidate
Date: 2026
"""

import numpy as np
import pandas as pd


class BacktestEngine:
    """
    Backtesting engine for pairs trading strategy.
    
    Features:
    - Daily mark-to-market P&L calculation
    - Transaction cost modeling
    - Position sizing based on hedge ratio
    - Comprehensive performance metrics
    - Trade-by-trade P&L tracking
    """
    
    def __init__(self, initial_capital=1000000, transaction_cost=0.0005, 
                 contract_multiplier_rb=10, contract_multiplier_hc=10):
        """
        Initialize backtest engine.
        
        Args:
            initial_capital: Initial capital in RMB
            transaction_cost: Transaction cost per trade (fraction of notional)
            contract_multiplier_rb: Contract multiplier for RB (10 tons/contract)
            contract_multiplier_hc: Contract multiplier for HC (10 tons/contract)
        """
        self.initial_capital = initial_capital
        self.transaction_cost = transaction_cost
        self.contract_multiplier_rb = contract_multiplier_rb
        self.contract_multiplier_hc = contract_multiplier_hc
        
    def run_backtest(self, signals, beta):
        """
        Run backtest on trading signals.
        
        Args:
            signals: DataFrame with position, rb_price, hc_price columns
            beta: Hedge ratio from cointegration regression
            
        Returns:
            Dictionary with backtest results
        """
        n = len(signals)
        
        # Initialize tracking arrays
        portfolio_value = np.zeros(n)
        daily_pnl = np.zeros(n)
        rb_contracts = np.zeros(n)  # Number of contracts (positive=long, negative=short)
        hc_contracts = np.zeros(n)
        cash = np.zeros(n)
        
        # Trade tracking
        trades = []
        current_trade = None
        trade_count = 0
        
        # State variables
        current_cash = self.initial_capital
        current_rb = 0.0  # RB contracts held
        current_hc = 0.0  # HC contracts held
        prev_rb_price = 0
        prev_hc_price = 0
        
        for i in range(n):
            rb_price = float(signals['rb_price'].iloc[i])
            hc_price = float(signals['hc_price'].iloc[i])
            pos = int(signals['position'].iloc[i])
            trade_type = str(signals['trade_type'].iloc[i])
            
            # Calculate daily P&L from position marking
            if i > 0 and current_rb != 0:
                rb_pnl = current_rb * (rb_price - prev_rb_price) * self.contract_multiplier_rb
                hc_pnl = current_hc * (hc_price - prev_hc_price) * self.contract_multiplier_hc
                daily_pnl[i] = rb_pnl + hc_pnl
                current_cash += daily_pnl[i]
            
            # Check for entry signal
            if trade_type.startswith('entry') and current_rb == 0:
                trade_count += 1
                
                # Calculate position sizes (dollar neutral, 50% of cash per leg notional)
                notional_per_leg = current_cash * 0.4  # Use 40% per leg = 80% total, leave 20% buffer
                
                if trade_type == 'entry_long':
                    # Long RB, Short HC
                    rb_qty = notional_per_leg / (rb_price * self.contract_multiplier_rb)
                    hc_qty = beta * notional_per_leg / (hc_price * self.contract_multiplier_hc)
                    
                    current_rb = rb_qty
                    current_hc = -hc_qty
                else:
                    # Short RB, Long HC
                    rb_qty = notional_per_leg / (rb_price * self.contract_multiplier_rb)
                    hc_qty = beta * notional_per_leg / (hc_price * self.contract_multiplier_hc)
                    
                    current_rb = -rb_qty
                    current_hc = hc_qty
                
                # Transaction cost for opening
                notional_rb = abs(current_rb) * rb_price * self.contract_multiplier_rb
                notional_hc = abs(current_hc) * hc_price * self.contract_multiplier_hc
                open_cost = (notional_rb + notional_hc) * self.transaction_cost
                current_cash -= open_cost
                
                # Record trade entry
                current_trade = {
                    'entry_idx': i,
                    'entry_rb_price': rb_price,
                    'entry_hc_price': hc_price,
                    'rb_contracts': current_rb,
                    'hc_contracts': current_hc,
                    'direction': 'long' if 'long' in trade_type else 'short',
                    'open_cost': open_cost,
                    'entry_zscore': float(signals['zscore'].iloc[i]) if 'zscore' in signals.columns else 0,
                }
            
            # Check for exit signal
            elif trade_type.startswith('exit') and current_rb != 0:
                # Transaction cost for closing
                notional_rb = abs(current_rb) * rb_price * self.contract_multiplier_rb
                notional_hc = abs(current_hc) * hc_price * self.contract_multiplier_hc
                close_cost = (notional_rb + notional_hc) * self.transaction_cost
                current_cash -= close_cost
                
                # Calculate trade P&L
                if current_trade is not None:
                    rb_pnl_total = current_rb * (rb_price - current_trade['entry_rb_price']) * self.contract_multiplier_rb
                    hc_pnl_total = current_hc * (hc_price - current_trade['entry_hc_price']) * self.contract_multiplier_hc
                    total_pnl = rb_pnl_total + hc_pnl_total - current_trade['open_cost'] - close_cost
                    
                    current_trade['exit_idx'] = i
                    current_trade['exit_rb_price'] = rb_price
                    current_trade['exit_hc_price'] = hc_price
                    current_trade['exit_reason'] = trade_type.replace('exit_', '')
                    current_trade['total_pnl'] = total_pnl
                    current_trade['close_cost'] = close_cost
                    current_trade['holding_days'] = i - current_trade['entry_idx']
                    current_trade['is_win'] = total_pnl > 0
                    current_trade['exit_zscore'] = float(signals['zscore'].iloc[i]) if 'zscore' in signals.columns else 0
                    
                    trades.append(current_trade)
                    current_trade = None
                
                # Close positions
                current_rb = 0
                current_hc = 0
            
            # Update portfolio value
            rb_mtm = current_rb * rb_price * self.contract_multiplier_rb
            hc_mtm = current_hc * hc_price * self.contract_multiplier_hc
            portfolio_value[i] = current_cash + rb_mtm + hc_mtm
            
            # Store values
            rb_contracts[i] = current_rb
            hc_contracts[i] = current_hc
            cash[i] = current_cash
            
            prev_rb_price = rb_price
            prev_hc_price = hc_price
        
        # Calculate performance metrics
        portfolio_series = pd.Series(portfolio_value)
        daily_returns = portfolio_series.pct_change().dropna()
        
        # Total return
        total_return = (portfolio_value[-1] - self.initial_capital) / self.initial_capital
        
        # Annualized return (assuming 252 trading days)
        n_days = len(portfolio_value)
        ann_return = (1 + total_return) ** (252 / n_days) - 1 if n_days > 0 else 0
        
        # Annualized volatility
        ann_vol = daily_returns.std() * np.sqrt(252) if len(daily_returns) > 0 else 0
        
        # Sharpe ratio (assuming 0 risk-free rate)
        sharpe_ratio = ann_return / ann_vol if ann_vol > 0 else 0
        
        # Max drawdown
        cummax = portfolio_series.cummax()
        drawdown = (portfolio_series - cummax) / cummax
        max_drawdown = drawdown.min()
        
        # Win rate
        wins = sum(1 for t in trades if t['is_win'])
        losses = sum(1 for t in trades if not t['is_win'])
        win_rate = wins / len(trades) if len(trades) > 0 else 0
        
        # Profit factor
        total_profit = sum(t['total_pnl'] for t in trades if t['is_win'])
        total_loss = sum(abs(t['total_pnl']) for t in trades if not t['is_win'])
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        
        # Calmar ratio
        calmar_ratio = ann_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        # Sortino ratio (downside deviation)
        downside_returns = daily_returns[daily_returns < 0]
        downside_vol = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0
        sortino_ratio = ann_return / downside_vol if downside_vol > 0 else 0
        
        results = {
            'portfolio_value': portfolio_value,
            'daily_pnl': daily_pnl,
            'daily_returns': daily_returns.values,
            'rb_position': rb_contracts,
            'hc_position': hc_contracts,
            'cash': cash,
            'drawdown': drawdown.values,
            'trades': trades,
            'total_return': total_return,
            'annualized_return': ann_return,
            'annualized_volatility': ann_vol,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'calmar_ratio': calmar_ratio,
            'max_drawdown': max_drawdown,
            'num_trades': len(trades),
            'wins': wins,
            'losses': losses,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'total_profit': total_profit,
            'total_loss': total_loss,
            'initial_capital': self.initial_capital,
            'final_capital': portfolio_value[-1],
            'n_days': n_days,
        }
        
        return results


def calculate_trade_analytics(signals, beta, contract_multiplier_rb=10, contract_multiplier_hc=10):
    """
    Calculate detailed trade-by-trade analytics.
    
    Args:
        signals: DataFrame with trading signals
        beta: Hedge ratio
        contract_multiplier_rb: RB contract multiplier
        contract_multiplier_hc: HC contract multiplier
        
    Returns:
        DataFrame with individual trade details
    """
    engine = BacktestEngine(
        contract_multiplier_rb=contract_multiplier_rb,
        contract_multiplier_hc=contract_multiplier_hc
    )
    bt_result = engine.run_backtest(signals, beta)
    
    trades = bt_result['trades']
    if not trades:
        return pd.DataFrame()
    
    trades_df = pd.DataFrame(trades)
    
    # Add return percentage
    if 'entry_rb_price' in trades_df.columns:
        entry_notional = (trades_df['entry_rb_price'] * contract_multiplier_rb * abs(trades_df['rb_contracts']) +
                         trades_df['entry_hc_price'] * contract_multiplier_hc * abs(trades_df['hc_contracts']))
        trades_df['return_pct'] = trades_df['total_pnl'] / entry_notional * 100
    
    return trades_df


if __name__ == "__main__":
    from data_loader import load_pair_data
    from cointegration import engle_granger_cointegration
    from ou_process import calculate_zscore
    from strategy import PairsTradingStrategy
    import os
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rb_path = os.path.join(base_dir, 'data', 'rb-2023-2025.csv')
    hc_path = os.path.join(base_dir, 'data', 'hc-2023-2025.csv')
    
    df = load_pair_data(rb_path, hc_path)
    eg_result = engle_granger_cointegration(df['rb_log'], df['hc_log'])
    zscore = calculate_zscore(eg_result['residuals'])
    
    strategy = PairsTradingStrategy(entry_z=2.0, exit_z=0.0, stop_loss_z=3.0, max_holding_days=30)
    signals = strategy.generate_signals(zscore, df['rb_close'], df['hc_close'], eg_result['beta'])
    
    print("=== Backtest Results ===")
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
    print(f"Wins: {bt_result['wins']}, Losses: {bt_result['losses']}")
    print(f"Win rate: {bt_result['win_rate']:.2%}")
    print(f"Profit factor: {bt_result['profit_factor']:.4f}")
    print(f"Total profit: ¥{bt_result['total_profit']:,.0f}")
    print(f"Total loss: ¥{bt_result['total_loss']:,.0f}")
    
    print("\n=== Trade Details ===")
    trades_df = calculate_trade_analytics(signals, eg_result['beta'])
    if len(trades_df) > 0:
        print(f"Total trades: {len(trades_df)}")
        print(f"Avg holding days: {trades_df['holding_days'].mean():.1f}")
        print(f"Avg P&L per trade: ¥{trades_df['total_pnl'].mean():,.0f}")
        print(f"Best trade: ¥{trades_df['total_pnl'].max():,.0f}")
        print(f"Worst trade: ¥{trades_df['total_pnl'].min():,.0f}")
        print(f"\nExit reasons:")
        print(trades_df['exit_reason'].value_counts().to_string())
        print(f"\nAll trades:")
        for i, t in enumerate(trades_df.itertuples()):
            print(f"  Trade {i+1}: {t.direction:5s} | P&L: ¥{t.total_pnl:>10,.0f} | "
                  f"Hold: {t.holding_days:3d}d | Exit: {t.exit_reason}")
