# CQF Pairs Trading - Jupyter Notebook 说明

## 📓 Notebook信息

**文件名**: `CQF_Pairs_Trading_Complete.ipynb`  
**大小**: 114 KB  
**总单元格**: 20个  
**结构**: 11个Markdown + 9个代码单元格

---

## 📋 Notebook结构

### 第1部分：标题与介绍
- 项目信息
- CQF技术要求完成情况
- Notebook结构说明

### 第2部分：环境准备
- 导入所有Python库
- 设置显示和绘图参数
- 版本信息显示

### 第3部分：模块1 - 数据加载 (data_loader.py)
- `load_pair_data()`: 加载RB和HC期货数据
- `verify_data_quality()`: 数据质量检查
- 期货换月跳空修正
- 对数价格和价差计算

### 第4部分：模块2 - 协整检验 (cointegration.py)
**CQF强制要求**:
- `adf_test()`: ADF平稳性检验（自主编码）
- `engle_granger_cointegration()`: EG两步法协整检验（自主编码）
- `half_life()`: 半衰期计算
- `johansen_cointegration()`: Johansen多元协整检验
- `vecm_analysis()`: VECM向量误差修正模型

### 第5部分：模块3 - OU过程 (ou_process.py)
- `fit_ou_process()`: MLE极大似然估计OU参数
- `calculate_zscore()`: Z-score标准化
- 均值回归速度、长期均值、波动率计算

### 第6部分：模块4 - 交易策略 (strategy.py)
**CQF强制要求**:
- `PairsTradingStrategy`: 配对交易策略类
- `optimize_threshold()`: Z-score阈值优化（网格遍历）
- 交易信号生成
- 持仓管理

### 第7部分：模块5 - 回测引擎 (backtest.py)
- `BacktestEngine`: 回测引擎类
- `calculate_trade_analytics()`: 交易分析
- 绩效指标：收益率、夏普比率、最大回撤、胜率等

### 第8部分：模块6 - 滚动窗口 (rolling.py)
- `RollingCointegration`: 滚动窗口协整分析
- 8个月窗口，10日滚动
- 动态对冲比率演化
- 结构断裂识别

### 第9部分：模块7 - 可视化 (visualization.py)
- `generate_all_figures()`: 生成所有图表
- 价格走势图、价差图、Z-score图
- 交易信号图、累计收益图、回撤图
- 滚动窗口分析图

### 第10部分：主执行流程
完整的分析pipeline：
1. 数据加载
2. 协整检验
3. OU过程拟合
4. 阈值优化
5. 静态策略回测
6. 滚动窗口分析
7. 结果总结

### 第11部分：结论
- 主要发现
- CQF技术要求完成情况
- 研究价值

---

## 🚀 如何使用

### 方法1：在Jupyter中运行
```bash
# 启动Jupyter Notebook
jupyter notebook CQF_Pairs_Trading_Complete.ipynb

# 或使用JupyterLab
jupyter lab CQF_Pairs_Trading_Complete.ipynb
```

### 方法2：在VS Code中运行
1. 用VS Code打开 `CQF_Pairs_Trading_Complete.ipynb`
2. 选择Python环境（venv）
3. 点击"Run All"执行所有单元格

### 方法3：转换为Python脚本
```bash
# 转换为.py文件
jupyter nbconvert --to script CQF_Pairs_Trading_Complete.ipynb

# 运行生成的脚本
python CQF_Pairs_Trading_Complete.py
```

---

## 📁 所需数据文件

确保以下数据文件在正确位置：
```
Script/
├── CQF_Pairs_Trading_Complete.ipynb  ← 主notebook
└── data/
    ├── rb-2023-2025.csv               ← 螺纹钢数据
    └── hc-2023-2025.csv               ← 热轧板数据
```

---

## ✅ CQF技术要求验证

| 技术要求 | 实现位置 | 状态 |
|---------|---------|------|
| 矩阵形式VAR | 模块2: cointegration.py | ✅ |
| EG两步法（自主编码） | 模块2: `engle_granger_cointegration()` | ✅ |
| 均值回归评估 | 模块2: `half_life()` + 模块3: OU拟合 | ✅ |
| Z-score优化 | 模块4: `optimize_threshold()` | ✅ |
| Johansen协整 | 模块2: `johansen_cointegration()` | ✅ |
| VECM模型 | 模块2: `vecm_analysis()` | ✅ |
| OU过程MLE | 模块3: `fit_ou_process()` | ✅ |
| 滚动窗口分析 | 模块6: `RollingCointegration` | ✅ |

---

## 📊 预期输出

运行完整的notebook将产生：

### 1. 数据统计
- 交易日数：727天
- 日期范围：2023-01-03 至 2025-12-31
- 价格相关性：0.9904

### 2. 协整检验结果
- 对冲比率 β：1.078
- 截距项 α：-0.6786
- ADF统计量：-4.57
- p值：0.0001（1%显著）

### 3. OU过程参数
- 均值回归速度 θ：0.0381
- 长期均值 μ：-0.0019
- 波动率 σ：0.003812
- 半衰期：18.2天

### 4. 最优策略参数
- 开仓阈值：2.4σ
- 平仓阈值：0.8σ
- 优化目标：夏普比率最大化

### 5. 静态策略绩效
- 累计收益率：4.79%
- 年化收益率：1.67%
- 夏普比率：0.30
- 最大回撤：7.45%
- 交易次数：4次
- 胜率：100%

### 6. 滚动窗口分析
- 有效窗口数：559个
- 协整通过率：34.88%
- 动态策略收益：+0.17%

---

## 📝 提交说明

### 作为CODE.zip的一部分提交

**推荐提交内容**：
```
TS_[YourName]_CODE.zip
├── CQF_Pairs_Trading_Complete.ipynb   ← 完整的分析代码
├── data/
│   ├── rb-2023-2025.csv
│   └── hc-2023-2025.csv
├── README.md                           ← 运行说明
└── requirements.txt                    ← Python依赖
```

**不需要单独提交的文件**：
- ❌ 各个独立的.py模块（已整合到notebook中）
- ❌ 生成的图表（notebook中可重新生成）

---

## 🔧 环境要求

```
Python >= 3.11
numpy >= 1.24.0
pandas >= 2.0.0
matplotlib >= 3.7.0
seaborn >= 0.12.0
scipy >= 1.10.0
statsmodels >= 0.14.0
```

安装依赖：
```bash
pip install numpy pandas matplotlib seaborn scipy statsmodels jupyter
```

---

## ⚠️ 注意事项

1. **数据路径**: 确保数据文件在 `data/` 目录下
2. **执行顺序**: 必须从上到下顺序执行所有单元格
3. **运行时间**: 完整执行约需要2-3分钟
4. **内存占用**: 约200-300MB

---

## 📞 技术支持

如果遇到问题：
1. 检查数据文件路径是否正确
2. 确认Python环境和依赖库版本
3. 查看notebook中的错误提示信息

---

**生成日期**: 2026-08-10  
**版本**: v1.0  
**状态**: ✅ 完整可用
