#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动修复notebook中的函数调用错误
根据实际的函数签名和返回值修复Cell 20
"""

import json
import re

# 定义所有函数的正确调用方式和返回值
FUNCTION_SPECS = {
    'engle_granger_cointegration': {
        'params': ['y', 'x'],
        'returns': {
            'alpha': 'float',
            'beta': 'float',
            'residuals': 'array',
            'adf_statistic': 'float',
            'adf_pvalue': 'float',
            'is_cointegrated_1pct': 'bool',
            'is_cointegrated_5pct': 'bool',
            'is_cointegrated_10pct': 'bool',
            'r_squared': 'float',
            'residual_std': 'float',
            'residual_mean': 'float',
        }
    },
    'half_life': {
        'params': ['residuals'],
        'returns': {
            'theta': 'float',
            'half_life': 'float',
            'ar_coeff': 'float',
            'r_squared': 'float',
        }
    },
    'fit_ou_process': {
        'params': ['residuals', 'dt=1.0'],
        'returns': {
            'theta_mle': 'float',
            'mu_mle': 'float',
            'sigma_mle': 'float',
            'theta_ls': 'float',
            'mu_ls': 'float',
            'sigma_ls': 'float',
            'half_life_mle': 'float',
        }
    },
    'calculate_zscore': {
        'params': ['residuals', 'window=None'],
        'returns': 'Series',
    },
    'optimize_threshold': {
        'params': ['zscore', 'rb_price', 'hc_price', 'beta', 'entry_range=(1.0, 3.0)', 'exit_range=(0.0, 1.0)', 'step=0.1', 'metric="sharpe"'],
        'returns': {
            'all_results': 'DataFrame',
            'best_params': 'dict',
            'best_entry_z': 'float',
            'best_exit_z': 'float',
            'metric': 'str',
        }
    },
}

# 定义需要修复的错误模式
FIXES = [
    # engle_granger_cointegration 返回值
    (r"coint_result\['adf_stat'\]", "coint_result['adf_statistic']"),
    (r"coint_result\['is_cointegrated'\](?!')", "coint_result['is_cointegrated_5pct']"),

    # fit_ou_process 返回值
    (r"ou_params\['theta'\](?!_)", "ou_params['theta_mle']"),
    (r"ou_params\['mu'\](?!_)", "ou_params['mu_mle']"),
    (r"ou_params\['sigma'\](?!_)", "ou_params['sigma_mle']"),

    # half_life 返回值
    (r"half_life_days\s*=\s*half_life\(([^)]+)\)", r"half_life_result = half_life(\1)"),
    (r"\{half_life_days", "{half_life_result['half_life']"),

    # calculate_zscore 调用
    (r"calculate_zscore\(([^,]+),\s*ou_params\['mu_mle'\],\s*ou_params\['sigma_mle'\]\)", r"calculate_zscore(\1)"),

    # optimize_threshold 调用
    (r"optimize_threshold\(\s*residuals=residuals,\s*zscore=zscore,",
     "optimize_threshold(\n    zscore=zscore,\n    rb_price=df['rb_close'].values,\n    hc_price=df['hc_close'].values,\n    beta=beta,"),
    (r"z_open_range=", "entry_range="),
    (r"z_close_range=", "exit_range="),

    # optimize_threshold 返回值
    (r"best_params\['z_open'\]", "best_params['best_entry_z']"),
    (r"best_params\['z_close'\]", "best_params['best_exit_z']"),
    (r"best_params\['sharpe'\]", "best_params['best_params']['sharpe_ratio']"),
]

def fix_notebook():
    """修复notebook中的所有函数调用错误"""

    print("=" * 70)
    print("自动修复Notebook")
    print("=" * 70)

    # 读取notebook
    with open('CQF_Pairs_Trading_Complete.ipynb', 'r', encoding='utf-8') as f:
        nb = json.load(f)

    # 获取Cell 20
    cell20 = nb['cells'][20]
    source = '\n'.join(cell20['source'])
    original_source = source

    # 应用所有修复
    fixes_applied = []
    for pattern, replacement in FIXES:
        matches = re.findall(pattern, source)
        if matches:
            source = re.sub(pattern, replacement, source)
            fixes_applied.append((pattern, replacement, len(matches)))

    if fixes_applied:
        print(f"\n应用了 {len(fixes_applied)} 个修复:")
        for pattern, replacement, count in fixes_applied:
            print(f"  - {count}x: {pattern[:50]}... -> {replacement[:50]}...")

        # 更新notebook
        nb['cells'][20]['source'] = source.split('\n')

        # 保存
        with open('CQF_Pairs_Trading_Complete.ipynb', 'w', encoding='utf-8') as f:
            json.dump(nb, f, ensure_ascii=False, indent=1)

        print("\nNotebook已更新并保存!")
    else:
        print("\n没有发现需要修复的问题")

    print("=" * 70)

    return len(fixes_applied) > 0

if __name__ == '__main__':
    fixed = fix_notebook()
    exit(0 if fixed else 1)
