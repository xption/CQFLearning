# CQF Final Project - TS: Pairs Trading
# RB & HC Futures Pairs Trading Strategy

## Author: CQF Candidate
## Date: August 2026

### Project Overview
This project implements a cointegration-based pairs trading strategy on Chinese steel futures (RB - rebar, HC - hot-rolled coil) using daily data from 2023 to 2025.

### File Structure
```
.
├── code/
│   ├── data_loader.py       # Data loading and preprocessing
│   ├── cointegration.py     # Engle-Granger cointegration test, ADF, Hurst, VR
│   ├── ou_process.py        # Ornstein-Uhlenbeck process fitting
│   ├── strategy.py          # Trading strategy and threshold optimization
│   ├── backtest.py          # Backtesting engine
│   ├── rolling.py           # Rolling window dynamic cointegration
│   ├── visualization.py     # Visualization functions
│   └── main.py              # Main execution script
└── data/
    ├── rb-2023-2025.csv     # RB futures daily data
    └── hc-2023-2025.csv     # HC futures daily data
```

### How to Run
```bash
cd code
python main.py
```

### Dependencies
- Python 3.8+
- numpy
- pandas
- statsmodels
- matplotlib
- scipy

### Key Results
- Cointegration: Significant at 1% level (ADF = -4.57, p = 0.0001)
- Hedge ratio (beta): 1.078
- Half-life of mean reversion: ~18 days
- Optimal strategy: entry at 2.4σ, exit at 0.8σ
- Sharpe ratio: 0.30
- Total return (3 years): 4.79%
- Win rate: 100% (4 trades)
