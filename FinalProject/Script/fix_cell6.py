import json

# 读取notebook
with open('CQF_Pairs_Trading_Complete.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# 定义正确的代码（使用单引号避免转义）
code_lines = [
    '# 加载数据',
    'print("正在加载期货数据...")',
    '',
    'rb_path = "data/rb-2023-2025.csv"',
    'hc_path = "data/hc-2023-2025.csv"',
    '',
    '# 调用数据加载函数',
    'df = load_pair_data(rb_path, hc_path)',
    '',
    'print("\n数据加载完成！")',
    'print(f"日期范围: {df[\'date\'].min().date()} 至 {df[\'date\'].max().date()}")',
    'print(f"交易日数: {len(df)}")',
    'print("\n数据预览:")',
    'print(df.head())',
    '',
    '# 数据质量检查',
    'print("\n执行数据质量检查...")',
    'verify_data_quality(df)',
    '',
    '# 显示基本统计',
    'print("\n价格统计:")',
    'print(df[["rb_close", "hc_close", "spread"]].describe())'
]

# 更新Cell 6
nb['cells'][6]['source'] = code_lines

# 保存
with open('CQF_Pairs_Trading_Complete.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("Cell 6 fixed!")
