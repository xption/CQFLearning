"""
CQF Final Project - TS: Pairs Trading
Data Loading and Preprocessing Module
Author: CQF Candidate
Date: 2026
"""

import pandas as pd
import numpy as np
import os


def parse_markdown_csv(filepath):
    """
    Parse a standard CSV file with futures data.
    
    Args:
        filepath: Path to the CSV file
        
    Returns:
        DataFrame with parsed data
    """
    df = pd.read_csv(filepath)
    
    # Convert numeric columns
    numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'hold', 'settle']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Convert date
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)
    
    return df


def load_pair_data(rb_path, hc_path):
    """
    Load and merge RB (螺纹钢) and HC (热轧板) futures data.
    
    Args:
        rb_path: Path to RB data file
        hc_path: Path to HC data file
        
    Returns:
        Merged DataFrame with both price series
    """
    rb_df = parse_markdown_csv(rb_path)
    hc_df = parse_markdown_csv(hc_path)
    
    # Rename columns
    rb_df = rb_df.rename(columns={
        'open': 'rb_open', 'high': 'rb_high', 'low': 'rb_low',
        'close': 'rb_close', 'volume': 'rb_volume', 'hold': 'rb_hold',
        'settle': 'rb_settle'
    })
    hc_df = hc_df.rename(columns={
        'open': 'hc_open', 'high': 'hc_high', 'low': 'hc_low',
        'close': 'hc_close', 'volume': 'hc_volume', 'hold': 'hc_hold',
        'settle': 'hc_settle'
    })
    
    # Merge on date (inner join - only common trading days)
    merged = pd.merge(rb_df[['date', 'rb_close', 'rb_volume', 'rb_hold']],
                      hc_df[['date', 'hc_close', 'hc_volume', 'hc_hold']],
                      on='date', how='inner')
    merged = merged.sort_values('date').reset_index(drop=True)
    
    # Compute log prices
    merged['rb_log'] = np.log(merged['rb_close'])
    merged['hc_log'] = np.log(merged['hc_close'])
    
    # Compute returns
    merged['rb_ret'] = merged['rb_close'].pct_change()
    merged['hc_ret'] = merged['hc_close'].pct_change()
    
    # Spread (price difference)
    merged['spread_price'] = merged['rb_close'] - merged['hc_close']
    merged['spread_log'] = merged['rb_log'] - merged['hc_log']
    
    return merged


def verify_data_quality(df):
    """
    Verify data quality and print summary statistics.
    
    Args:
        df: Merged DataFrame
        
    Returns:
        Dictionary of quality metrics
    """
    metrics = {}
    metrics['date_range'] = (df['date'].min(), df['date'].max())
    metrics['total_days'] = len(df)
    metrics['rb_missing'] = df['rb_close'].isna().sum()
    metrics['hc_missing'] = df['hc_close'].isna().sum()
    metrics['rb_price_range'] = (df['rb_close'].min(), df['rb_close'].max())
    metrics['hc_price_range'] = (df['hc_close'].min(), df['hc_close'].max())
    metrics['correlation'] = df['rb_close'].corr(df['hc_close'])
    metrics['log_correlation'] = df['rb_log'].corr(df['hc_log'])
    
    # Check for price gaps (potential roll issues)
    df['rb_gap'] = df['rb_close'].diff().abs()
    df['hc_gap'] = df['hc_close'].diff().abs()
    metrics['rb_max_gap'] = df['rb_gap'].max()
    metrics['hc_max_gap'] = df['hc_gap'].max()
    
    return metrics


if __name__ == "__main__":
    # Test data loading
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rb_path = os.path.join(base_dir, 'data', 'rb-2023-2025.csv')
    hc_path = os.path.join(base_dir, 'data', 'hc-2023-2025.csv')
    
    df = load_pair_data(rb_path, hc_path)
    metrics = verify_data_quality(df)
    
    print("=== Data Quality Report ===")
    print(f"Date range: {metrics['date_range'][0].date()} to {metrics['date_range'][1].date()}")
    print(f"Total trading days: {metrics['total_days']}")
    print(f"RB missing values: {metrics['rb_missing']}")
    print(f"HC missing values: {metrics['hc_missing']}")
    print(f"RB price range: {metrics['rb_price_range'][0]:.0f} - {metrics['rb_price_range'][1]:.0f}")
    print(f"HC price range: {metrics['hc_price_range'][0]:.0f} - {metrics['hc_price_range'][1]:.0f}")
    print(f"Price correlation: {metrics['correlation']:.4f}")
    print(f"Log price correlation: {metrics['log_correlation']:.4f}")
    print(f"RB max daily gap: {metrics['rb_max_gap']:.0f}")
    print(f"HC max daily gap: {metrics['hc_max_gap']:.0f}")
    
    print("\nFirst 5 rows:")
    print(df[['date', 'rb_close', 'hc_close', 'spread_log']].head())
    print("\nLast 5 rows:")
    print(df[['date', 'rb_close', 'hc_close', 'spread_log']].tail())
