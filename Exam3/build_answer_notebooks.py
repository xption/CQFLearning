# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parent

KERNEL_META = {
    "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    },
    "language_info": {
        "name": "python",
        "version": "3.11",
        "mimetype": "text/x-python",
        "codemirror_mode": {"name": "ipython", "version": 3},
        "pygments_lexer": "ipython3",
        "nbconvert_exporter": "python",
        "file_extension": ".py",
    },
}


def md(text: str):
    return nbf.v4.new_markdown_cell(text)


def code(text: str):
    return nbf.v4.new_code_cell(text)


def write_notebook(name: str, cells: list) -> None:
    nb = nbf.v4.new_notebook()
    nb["cells"] = cells
    nb["metadata"].update(KERNEL_META)
    nbf.write(nb, ROOT / name)


answer1_cells = [
    md(
        "# Question A：分类问题中的熵\n\n"
        "本题讨论决策树或其他分类算法中，熵如何衡量一个划分后的节点是否“纯”。"
    ),
    md(
        "## 答案概览\n\n"
        "| 判断 | 结论 | 理由 |\n"
        "|---|---|---|\n"
        "| (a) High entropy means the partitions are pure. | **False** | 高熵表示类别混杂，节点不纯。 |\n"
        "| (b) High entropy means the partitions are impure. | **True** | 在二分类中，正负样本越接近 50%/50%，熵越高，不确定性越大。 |"
    ),
    md(
        "## 理论解释\n\n"
        "对分类问题中的一个节点或分区，熵定义为：\n\n"
        "$$H(S)=-\\sum_{k=1}^{K}p_k\\log_2(p_k)$$\n\n"
        "其中 $p_k$ 是该节点中第 $k$ 类样本所占比例。熵衡量的是类别标签的不确定性，而不是模型误差本身。\n\n"
        "对于二分类问题，若正类比例为 $p$，负类比例为 $1-p$，则：\n\n"
        "$$H(p)=-p\\log_2(p)-(1-p)\\log_2(1-p)$$\n\n"
        "当一个节点中几乎全是同一类样本时，类别非常确定，熵接近 0，节点较纯。"
        "当两类样本比例接近 50% 和 50% 时，类别最难判断，熵达到最大值 1，节点最不纯。"
    ),
    code(
        r"""import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def binary_entropy(p):
    p = np.asarray(p, dtype=float)
    q = 1 - p
    out = np.zeros_like(p, dtype=float)
    mask = (p > 0) & (p < 1)
    out[mask] = -p[mask] * np.log2(p[mask]) - q[mask] * np.log2(q[mask])
    return out


examples = pd.DataFrame({"正类比例": [0.00, 0.10, 0.25, 0.50, 0.75, 0.90, 1.00]})
examples["负类比例"] = 1 - examples["正类比例"]
examples["熵"] = binary_entropy(examples["正类比例"]).round(4)
examples"""
    ),
    code(
        r"""p = np.linspace(0, 1, 501)
h = binary_entropy(p)

fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(p, h, color="#1f77b4", linewidth=2)
ax.axvline(0.5, color="gray", linestyle="--", linewidth=1)
ax.scatter([0, 0.5, 1], [0, 1, 0], color="#d62728", zorder=3)
ax.set_title("二分类熵与类别比例的关系")
ax.set_xlabel("正类比例 p")
ax.set_ylabel("Entropy")
ax.grid(True, alpha=0.3)
plt.show()"""
    ),
    md(
        "## 结论\n\n"
        "因此，(a) 是 **False**，(b) 是 **True**。熵越低，说明划分后的节点中某一类别越占主导，节点越纯；"
        "熵越高，说明不同类别混在一起的程度越高，节点越不纯。决策树在选择分裂变量时，通常会寻找能够最大幅度降低熵的划分，"
        "也就是最大化信息增益。"
    ),
]


answer2_cells = [
    md(
        "# Question B：使用 Funnelling Approach 进行特征选择\n\n"
        "本题使用沪深 300 指数数据构造机器学习特征，并通过 filter、wrapper 和 embedded 三类方法逐步收窄特征集合。"
    ),
    md(
        "## 方法概览\n\n"
        "本研究把特征选择设计成三层漏斗：\n\n"
        "1. **Filter 方法**：先在模型外部检查数据质量、删除高度相关特征，并用互信息衡量单个特征与目标变量的关联。\n"
        "2. **Wrapper 方法**：使用时间序列交叉验证，比较不同特征数量下的模型 ROC AUC，选择在训练集交叉验证中表现最稳的候选特征组。\n"
        "3. **Embedded 方法**：在候选特征组上训练 XGBoost，用 gain importance 排序，再用时间序列交叉验证决定最终保留多少个重要特征。\n\n"
        "这样做的目标不是寻找“单个最强特征”，而是在金融短期预测这种低信噪比任务中，保留一组弱但互补的预测信号。"
    ),
    code(
        r"""from pathlib import Path
import os
import sys

import pandas as pd

# 允许 notebook 从项目根目录或 Exam3 目录运行。
if Path.cwd().name != "Exam3" and (Path.cwd() / "Exam3").exists():
    os.chdir(Path.cwd() / "Exam3")
if str(Path.cwd()) not in sys.path:
    sys.path.insert(0, str(Path.cwd()))

from workflow_draft import (
    WorkflowConfig,
    build_features,
    train_test_split_time,
    feature_selection_funnel,
)

config = WorkflowConfig(data_path=Path("CSI300_2005_2026.csv"))
config"""
    ),
    md(
        "## 数据、标签与样本切分\n\n"
        "研究对象为沪深 300 指数。为避免未来信息泄露，所有特征均使用当日或过去窗口的数据计算；"
        "目标变量使用下一交易日收益率。\n\n"
        "标签定义为：若下一交易日对数收益率大于 **0.15%**，则记为 1，否则记为 0。"
        "这个阈值用于把极小的近零上涨归为非显著上涨，避免把市场噪声机械地视作有效上涨信号。\n\n"
        "样本从 2010 年开始，最后 20% 作为时间顺序上的测试集。第 2 题的特征选择只使用训练集完成。"
    ),
    code(
        r"""data, feature_cols = build_features(config)
X_train, X_test, y_train, y_test, train_frame, test_frame = train_test_split_time(
    data, feature_cols, config
)

summary = pd.DataFrame({
    "项目": [
        "完整样本起止", "训练集起止", "测试集起止",
        "完整样本数", "训练集样本数", "测试集样本数",
        "候选特征数", "训练集正类比例", "测试集正类比例", "标签阈值",
    ],
    "数值": [
        f"{data.index.min().date()} 至 {data.index.max().date()}",
        f"{train_frame.index.min().date()} 至 {train_frame.index.max().date()}",
        f"{test_frame.index.min().date()} 至 {test_frame.index.max().date()}",
        len(data), len(train_frame), len(test_frame), len(feature_cols),
        round(y_train.mean(), 4), round(y_test.mean(), 4), config.target_threshold,
    ],
})
summary"""
    ),
    md(
        "## 原始候选特征池\n\n"
        "原始特征池覆盖收益、趋势、波动率、成交量、K 线形态和技术指标。"
        "特征数量必须足够多，才能让后续漏斗式选择有意义；同时，所有滚动窗口都只使用历史数据。"
    ),
    code(
        r"""feature_groups = pd.DataFrame({
    "类别": ["收益与动量", "趋势/均线", "波动率与极值", "成交量", "K 线结构", "技术指标", "日历变量"],
    "示例特征": [
        "log_ret_1, ret_sum_2, ret_sum_3, ret_sum_10, ret_sum_120",
        "ma_ratio_3, ma_ratio_5, ma_ratio_20, ma_ratio_120",
        "volatility_20, rolling_min_ret_5, rolling_max_ret_60, atr_20",
        "volume_ret, volume_z_10, volume_z_20, volume_z_40",
        "range_pct, gap_ret, upper_shadow, lower_shadow, close_pos",
        "rsi_6, rsi_14, rsi_21, macd, macd_signal, macd_hist",
        "dow",
    ],
})
feature_groups"""
    ),
    md(
        "## 第一步：Filter 方法\n\n"
        "Filter 阶段不依赖最终模型。这里先删除训练集中两两相关系数绝对值大于 0.98 的冗余特征，"
        "再用 mutual information 对剩余特征排序。高度相关的特征通常携带重复信息，保留它们会增加模型复杂度，"
        "也会让特征重要性解释变得不稳定。互信息则可捕捉非线性关联，比简单线性相关更适合树模型前的粗筛。"
    ),
    code(
        r"""selection = feature_selection_funnel(X_train, y_train, config)

print(f"原始特征数: {len(feature_cols)}")
print(f"高相关删除数: {len(selection['corr_dropped'])}")
print(f"高相关删除后特征数: {len(selection['corr_features'])}")
print()
print("被删除的高相关特征:")
print(selection["corr_dropped"])"""
    ),
    code(
        r"""mi_top20 = selection["mi_scores"].head(20).rename("mutual_information").to_frame()
mi_top20"""
    ),
    md(
        "## 第二步：Wrapper 方法\n\n"
        "Wrapper 阶段把特征选择放回模型训练流程中。具体做法是：按互信息排名依次取前 N 个特征，"
        "并用 `TimeSeriesSplit` 计算 XGBoost 在训练集交叉验证中的 ROC AUC。\n\n"
        "这里使用时间序列交叉验证，而不是随机 K 折，是因为金融时间序列存在明显的时间顺序。"
        "随机打乱会让训练数据间接看到未来结构，产生过于乐观的结果。"
    ),
    code(
        r"""wrapper_table = selection["wrapper_table"].copy()
wrapper_table["cv_mean_auc"] = wrapper_table["cv_mean_auc"].round(4)
wrapper_table["cv_std_auc"] = wrapper_table["cv_std_auc"].round(4)
wrapper_table"""
    ),
    md(
        "从上表可以看到，训练集交叉验证并没有支持过度压缩特征数量；保留高相关筛选后的全部 64 个特征时，"
        "平均 ROC AUC 最高。这个结果符合短期市场方向预测的特点：单个特征信号很弱，多个弱信号组合后才可能形成较稳定的信息。"
    ),
    md(
        "## 第三步：Embedded 方法\n\n"
        "Embedded 阶段使用 XGBoost 的 gain importance。Gain 衡量某个特征被用于树分裂时带来的平均损失下降，"
        "更接近模型内部实际使用特征的方式。\n\n"
        "为避免只看一次模型的重要性排序而过拟合，最终仍然用时间序列交叉验证比较 top K 重要特征的表现。"
    ),
    code(
        r"""gain_top25 = selection["gain_scores"].head(25).rename("xgb_gain_importance").to_frame()
gain_top25"""
    ),
    code(
        r"""embedded_table = selection["embedded_table"].copy()
embedded_table["cv_mean_auc"] = embedded_table["cv_mean_auc"].round(4)
embedded_table["cv_std_auc"] = embedded_table["cv_std_auc"].round(4)
embedded_table"""
    ),
    md(
        "Embedded 阶段最终选择 top 40 个特征。该数量在训练集时间序列交叉验证中给出最高平均 ROC AUC，"
        "同时相比 64 个候选特征明显降低了维度。"
    ),
    code(
        r"""final_features = selection["final_features"]
final_feature_table = pd.DataFrame({
    "序号": range(1, len(final_features) + 1),
    "最终特征": final_features,
    "XGBoost gain": selection["gain_scores"].loc[final_features].round(6).values,
})
final_feature_table"""
    ),
    md(
        "## 特征选择结论\n\n"
        "最终保留的特征主要集中在短期均线偏离、近期极端收益、短期动量、成交量标准化、MACD/RSI、"
        "价格区间和跳空收益等维度。它们共同描述了市场在最近数日到数月内的趋势、反转、波动和成交状态。\n\n"
        "这组特征将作为第 3 题梯度提升分类模型的输入。"
    ),
]


# Reference-style overrides for Answer2 and Answer3. These cells keep the
# submitted notebooks close to the course workflow while still answering the
# feature-selection and CSI 300 requirements.
answer2_cells = [
    md(
        "# Question B：使用 Funnelling Approach 进行特征选择\n\n"
        "本题在沪深 300 指数数据上构造滚动收益和滚动波动率特征，并将 filter、wrapper 和 embedded 三类方法组合成漏斗式特征选择流程。"
    ),
    code(
        r"""# Data manipulation
import pandas as pd
import numpy as np

# Visualization
import matplotlib.pyplot as plt

# Classifier
from xgboost import XGBClassifier

# Feature selection and model validation
from sklearn.feature_selection import mutual_info_classif
from sklearn.model_selection import train_test_split, TimeSeriesSplit, cross_val_score
from sklearn.utils.class_weight import compute_sample_weight

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False"""
    ),
    md(
        "## 数据读取与候选特征构造\n\n"
        "候选特征与建模流程保持一致：先计算日度对数收益率，然后生成 10 到 60 日窗口的滚动累计收益 `Ret_*` 和滚动标准差 `Std_*`。"
        "这些特征分别刻画趋势/动量和波动状态。"
    ),
    code(
        r"""# Load file
df = pd.read_csv("CSI300_2005_2026.csv", index_col=0, parse_dates=True)

# Calculate returns
df["Returns"] = np.log(df["Adj Close"]).diff()
df = df["2010":].copy()

# Create features (predictors) list
features_list = []
for r in range(10, 65, 5):
    df["Ret_" + str(r)] = df.Returns.rolling(r).sum()
    df["Std_" + str(r)] = df.Returns.rolling(r).std()
    features_list.append("Ret_" + str(r))
    features_list.append("Std_" + str(r))

# Define target before dropping NaN values so the last row without a forward return is removed.
target_threshold = 0.0010
df["Target_Return"] = np.log(df["Adj Close"].shift(-1) / df["Adj Close"])
df["Label"] = np.where(df["Target_Return"] > target_threshold, 1, 0)

# Drop NaN values
df.dropna(inplace=True)

X = df[features_list]
y = df["Label"].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
sample_weights = compute_sample_weight(class_weight="balanced", y=y_train)

summary = pd.DataFrame({
    "Item": ["Candidate features", "Training observations", "Testing observations", "Training positive rate", "Testing positive rate"],
    "Value": [len(features_list), len(X_train), len(X_test), round(y_train.mean(), 4), round(y_test.mean(), 4)],
})
summary"""
    ),
    md(
        "## Step 1：Filter 方法\n\n"
        "Filter 阶段先删除高度相关的冗余特征，再用 mutual information 对剩余特征排序。"
        "相关性阈值设为 0.98，用于减少几乎重复的滚动波动率特征。"
    ),
    code(
        r"""# Correlation filter
corr = X_train.corr().abs()
upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
corr_dropped = [column for column in upper.columns if any(upper[column] > 0.98)]
corr_features = [column for column in X_train.columns if column not in corr_dropped]

# Mutual information filter
mi_scores = pd.Series(
    mutual_info_classif(X_train[corr_features], y_train, random_state=42),
    index=corr_features,
).sort_values(ascending=False)

filter_features = list(mi_scores.head(min(18, len(mi_scores))).index)

print(f"Initial feature count: {len(features_list)}")
print(f"Dropped by correlation filter: {corr_dropped}")
print(f"Features kept for wrapper step: {len(filter_features)}")
mi_scores.head(18).to_frame("mutual_information")"""
    ),
    md(
        "## Step 2：Wrapper 方法\n\n"
        "Wrapper 阶段使用 XGBoost 分类器和 `TimeSeriesSplit`。按互信息排序取前 N 个特征，比较不同 N 下的交叉验证 ROC AUC，"
        "并使用 `compute_sample_weight` 处理训练集类别不平衡。"
    ),
    code(
        r"""# Wrapper selection with time-series cross validation
tscv = TimeSeriesSplit(n_splits=5, gap=1)
wrapper_rows = []

for n_features in [8, 10, 12, 14, 16, 18]:
    cols = filter_features[: min(n_features, len(filter_features))]
    selector_model = XGBClassifier(
        verbosity=0,
        eval_metric="logloss",
        n_estimators=100,
        max_depth=3,
        learning_rate=0.05,
    )
    cv_scores = cross_val_score(
        selector_model,
        X_train[cols],
        y_train,
        cv=tscv,
        scoring="roc_auc",
        params={"sample_weight": sample_weights},
        n_jobs=1,
    )
    wrapper_rows.append({
        "n_features": len(cols),
        "cv_roc_auc_mean": cv_scores.mean(),
        "cv_roc_auc_std": cv_scores.std(),
        "features": cols,
    })

wrapper_table = pd.DataFrame(wrapper_rows).drop_duplicates("n_features")
best_wrapper = wrapper_table.sort_values(["cv_roc_auc_mean", "n_features"], ascending=[False, True]).iloc[0]
wrapper_features = list(best_wrapper["features"])

wrapper_table.drop(columns=["features"]).round(4)"""
    ),
    md(
        "## Step 3：Embedded 方法\n\n"
        "Embedded 阶段在 wrapper 选出的特征上训练 XGBoost，并使用模型内部的 gain importance 排序。"
        "最终保留 gain 排名前 10 的特征作为第 3 题模型输入。"
    ),
    code(
        r"""# Embedded selection by XGBoost gain importance
embedded_model = XGBClassifier(
    verbosity=0,
    eval_metric="logloss",
    n_estimators=100,
    max_depth=3,
    learning_rate=0.05,
    importance_type="gain",
)

embedded_model.fit(X_train[wrapper_features], y_train, sample_weight=sample_weights)

gain_scores = pd.Series(
    embedded_model.feature_importances_,
    index=wrapper_features,
).sort_values(ascending=False)

final_features = list(gain_scores.head(min(10, len(gain_scores))).index)

final_feature_table = pd.DataFrame({
    "Rank": range(1, len(final_features) + 1),
    "Feature": final_features,
    "XGBoost gain": gain_scores.loc[final_features].round(6).values,
})
final_feature_table"""
    ),
    md(
        "## 特征选择结论\n\n"
        "漏斗流程从 22 个候选滚动特征开始，先通过相关性和互信息进行 filter，再通过时间序列交叉验证完成 wrapper 筛选，"
        "最后通过 XGBoost gain importance 完成 embedded 筛选。最终特征将用于第 3 题的梯度提升模型。"
    ),
]


answer3_cells = [
    md(
        "# XGBoost：Predicting Positive Market Moves Using CSI 300\n\n"
        "本研究使用沪深 300 指数数据建立梯度提升分类模型，目标是预测下一交易日是否出现有效上涨。"
        "分析流程包括数据读取、探索性分析、清洗、特征工程、特征选择、模型训练、超参数调优、预测质量评估以及简单交易信号回测。"
    ),
    md("## Install Packages"),
    code(
        r"""# Install packages
# 检查分析所需依赖是否可导入。
import importlib.util
import pandas as pd

required_packages = ["numpy", "pandas", "matplotlib", "sklearn", "xgboost", "scipy"]
package_status = pd.DataFrame({
    "Package": required_packages,
    "Available": [importlib.util.find_spec(pkg) is not None for pkg in required_packages],
})
package_status"""
    ),
    md("## Import Libraries"),
    code(
        r"""# Data manipulation
from pathlib import Path
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import ConfusionMatrixDisplay, PrecisionRecallDisplay, RocCurveDisplay

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

# 设置工作目录以便读取数据与工具函数。
if Path.cwd().name != "Exam3" and (Path.cwd() / "Exam3").exists():
    os.chdir(Path.cwd() / "Exam3")
if str(Path.cwd()) not in sys.path:
    sys.path.insert(0, str(Path.cwd()))

from workflow_draft import (
    WorkflowConfig,
    build_features,
    train_test_split_time,
    feature_selection_funnel,
    regularized_xgb,
    evaluate_classifier,
    tune_xgb,
    backtest_signal,
)

DATA_PATH = Path("CSI300_2005_2026.csv")
config = WorkflowConfig(data_path=DATA_PATH)
config"""
    ),
    md(
        "## Section 1: Experiment Tracking\n\n"
        "本研究记录实验目标、样本切分、标签定义、交叉验证方案、模型参数、评估指标和回测结果。"
        "这些信息用于保证建模流程可复核，并方便比较基准模型与调参后模型的表现。"
    ),
    code(
        r"""# Experiment Tracker
experiment_setup = pd.DataFrame({
    "Item": [
        "Asset",
        "Data source",
        "Objective",
        "Target threshold",
        "Train/test split",
        "Cross validation",
        "Experiment tracking",
    ],
    "Value": [
        "CSI 300 Index",
        str(DATA_PATH),
        "Predict next-day effective uptrend with binomial classification",
        f"next-day log return > {config.target_threshold:.2%}",
        f"Chronological split, test size = {config.test_size:.0%}",
        f"TimeSeriesSplit(n_splits={config.cv_splits}, gap={config.cv_gap})",
        "Configuration table, cross-validation output, metrics and plots",
    ],
})
experiment_setup"""
    ),
    md(
        "## Section 2: The workflow\n\n"
        "We'll employ XGBoost classifier from `scikit-learn` for stock / equity index trend prediction.\n\n"
        "| Steps        | Workflow                  | Remarks                                                         |\n"
        "|:-------------|:--------------------------|:----------------------------------------------------------------|\n"
        "|Step 1        | Ideation                  | Define objective, success metrics     |\n"
        "|Step 2        | Data Collection           | Gather and integrate data\n"
        "|Step 3        | Exploratory Data Analysis (Initial) | Broad exploration: stats, distributions, correlations, missing data |\n"
        "|Step 4        | Data Cleaning           | Handle missing values, outliers, duplicates.            |\n"
        "|Step 5        | Feature Engineering & Transformation            | Feature creation, scaling, encoding, selection                         |\n"
        "|        | Subset Validation EDA            | Re-examine chosen features: check distributions, multicollinearity, relationships                      |               \n"
        "|Step 6        | Modeling                  | Select algorithm(s), train models, tune hyperparameters                           |\n"
        "|Step 7        | Evaluation                   | Validate using metrics and backtesting       |"
    ),
    md(
        "### (1) Load Data\n\n"
        "数据文件为 `CSI300_2005_2026.csv`。字段包括 Open、High、Low、Close、Adj Close 和 Volume。"
    ),
    code(
        r"""# Load file
raw_df = pd.read_csv(DATA_PATH, parse_dates=["Date"]).sort_values("Date").set_index("Date")

raw_summary = pd.DataFrame({
    "Item": ["Start date", "End date", "Rows", "Columns"],
    "Value": [raw_df.index.min().date(), raw_df.index.max().date(), len(raw_df), raw_df.shape[1]],
})
display(raw_df.head())
raw_summary"""
    ),
    md("### (2) EDA of Original dataset"),
    code(
        r"""# Descriptive statistics
raw_df.describe().T"""
    ),
    code(
        r"""fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
raw_df["Adj Close"].plot(ax=axes[0], color="#1f77b4", linewidth=1.4)
axes[0].set_title("沪深 300 调整收盘价")
axes[0].set_ylabel("Index level")
axes[0].grid(True, alpha=0.3)

raw_df["Volume"].plot(ax=axes[1], color="#7f7f7f", linewidth=1.0)
axes[1].set_title("成交量")
axes[1].set_ylabel("Volume")
axes[1].grid(True, alpha=0.3)
plt.tight_layout()
plt.show()"""
    ),
    md("### (3) Cleaning & Imputation"),
    code(
        r"""# Check for missing values, duplicates and invalid prices.
cleaning_checks = pd.DataFrame({
    "Check": [
        "Missing values",
        "Duplicate dates",
        "Non-positive Open/High/Low/Close/Adj Close",
        "Non-positive Volume",
    ],
    "Result": [
        int(raw_df.isna().sum().sum()),
        int(raw_df.index.duplicated().sum()),
        int((raw_df[["Open", "High", "Low", "Close", "Adj Close"]] <= 0).sum().sum()),
        int((raw_df["Volume"] <= 0).sum()),
    ],
})
cleaning_checks"""
    ),
    md(
        "### (4) Feature Engineering\n\n"
        "特征只使用当日或历史信息构造，避免未来信息泄露。候选特征覆盖收益、动量、均线偏离、波动率、成交量、"
        "K 线结构、RSI、MACD 和 ATR 等维度。"
    ),
    code(
        r"""# Create features and split the datasets into training and testing data.
data, feature_cols = build_features(config)
X_train, X_test, y_train, y_test, train_frame, test_frame = train_test_split_time(
    data, feature_cols, config
)

feature_summary = pd.DataFrame({
    "Item": [
        "Usable sample",
        "Training sample",
        "Testing sample",
        "Candidate feature count",
        "Training positive rate",
        "Testing positive rate",
    ],
    "Value": [
        f"{data.index.min().date()} to {data.index.max().date()}, n={len(data)}",
        f"{train_frame.index.min().date()} to {train_frame.index.max().date()}, n={len(train_frame)}",
        f"{test_frame.index.min().date()} to {test_frame.index.max().date()}, n={len(test_frame)}",
        len(feature_cols),
        round(y_train.mean(), 4),
        round(y_test.mean(), 4),
    ],
})
feature_summary"""
    ),
    md("#### (a) Feature Specification"),
    code(
        r"""# Feature specification
feature_groups = pd.DataFrame({
    "Category": ["Return/Momentum", "Trend", "Volatility", "Volume", "Candle shape", "Technical indicators", "Calendar"],
    "Examples": [
        "log_ret_1, ret_sum_2, ret_sum_3, ret_sum_10, ret_sum_120",
        "ma_ratio_3, ma_ratio_5, ma_ratio_20, ma_ratio_120",
        "volatility_20, rolling_min_ret_5, rolling_max_ret_60, atr_20",
        "volume_ret, volume_z_10, volume_z_20, volume_z_40",
        "range_pct, gap_ret, upper_shadow, lower_shadow, close_pos",
        "rsi_6, rsi_14, rsi_21, macd, macd_signal, macd_hist",
        "dow",
    ],
})
feature_groups"""
    ),
    code(
        r"""# Feature selection subset derived from Question B.
selection = feature_selection_funnel(X_train, y_train, config)
final_features = selection["final_features"]

final_feature_table = pd.DataFrame({
    "Rank": range(1, len(final_features) + 1),
    "Feature": final_features,
    "XGBoost gain": selection["gain_scores"].loc[final_features].round(6).values,
})
final_feature_table.head(20)"""
    ),
    md("#### (b) Target or Label Definition"),
    code(
        r"""# Define Target
target_summary = pd.DataFrame({
    "Dataset": ["Train", "Test"],
    "Observations": [len(y_train), len(y_test)],
    "Positive rate": [round(y_train.mean(), 4), round(y_test.mean(), 4)],
    "Negative rate": [round(1 - y_train.mean(), 4), round(1 - y_test.mean(), 4)],
})

print(f"Target definition: y=1 if next-day log return > {config.target_threshold:.2%}; otherwise y=0.")
target_summary"""
    ),
    md(
        "### (5) Boosting Ensemble\n\n"
        "本节先建立一个正则化的 XGBoost 基准模型。模型使用时间顺序切分，不打乱样本；类别权重通过训练集正负样本比例自动设置。"
    ),
    code(
        r"""# Scale and fit the classifier model
base_model = regularized_xgb(y_train, config)
base_eval = evaluate_classifier(
    base_model,
    X_train[final_features],
    y_train,
    X_test[final_features],
    y_test,
)

base_metrics = pd.DataFrame({
    "Metric": ["Train AUC", "Test AUC", "Accuracy", "Balanced Accuracy", "Decision threshold"],
    "Base XGBoost": [
        base_eval["train_auc"],
        base_eval["test_auc"],
        base_eval["accuracy"],
        base_eval["balanced_accuracy"],
        base_eval["threshold"],
    ],
})
base_metrics["Base XGBoost"] = base_metrics["Base XGBoost"].round(4)
base_metrics"""
    ),
    md("### (6) Hyperparameter Tuning"),
    md(
        "#### (a) XGBoost's hyper-parameter\n\n"
        "调优使用 `RandomizedSearchCV` 和 `TimeSeriesSplit`，目标函数为 ROC AUC。"
        "参数搜索在训练集上进行时间序列交叉验证，并将最优参数用于样本外测试集评估。"
    ),
    code(
        r"""# Cross-validation and randomized search
search = tune_xgb(X_train[final_features], y_train, config, n_iter=50)

best_params = pd.DataFrame({
    "Parameter": list(search.best_params_.keys()),
    "Best value": list(search.best_params_.values()),
})
print(f"Best cross-validated ROC AUC: {search.best_score_:.4f}")
best_params"""
    ),
    md("#### (b) Randomized search result"),
    code(
        r"""# Create tuned model using best parameters from local search.
tuned_eval = evaluate_classifier(
    search.best_estimator_,
    X_train[final_features],
    y_train,
    X_test[final_features],
    y_test,
)

metrics_comparison = pd.DataFrame({
    "Metric": ["Train AUC", "Test AUC", "Accuracy", "Balanced Accuracy", "Decision threshold"],
    "Base XGBoost": [
        base_eval["train_auc"],
        base_eval["test_auc"],
        base_eval["accuracy"],
        base_eval["balanced_accuracy"],
        base_eval["threshold"],
    ],
    "Tuned XGBoost": [
        tuned_eval["train_auc"],
        tuned_eval["test_auc"],
        tuned_eval["accuracy"],
        tuned_eval["balanced_accuracy"],
        tuned_eval["threshold"],
    ],
})
metrics_comparison[["Base XGBoost", "Tuned XGBoost"]] = metrics_comparison[["Base XGBoost", "Tuned XGBoost"]].round(4)
metrics_comparison"""
    ),
    md("### (7) Evaluation"),
    code(
        r"""# Return the evaluation results
print("Confusion matrix [[TN, FP], [FN, TP]]:")
print(tuned_eval["confusion_matrix"])
print()
print("Classification report:")
print(tuned_eval["classification_report"])"""
    ),
    code(
        r"""# Display ROC, precision-recall curve and confusion matrix.
fig, axes = plt.subplots(1, 3, figsize=(16, 4.5))

RocCurveDisplay.from_predictions(
    y_test,
    tuned_eval["test_proba"],
    ax=axes[0],
    name="Tuned XGBoost",
    color="#1f77b4",
)
axes[0].plot([0, 1], [0, 1], linestyle="--", color="gray", linewidth=1)
axes[0].set_title("ROC Curve")
axes[0].grid(True, alpha=0.3)

PrecisionRecallDisplay.from_predictions(
    y_test,
    tuned_eval["test_proba"],
    ax=axes[1],
    name="Tuned XGBoost",
    color="#ff7f0e",
)
axes[1].set_title("Precision-Recall Curve")
axes[1].grid(True, alpha=0.3)

ConfusionMatrixDisplay(
    confusion_matrix=tuned_eval["confusion_matrix"],
    display_labels=["0: Non-uptrend", "1: Uptrend"],
).plot(ax=axes[2], colorbar=False, cmap="Blues")
axes[2].set_title("Confusion Matrix")

plt.tight_layout()
plt.show()"""
    ),
    md("#### (a) Feature Importance"),
    code(
        r"""# Plot the feature importance of the tuned model.
booster = tuned_eval["model"].get_booster()
score = booster.get_score(importance_type="gain")
importance = (
    pd.Series(score, name="gain")
    .reindex(final_features)
    .fillna(0)
    .sort_values(ascending=False)
)

fig, ax = plt.subplots(figsize=(8, 7))
importance.head(20).sort_values().plot(kind="barh", ax=ax, color="#2ca02c")
ax.set_title("Top 20 Feature Importance by Gain")
ax.set_xlabel("Gain")
ax.grid(True, axis="x", alpha=0.3)
plt.tight_layout()
plt.show()

importance.head(20).round(4).to_frame()"""
    ),
    md("#### (b) Backtest Analysis"),
    code(
        r"""# Optional add-on: simple backtest of predicted signals.
backtest = backtest_signal(test_frame, tuned_eval["y_pred"])
backtest.round(4)"""
    ),
    code(
        r"""signal = pd.Series(tuned_eval["y_pred"], index=test_frame.index, name="signal")
strategy_returns = signal * test_frame["next_log_ret"]
buy_hold_returns = test_frame["next_log_ret"]

wealth = pd.DataFrame({
    "Strategy": np.exp(strategy_returns.cumsum()),
    "Buy & Hold": np.exp(buy_hold_returns.cumsum()),
})

fig, ax = plt.subplots(figsize=(9, 4.5))
wealth.plot(ax=ax, linewidth=2)
ax.set_title("Cumulative Wealth on Test Set")
ax.set_ylabel("Cumulative wealth")
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()"""
    ),
    md(
        "## Conclusion\n\n"
        "调参后的 XGBoost 在测试集上的 ROC AUC 约为 0.57，说明模型具有一定但较弱的方向排序能力。"
        "Accuracy 和 balanced accuracy 也仅略高于随机水平，这与短期指数收益接近有效市场、噪声较高的事实一致。\n\n"
        "从经济意义看，简单信号策略在测试期内优于买入持有，并且最大回撤更小。不过该结果仍需谨慎解读："
        "正式交易前应加入交易成本、滑点、参数稳定性检验和滚动样本外测试。总体而言，模型不是一个强预测器，"
        "但在受限的监督学习框架下，它展示了比随机分类更好的样本外排序能力和一定的风险控制价值。"
    ),
]


answer3_cells = [
    md(
        "# XGBoost：Predicting Positive Market Moves Using CSI 300\n\n"
        "本研究使用沪深 300 指数数据建立 XGBoost 二分类模型，目标是预测下一交易日是否出现有效上涨。"
        "整体实现遵循标准机器学习 workflow：数据读取、EDA、清洗、特征工程、模型训练、调参、评估与回测。"
    ),
    md("## Install Packages"),
    code(
        r"""# Install packages
# 检查分析所需依赖是否可导入。
import importlib.util
import pandas as pd

required_packages = ["numpy", "pandas", "matplotlib", "sklearn", "xgboost", "scipy"]
package_status = pd.DataFrame({
    "Package": required_packages,
    "Available": [importlib.util.find_spec(pkg) is not None for pkg in required_packages],
})
package_status"""
    ),
    md("## Import Libraries"),
    code(
        r"""# Data manipulation
from pathlib import Path
import os
import sys

import pandas as pd
import numpy as np

# Visualization
import matplotlib.pyplot as plt

# Classifier
from xgboost import XGBClassifier, plot_importance

# Preprocessing and validation
from sklearn.feature_selection import mutual_info_classif
from sklearn.model_selection import (
    train_test_split,
    TimeSeriesSplit,
    cross_val_score,
    RandomizedSearchCV,
)
from sklearn.utils.class_weight import compute_sample_weight

# Metrics
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    RocCurveDisplay,
    ConfusionMatrixDisplay,
    PrecisionRecallDisplay,
    classification_report,
    roc_auc_score,
    f1_score,
    precision_score,
    recall_score,
)

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

# 设置工作目录以便读取数据。
if Path.cwd().name != "Exam3" and (Path.cwd() / "Exam3").exists():
    os.chdir(Path.cwd() / "Exam3")

DATA_PATH = Path("CSI300_2005_2026.csv")"""
    ),
    md(
        "## Section 1: Experiment Tracking\n\n"
        "实验记录包括资产、样本区间、目标变量定义、训练/测试切分、交叉验证方法、调参范围与最终评估指标。"
    ),
    code(
        r"""# Experiment Tracker
experiment_config = {
    "asset": "CSI 300 Index",
    "data": str(DATA_PATH),
    "target": "next-day effective uptrend",
    "target_threshold": 0.0010,
    "test_size": 0.2,
    "random_state": 42,
}

pd.DataFrame(experiment_config.items(), columns=["Item", "Value"])"""
    ),
    md(
        "## Section 2: The workflow\n\n"
        "We'll employ XGBoost classifier from `scikit-learn` for stock / equity index trend prediction.\n\n"
        "| Steps        | Workflow                  | Remarks                                                         |\n"
        "|:-------------|:--------------------------|:----------------------------------------------------------------|\n"
        "|Step 1        | Ideation                  | Define objective, success metrics     |\n"
        "|Step 2        | Data Collection           | Gather and integrate data\n"
        "|Step 3        | Exploratory Data Analysis (Initial) | Broad exploration: stats, distributions, correlations, missing data |\n"
        "|Step 4        | Data Cleaning           | Handle missing values, outliers, duplicates.            |\n"
        "|Step 5        | Feature Engineering & Transformation            | Feature creation, scaling, encoding, selection                         |\n"
        "|        | Subset Validation EDA            | Re-examine chosen features: check distributions, multicollinearity, relationships                      |               \n"
        "|Step 6        | Modeling                  | Select algorithm(s), train models, tune hyperparameters                           |\n"
        "|Step 7        | Evaluation                   | Validate using metrics and backtesting       |"
    ),
    md("### (1) Load Data"),
    code(
        r"""# Load file
df = pd.read_csv(DATA_PATH, index_col=0, parse_dates=True)

# Calculate returns
df["Returns"] = np.log(df["Adj Close"]).diff()
df = df["2010":].copy()

# Verify the output
df"""
    ),
    md("### (2) EDA of Original dataset"),
    code(
        r"""# Descriptive statistics
df.describe().T"""
    ),
    code(
        r"""fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
df["Adj Close"].plot(ax=axes[0], color="#1f77b4", linewidth=1.4)
axes[0].set_title("CSI 300 Adjusted Close")
axes[0].set_ylabel("Index level")
axes[0].grid(True, alpha=0.3)

df["Returns"].plot(ax=axes[1], color="#7f7f7f", linewidth=1.0)
axes[1].set_title("Daily Log Returns")
axes[1].set_ylabel("Return")
axes[1].grid(True, alpha=0.3)
plt.tight_layout()
plt.show()"""
    ),
    md("### (3) Cleaning & Imputation"),
    code(
        r"""# Check for missing values
df.isnull().sum()"""
    ),
    md("### (4) Feature Engineering"),
    code(
        r"""# Create features (predictors) list
features_list = []
for r in range(10, 65, 5):
    df["Ret_" + str(r)] = df.Returns.rolling(r).sum()
    df["Std_" + str(r)] = df.Returns.rolling(r).std()
    features_list.append("Ret_" + str(r))
    features_list.append("Std_" + str(r))

# Define the forward return and label before dropping NaN values.
target_threshold = experiment_config["target_threshold"]
df["Target_Return"] = np.log(df["Adj Close"].shift(-1) / df["Adj Close"])
df["Label"] = np.where(df["Target_Return"] > target_threshold, 1, 0)

# Drop NaN values
df.dropna(inplace=True)

print(f"Candidate feature count: {len(features_list)}")
print(f"Usable observations: {len(df)}")"""
    ),
    md("#### (a) Feature Specification"),
    code(
        r"""# Convert to NumPy
X_all = df[features_list]
X_all.head(2)"""
    ),
    code(
        r"""# Feature subset derived by the funnelling approach.
y_for_selection = df["Label"].values
X_train_all, X_test_all, y_train, y_test = train_test_split(
    X_all, y_for_selection, test_size=0.2, shuffle=False
)
sample_weights = compute_sample_weight(class_weight="balanced", y=y_train)

# Filter: remove highly correlated features and rank by mutual information.
corr = X_train_all.corr().abs()
upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
corr_dropped = [column for column in upper.columns if any(upper[column] > 0.98)]
corr_features = [column for column in X_train_all.columns if column not in corr_dropped]

mi_scores = pd.Series(
    mutual_info_classif(X_train_all[corr_features], y_train, random_state=42),
    index=corr_features,
).sort_values(ascending=False)
filter_features = list(mi_scores.head(min(18, len(mi_scores))).index)

# Wrapper: choose feature count by time-series CV with XGBoost.
tscv = TimeSeriesSplit(n_splits=5, gap=1)
wrapper_rows = []
for n_features in [8, 10, 12, 14, 16, 18]:
    cols = filter_features[: min(n_features, len(filter_features))]
    selector_model = XGBClassifier(
        verbosity=0,
        eval_metric="logloss",
        n_estimators=100,
        max_depth=3,
        learning_rate=0.05,
    )
    cv_scores = cross_val_score(
        selector_model,
        X_train_all[cols],
        y_train,
        cv=tscv,
        scoring="roc_auc",
        params={"sample_weight": sample_weights},
        n_jobs=1,
    )
    wrapper_rows.append({
        "n_features": len(cols),
        "cv_roc_auc_mean": cv_scores.mean(),
        "cv_roc_auc_std": cv_scores.std(),
        "features": cols,
    })

wrapper_table = pd.DataFrame(wrapper_rows).drop_duplicates("n_features")
best_wrapper = wrapper_table.sort_values(["cv_roc_auc_mean", "n_features"], ascending=[False, True]).iloc[0]
wrapper_features = list(best_wrapper["features"])

# Embedded: rank selected features using XGBoost gain importance.
embedded_model = XGBClassifier(
    verbosity=0,
    eval_metric="logloss",
    n_estimators=100,
    max_depth=3,
    learning_rate=0.05,
    importance_type="gain",
)
embedded_model.fit(X_train_all[wrapper_features], y_train, sample_weight=sample_weights)
gain_scores = pd.Series(embedded_model.feature_importances_, index=wrapper_features).sort_values(ascending=False)

final_features = list(gain_scores.head(min(10, len(gain_scores))).index)
X = df[final_features]

pd.DataFrame({
    "Rank": range(1, len(final_features) + 1),
    "Feature": final_features,
    "Gain": gain_scores.loc[final_features].round(6).values,
})"""
    ),
    md("#### (b) Target or Label Definition"),
    code(
        r"""# Define Target
y = df["Label"].values
y"""
    ),
    code(
        r"""# label count
class_labels = np.bincount(y)
class_labels"""
    ),
    md("### (5) Boosting Ensemble"),
    code(
        r"""# Splitting the datasets into training and testing data.
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

# Output the train and test data size
print(f"Train and Test Size {len(X_train)}, {len(X_test)}")"""
    ),
    code(
        r"""# Scale and fit the classifier model

# For binary or multiclass classification
sample_weights = compute_sample_weight(class_weight="balanced", y=y_train)

base_model = XGBClassifier(
    verbosity=0,
    eval_metric="logloss",
)

base_model.fit(
    X_train,
    y_train,
    sample_weight=sample_weights,
)"""
    ),
    code(
        r"""# Predicting the test dataset
y_pred = base_model.predict(X_test)

# Predict Probabilities
y_proba = base_model.predict_proba(X_test)"""
    ),
    code(
        r"""# Accuracy Scores
acc_train = accuracy_score(y_train, base_model.predict(X_train))
acc_test = accuracy_score(y_test, y_pred)

print(f"Train Accuracy: {acc_train:0.4}, Test Accuracy: {acc_test:0.4}")"""
    ),
    code(
        r"""# Balanced Accuracy Scores
bal_acc_train = balanced_accuracy_score(y_train, base_model.predict(X_train))
bal_acc_test = balanced_accuracy_score(y_test, y_pred)

print(f"Train Balanced Accuracy: {bal_acc_train:0.4}, Test Balanced Accuracy: {bal_acc_test:0.4}")"""
    ),
    code(
        r"""# Display confussion matrix
disp_cm = ConfusionMatrixDisplay.from_estimator(
    base_model,
    X_test,
    y_test,
    display_labels=base_model.classes_,
    cmap=plt.cm.Blues,
)
disp_cm.ax_.set_title("Confusion matrix")
plt.show()"""
    ),
    code(
        r"""# Classification Report
print(classification_report(y_test, y_pred))"""
    ),
    code(
        r"""# Display ROCCurve
disp_roc = RocCurveDisplay.from_estimator(
    base_model,
    X_test,
    y_test,
    name="XGBoost",
)

disp_roc.ax_.set_title("ROC Curve")
plt.plot([0, 1], [0, 1], linestyle="--")
plt.show()"""
    ),
    code(
        r"""# Display PR Curve
disp_pr = PrecisionRecallDisplay.from_estimator(
    base_model,
    X_test,
    y_test,
    name="XGBoost",
)

disp_pr.ax_.set_title("Precision-Recall Curve")
plt.show()"""
    ),
    md("### (6) Hyperparameter Tuning"),
    md("#### (a) XGBoost's hyper-parameter"),
    code(
        r"""# Timeseries Cross Validation 2-split Demonstration
tscv_demo = TimeSeriesSplit(n_splits=2, gap=1)
for train, test in tscv_demo.split(X):
    print(f"Train: {train}, Test: {test}")"""
    ),
    code(
        r"""# Cross-validation
tscv = TimeSeriesSplit(n_splits=5, gap=1)"""
    ),
    code(
        r"""# Get params list
base_model.get_params()"""
    ),
    md("#### (b) Randomized Search"),
    code(
        r"""# Randomized search configuration
param_grid = {
    "learning_rate": [0.01, 0.03, 0.05, 0.08, 0.10],
    "max_depth": [1, 2, 3],
    "min_child_weight": [3, 5, 8, 12, 16],
    "gamma": [0.0, 0.5, 1.0, 2.0, 4.0],
    "colsample_bytree": [0.6, 0.75, 0.9, 1.0],
    "subsample": [0.6, 0.75, 0.9, 1.0],
    "n_estimators": [80, 120, 200, 300],
    "reg_alpha": [0, 0.1, 0.5, 1.0],
    "reg_lambda": [1, 3, 5, 10],
}

search = RandomizedSearchCV(
    estimator=XGBClassifier(verbosity=0, eval_metric="logloss"),
    param_distributions=param_grid,
    n_iter=50,
    scoring="roc_auc",
    cv=tscv,
    random_state=42,
    n_jobs=1,
)

search.fit(X_train, y_train, sample_weight=sample_weights)
best_params = search.best_params_

print("Best parameters found by randomized search:")
for k, v in best_params.items():
    print(f"  {k}: {v}")
print(f"Best cv/roc_auc_mean: {search.best_score_:.4f}")"""
    ),
    code(
        r"""# Create tuned model using best parameters
tuned_model = XGBClassifier(
    **best_params,
    verbosity=0,
    eval_metric="logloss",
)

# Fit with evaluation tracking
tuned_model.fit(
    X_train,
    y_train,
    sample_weight=sample_weights,
    eval_set=[(X_train, y_train), (X_test, y_test)],
    verbose=False,
)

print("Tuned model training completed successfully!")"""
    ),
    code(
        r"""# Return the evaluation results
evals_result = tuned_model.evals_result()
pd.DataFrame({
    "train_logloss": evals_result["validation_0"]["logloss"],
    "test_logloss": evals_result["validation_1"]["logloss"],
}).tail()"""
    ),
    code(
        r"""# Cross validation score with tuned model
cv_scores = cross_val_score(
    tuned_model,
    X_train,
    y_train,
    cv=tscv,
    scoring="f1",
    params={"sample_weight": sample_weights},
    n_jobs=1,
)
print(f"Mean CV Score: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")"""
    ),
    code(
        r"""# Predicting the test dataset
y_pred = tuned_model.predict(X_test)
y_proba = tuned_model.predict_proba(X_test)

# Measure Accuracy
acc_train = accuracy_score(y_train, tuned_model.predict(X_train))
acc_test = accuracy_score(y_test, y_pred)

print(f"\n Training Accuracy \t: {acc_train :0.4} \n Test Accuracy \t\t: {acc_test :0.4}")"""
    ),
    code(
        r"""bal_acc_train = balanced_accuracy_score(y_train, tuned_model.predict(X_train))
bal_acc_test = balanced_accuracy_score(y_test, y_pred)

print(f"Train Balanced Accuracy: {bal_acc_train:0.4}, Test Balanced Accuracy: {bal_acc_test:0.4}")
print(f"Test ROC AUC: {roc_auc_score(y_test, y_proba[:, 1]):0.4}")
print(f"Test F1: {f1_score(y_test, y_pred):0.4}")
print(f"Test Precision: {precision_score(y_test, y_pred):0.4}")
print(f"Test Recall: {recall_score(y_test, y_pred):0.4}")"""
    ),
    code(
        r"""# Tuned Model: Evaluation

# Confusion Matrix
disp = ConfusionMatrixDisplay.from_estimator(
    tuned_model,
    X_test,
    y_test,
    display_labels=tuned_model.classes_,
    cmap=plt.cm.Blues,
)
disp.ax_.set_title("Confusion matrix")
plt.show()

# Classification Report
print(classification_report(y_test, y_pred))

# ROC Curve
disp_roc = RocCurveDisplay.from_estimator(
    tuned_model,
    X_test,
    y_test,
    name="Tuned XGBoost",
)
disp_roc.ax_.set_title("ROC Curve")
plt.plot([0, 1], [0, 1], linestyle="--")
plt.show()

# PR Curve
disp_pr = PrecisionRecallDisplay.from_estimator(
    tuned_model,
    X_test,
    y_test,
    name="Tuned XGBoost",
)
disp_pr.ax_.set_title("Precision-Recall Curve")
plt.show()"""
    ),
    md("### (7) Evaluation"),
    md("#### (a) Feature Importance"),
    code(
        r"""# Plot the feature importance of the tuned model
plot_importance(tuned_model, importance_type="weight", title="Tuned Model Feature Importance", show_values=False)
plt.tight_layout()
plt.grid(True, alpha=0.3)
plt.show()"""
    ),
    code(
        r"""# The Gain is the most relevant attribute to interpret the relative importance of each feature.
gain_importance = tuned_model.get_booster().get_score(importance_type="gain")
pd.Series(gain_importance).sort_values(ascending=False).to_frame("gain")"""
    ),
    code(
        r"""# Feature importance by gain
plot_importance(tuned_model, importance_type="gain", show_values=False)
plt.tight_layout()
plt.grid(True, alpha=0.3)
plt.show()"""
    ),
    md("#### (b) Backtest Analysis"),
    code(
        r"""# Optional add-on: simple backtest of predicted signals.
test_index = X_test.index
signal = pd.Series(y_pred, index=test_index, name="signal")
strategy_returns = signal * df.loc[test_index, "Target_Return"]
buy_hold_returns = df.loc[test_index, "Target_Return"]

def performance(log_returns, exposure):
    wealth = np.exp(log_returns.cumsum())
    annual_return = wealth.iloc[-1] ** (252 / len(log_returns)) - 1
    annual_volatility = log_returns.std() * np.sqrt(252)
    sharpe = annual_return / annual_volatility if annual_volatility > 0 else np.nan
    drawdown = wealth / wealth.cummax() - 1
    return pd.Series({
        "total_return": wealth.iloc[-1] - 1,
        "annual_return": annual_return,
        "annual_volatility": annual_volatility,
        "sharpe": sharpe,
        "max_drawdown": drawdown.min(),
        "exposure": exposure,
    })

backtest = pd.DataFrame({
    "strategy": performance(strategy_returns, signal.mean()),
    "buy_hold": performance(buy_hold_returns, 1.0),
})
backtest.round(4)"""
    ),
    code(
        r"""wealth = pd.DataFrame({
    "Strategy": np.exp(strategy_returns.cumsum()),
    "Buy & Hold": np.exp(buy_hold_returns.cumsum()),
})

fig, ax = plt.subplots(figsize=(9, 4.5))
wealth.plot(ax=ax, linewidth=2)
ax.set_title("Cumulative Wealth on Test Set")
ax.set_ylabel("Cumulative wealth")
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()"""
    ),
    md(
        "## Conclusion\n\n"
        "模型在测试集上的 ROC AUC 高于 0.5，说明 XGBoost 对下一交易日有效上涨具有一定排序能力，但预测能力仍然较弱。"
        "这与短期指数收益噪声高、方向预测困难的经验相符。简单信号回测用于检验预测结果的经济含义，但未考虑交易成本和滑点，"
        "因此只能作为附加参考。"
    ),
]


# Final optimized Answer2/Answer3 definitions. The report structure follows the
# course workflow, while the feature set and model search space are adapted to
# the CSI 300 dataset.
answer2_cells = [
    md(
        "# Question B：使用 Funnelling Approach 进行特征选择\n\n"
        "本题使用沪深 300 指数数据构造较丰富的候选特征池，并通过 filter、wrapper 和 embedded 三类方法逐步筛选特征。"
        "候选特征覆盖收益、波动率、趋势、成交量、K 线结构和常用技术指标。"
    ),
    code(
        r"""import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import loguniform, randint, uniform
from xgboost import XGBClassifier
from sklearn.feature_selection import mutual_info_classif
from sklearn.model_selection import train_test_split, TimeSeriesSplit, cross_val_score
from sklearn.utils.class_weight import compute_sample_weight

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False"""
    ),
    md("## 候选特征构造"),
    code(
        r"""# Load file
df = pd.read_csv("CSI300_2005_2026.csv", parse_dates=["Date"]).sort_values("Date").set_index("Date")
df = df["2010":].copy()

# Core returns and price/volume structure
df["log_ret_1"] = np.log(df["Adj Close"]).diff()
df["simple_ret_1"] = df["Adj Close"].pct_change()
df["intraday_ret"] = df["Close"] / df["Open"] - 1
df["range_pct"] = df["High"] / df["Low"] - 1
df["gap_ret"] = df["Open"] / df["Close"].shift(1) - 1
df["upper_shadow"] = (df["High"] - df[["Open", "Close"]].max(axis=1)) / df["Close"]
df["lower_shadow"] = (df[["Open", "Close"]].min(axis=1) - df["Low"]) / df["Close"]
df["body_pct"] = (df["Close"] - df["Open"]) / df["Open"]
df["close_pos"] = (df["Close"] - df["Low"]) / (df["High"] - df["Low"]).replace(0, np.nan)
df["volume_ret"] = np.log(df["Volume"]).diff()
df["dow"] = df.index.dayofweek

# Rolling return, volatility, trend and volume features
for window in [2, 3, 5, 10, 20, 40, 60, 120]:
    df[f"ret_sum_{window}"] = df["log_ret_1"].rolling(window).sum()
    df[f"ret_mean_{window}"] = df["log_ret_1"].rolling(window).mean()
    df[f"volatility_{window}"] = df["log_ret_1"].rolling(window).std()
    df[f"ma_ratio_{window}"] = df["Adj Close"] / df["Adj Close"].rolling(window).mean() - 1
    df[f"volume_z_{window}"] = (
        df["Volume"] - df["Volume"].rolling(window).mean()
    ) / df["Volume"].rolling(window).std()
    df[f"rolling_min_ret_{window}"] = df["log_ret_1"].rolling(window).min()
    df[f"rolling_max_ret_{window}"] = df["log_ret_1"].rolling(window).max()

# RSI indicators
for window in [6, 14, 21]:
    delta = df["Adj Close"].diff()
    gain = delta.clip(lower=0).rolling(window).mean()
    loss = (-delta.clip(upper=0)).rolling(window).mean()
    rs = gain / loss.replace(0, np.nan)
    df[f"rsi_{window}"] = 100 - (100 / (1 + rs))

# MACD indicators
ema12 = df["Adj Close"].ewm(span=12, adjust=False).mean()
ema26 = df["Adj Close"].ewm(span=26, adjust=False).mean()
df["macd"] = ema12 - ema26
df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
df["macd_hist"] = df["macd"] - df["macd_signal"]

# ATR indicators
true_range = pd.concat(
    [
        df["High"] - df["Low"],
        (df["High"] - df["Close"].shift(1)).abs(),
        (df["Low"] - df["Close"].shift(1)).abs(),
    ],
    axis=1,
).max(axis=1)
for window in [14, 20]:
    df[f"atr_{window}"] = true_range.rolling(window).mean() / df["Adj Close"]

# Target: effective next-day uptrend
target_threshold = 0.0015
df["next_log_ret"] = df["log_ret_1"].shift(-1)
df["Label"] = np.where(df["next_log_ret"] > target_threshold, 1, 0)
df.loc[df["next_log_ret"].isna(), "Label"] = np.nan

excluded = ["Open", "High", "Low", "Close", "Adj Close", "Volume", "next_log_ret", "Label"]
features_list = [col for col in df.columns if col not in excluded]

data = df[features_list + ["Label", "next_log_ret"]].replace([np.inf, -np.inf], np.nan).dropna()
X = data[features_list]
y = data["Label"].astype(int).values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
sample_weights = compute_sample_weight(class_weight="balanced", y=y_train)

pd.DataFrame({
    "Item": ["Usable observations", "Training observations", "Testing observations", "Candidate features", "Training positive rate", "Testing positive rate"],
    "Value": [len(data), len(X_train), len(X_test), len(features_list), round(y_train.mean(), 4), round(y_test.mean(), 4)],
})"""
    ),
    md(
        "## Step 1：Filter 方法\n\n"
        "Filter 阶段先删除训练集中相关系数绝对值高于 0.98 的冗余变量，然后用 mutual information 对剩余变量排序。"
    ),
    code(
        r"""corr = X_train.corr().abs()
upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
corr_dropped = [column for column in upper.columns if any(upper[column] > 0.98)]
corr_features = [column for column in X_train.columns if column not in corr_dropped]

mi_scores = pd.Series(
    mutual_info_classif(X_train[corr_features], y_train, random_state=42),
    index=corr_features,
).sort_values(ascending=False)

filter_features = list(mi_scores.head(min(64, len(mi_scores))).index)

print(f"Initial feature count: {len(features_list)}")
print(f"Dropped by correlation filter: {len(corr_dropped)}")
print(f"Features kept after filter step: {len(filter_features)}")
mi_scores.head(20).to_frame("mutual_information")"""
    ),
    md(
        "## Step 2：Wrapper 方法\n\n"
        "Wrapper 阶段使用 XGBoost 和 `TimeSeriesSplit`，比较不同特征数量下的交叉验证 ROC AUC。"
        "由于标签存在轻微不平衡，训练中使用 `compute_sample_weight` 生成的样本权重。"
    ),
    code(
        r"""tscv = TimeSeriesSplit(n_splits=5, gap=1)
base_selector_params = {
    "verbosity": 0,
    "eval_metric": "logloss",
    "tree_method": "hist",
    "random_state": 42,
    "n_jobs": -1,
    "n_estimators": 120,
    "max_depth": 2,
    "learning_rate": 0.035,
    "subsample": 0.75,
    "colsample_bytree": 0.75,
    "min_child_weight": 5,
    "gamma": 1.0,
    "reg_alpha": 0.5,
    "reg_lambda": 3.0,
}

wrapper_rows = []
for n_features in [10, 15, 20, 25, 30, 35, 40, 50, len(filter_features)]:
    cols = filter_features[: min(n_features, len(filter_features))]
    selector_model = XGBClassifier(**base_selector_params)
    cv_scores = cross_val_score(
        selector_model,
        X_train[cols],
        y_train,
        cv=tscv,
        scoring="roc_auc",
        params={"sample_weight": sample_weights},
        n_jobs=1,
    )
    wrapper_rows.append({
        "n_features": len(cols),
        "cv_roc_auc_mean": cv_scores.mean(),
        "cv_roc_auc_std": cv_scores.std(),
        "features": cols,
    })

wrapper_table = pd.DataFrame(wrapper_rows).drop_duplicates("n_features")
best_wrapper = wrapper_table.sort_values(["cv_roc_auc_mean", "n_features"], ascending=[False, True]).iloc[0]
wrapper_features = list(best_wrapper["features"])

wrapper_table.drop(columns=["features"]).round(4)"""
    ),
    md(
        "## Step 3：Embedded 方法\n\n"
        "Embedded 阶段在 wrapper 选出的特征上训练 XGBoost，并使用 gain importance 排序；随后再次用时间序列交叉验证决定最终保留数量。"
    ),
    code(
        r"""embedded_model = XGBClassifier(**base_selector_params, importance_type="gain")
embedded_model.fit(X_train[wrapper_features], y_train, sample_weight=sample_weights)

gain_scores = pd.Series(
    embedded_model.feature_importances_,
    index=wrapper_features,
).sort_values(ascending=False)

embedded_rows = []
for n_features in [10, 15, 20, 25, 30, 35, 40, len(gain_scores)]:
    cols = list(gain_scores.head(min(n_features, len(gain_scores))).index)
    selector_model = XGBClassifier(**base_selector_params)
    cv_scores = cross_val_score(
        selector_model,
        X_train[cols],
        y_train,
        cv=tscv,
        scoring="roc_auc",
        params={"sample_weight": sample_weights},
        n_jobs=1,
    )
    embedded_rows.append({
        "n_features": len(cols),
        "cv_roc_auc_mean": cv_scores.mean(),
        "cv_roc_auc_std": cv_scores.std(),
        "features": cols,
    })

embedded_table = pd.DataFrame(embedded_rows).drop_duplicates("n_features")
best_embedded = embedded_table.sort_values(["cv_roc_auc_mean", "n_features"], ascending=[False, True]).iloc[0]
final_features = list(best_embedded["features"])

display(embedded_table.drop(columns=["features"]).round(4))

pd.DataFrame({
    "Rank": range(1, len(final_features) + 1),
    "Feature": final_features,
    "Gain": gain_scores.loc[final_features].round(6).values,
})"""
    ),
    md(
        "## 特征选择结论\n\n"
        "最终特征由三层漏斗共同决定：相关性和互信息完成初筛，时间序列交叉验证完成 wrapper 选择，"
        "XGBoost gain importance 和再次交叉验证完成 embedded 选择。该特征子集将用于第 3 题的模型训练与调参。"
    ),
]


answer3_cells = [
    md(
        "# XGBoost：Predicting Positive Market Moves Using CSI 300\n\n"
        "本研究使用沪深 300 指数数据建立 XGBoost 二分类模型，目标是预测下一交易日是否出现有效上涨。"
        "章节结构遵循标准机器学习 workflow，特征集和模型参数根据沪深 300 数据进行设计与调优。"
    ),
    md("## Install Packages"),
    code(
        r"""# Install packages
import importlib.util
import pandas as pd

required_packages = ["numpy", "pandas", "matplotlib", "sklearn", "xgboost", "scipy"]
package_status = pd.DataFrame({
    "Package": required_packages,
    "Available": [importlib.util.find_spec(pkg) is not None for pkg in required_packages],
})
package_status"""
    ),
    md("## Import Libraries"),
    code(
        r"""# Data manipulation
from pathlib import Path
import os
import warnings

warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np

# Visualization
import matplotlib.pyplot as plt

# Classifier
from xgboost import XGBClassifier, plot_importance

# Preprocessing and validation
from scipy.stats import loguniform, randint, uniform
from sklearn.feature_selection import mutual_info_classif
from sklearn.model_selection import (
    train_test_split,
    TimeSeriesSplit,
    cross_val_score,
    RandomizedSearchCV,
)
from sklearn.utils.class_weight import compute_sample_weight

# Metrics
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    RocCurveDisplay,
    ConfusionMatrixDisplay,
    PrecisionRecallDisplay,
    classification_report,
    roc_auc_score,
    f1_score,
    precision_score,
    recall_score,
)

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

if Path.cwd().name != "Exam3" and (Path.cwd() / "Exam3").exists():
    os.chdir(Path.cwd() / "Exam3")

DATA_PATH = Path("CSI300_2005_2026.csv")"""
    ),
    md(
        "## Section 1: Experiment Tracking\n\n"
        "实验记录包括资产、样本区间、目标变量定义、训练/测试切分、交叉验证方法、调参范围与最终评估指标。"
    ),
    code(
        r"""# Experiment Tracker
experiment_config = {
    "asset": "CSI 300 Index",
    "data": str(DATA_PATH),
    "target": "next-day effective uptrend",
    "target_threshold": 0.0015,
    "test_size": 0.2,
    "random_state": 42,
}

pd.DataFrame(experiment_config.items(), columns=["Item", "Value"])"""
    ),
    md(
        "## Section 2: The workflow\n\n"
        "We'll employ XGBoost classifier from `scikit-learn` for stock / equity index trend prediction.\n\n"
        "| Steps        | Workflow                  | Remarks                                                         |\n"
        "|:-------------|:--------------------------|:----------------------------------------------------------------|\n"
        "|Step 1        | Ideation                  | Define objective, success metrics     |\n"
        "|Step 2        | Data Collection           | Gather and integrate data\n"
        "|Step 3        | Exploratory Data Analysis (Initial) | Broad exploration: stats, distributions, correlations, missing data |\n"
        "|Step 4        | Data Cleaning           | Handle missing values, outliers, duplicates.            |\n"
        "|Step 5        | Feature Engineering & Transformation            | Feature creation, scaling, encoding, selection                         |\n"
        "|        | Subset Validation EDA            | Re-examine chosen features: check distributions, multicollinearity, relationships                      |               \n"
        "|Step 6        | Modeling                  | Select algorithm(s), train models, tune hyperparameters                           |\n"
        "|Step 7        | Evaluation                   | Validate using metrics and backtesting       |"
    ),
    md("### (1) Load Data"),
    code(
        r"""# Load file
df = pd.read_csv(DATA_PATH, parse_dates=["Date"]).sort_values("Date").set_index("Date")
df = df["2010":].copy()

# Calculate returns
df["log_ret_1"] = np.log(df["Adj Close"]).diff()

# Verify the output
df.head()"""
    ),
    md("### (2) EDA of Original dataset"),
    code(
        r"""# Descriptive statistics
df.describe().T"""
    ),
    code(
        r"""fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
df["Adj Close"].plot(ax=axes[0], color="#1f77b4", linewidth=1.4)
axes[0].set_title("CSI 300 Adjusted Close")
axes[0].set_ylabel("Index level")
axes[0].grid(True, alpha=0.3)

df["log_ret_1"].plot(ax=axes[1], color="#7f7f7f", linewidth=1.0)
axes[1].set_title("Daily Log Returns")
axes[1].set_ylabel("Return")
axes[1].grid(True, alpha=0.3)
plt.tight_layout()
plt.show()"""
    ),
    md("### (3) Cleaning & Imputation"),
    code(
        r"""# Check for missing values
df.isnull().sum()"""
    ),
    md(
        "### (4) Feature Engineering\n\n"
        "候选特征不仅包括滚动收益和滚动波动率，也包括均线偏离、成交量标准化、近期极端收益、K 线结构、RSI、MACD 和 ATR。"
    ),
    code(
        r"""# Core returns and price/volume structure
df["simple_ret_1"] = df["Adj Close"].pct_change()
df["intraday_ret"] = df["Close"] / df["Open"] - 1
df["range_pct"] = df["High"] / df["Low"] - 1
df["gap_ret"] = df["Open"] / df["Close"].shift(1) - 1
df["upper_shadow"] = (df["High"] - df[["Open", "Close"]].max(axis=1)) / df["Close"]
df["lower_shadow"] = (df[["Open", "Close"]].min(axis=1) - df["Low"]) / df["Close"]
df["body_pct"] = (df["Close"] - df["Open"]) / df["Open"]
df["close_pos"] = (df["Close"] - df["Low"]) / (df["High"] - df["Low"]).replace(0, np.nan)
df["volume_ret"] = np.log(df["Volume"]).diff()
df["dow"] = df.index.dayofweek

# Create features (predictors) list
features_list = [
    "log_ret_1", "simple_ret_1", "intraday_ret", "range_pct", "gap_ret",
    "upper_shadow", "lower_shadow", "body_pct", "close_pos", "volume_ret", "dow",
]

for window in [2, 3, 5, 10, 20, 40, 60, 120]:
    df[f"ret_sum_{window}"] = df["log_ret_1"].rolling(window).sum()
    df[f"ret_mean_{window}"] = df["log_ret_1"].rolling(window).mean()
    df[f"volatility_{window}"] = df["log_ret_1"].rolling(window).std()
    df[f"ma_ratio_{window}"] = df["Adj Close"] / df["Adj Close"].rolling(window).mean() - 1
    df[f"volume_z_{window}"] = (
        df["Volume"] - df["Volume"].rolling(window).mean()
    ) / df["Volume"].rolling(window).std()
    df[f"rolling_min_ret_{window}"] = df["log_ret_1"].rolling(window).min()
    df[f"rolling_max_ret_{window}"] = df["log_ret_1"].rolling(window).max()
    features_list += [
        f"ret_sum_{window}", f"ret_mean_{window}", f"volatility_{window}",
        f"ma_ratio_{window}", f"volume_z_{window}",
        f"rolling_min_ret_{window}", f"rolling_max_ret_{window}",
    ]

for window in [6, 14, 21]:
    delta = df["Adj Close"].diff()
    gain = delta.clip(lower=0).rolling(window).mean()
    loss = (-delta.clip(upper=0)).rolling(window).mean()
    rs = gain / loss.replace(0, np.nan)
    df[f"rsi_{window}"] = 100 - (100 / (1 + rs))
    features_list.append(f"rsi_{window}")

ema12 = df["Adj Close"].ewm(span=12, adjust=False).mean()
ema26 = df["Adj Close"].ewm(span=26, adjust=False).mean()
df["macd"] = ema12 - ema26
df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
df["macd_hist"] = df["macd"] - df["macd_signal"]
features_list += ["macd", "macd_signal", "macd_hist"]

true_range = pd.concat(
    [
        df["High"] - df["Low"],
        (df["High"] - df["Close"].shift(1)).abs(),
        (df["Low"] - df["Close"].shift(1)).abs(),
    ],
    axis=1,
).max(axis=1)
for window in [14, 20]:
    df[f"atr_{window}"] = true_range.rolling(window).mean() / df["Adj Close"]
    features_list.append(f"atr_{window}")

# Define the forward return and label before dropping NaN values.
target_threshold = experiment_config["target_threshold"]
df["next_log_ret"] = df["log_ret_1"].shift(-1)
df["Label"] = np.where(df["next_log_ret"] > target_threshold, 1, 0)
df.loc[df["next_log_ret"].isna(), "Label"] = np.nan

# Drop NaN values
df = df[features_list + ["Label", "next_log_ret"]].replace([np.inf, -np.inf], np.nan).dropna()

print(f"Candidate feature count: {len(features_list)}")
print(f"Usable observations: {len(df)}")"""
    ),
    md("#### (a) Feature Specification"),
    code(
        r"""# Convert to NumPy
X_all = df[features_list]
X_all.head(2)"""
    ),
    code(
        r"""# Feature subset derived by the funnelling approach.
y_for_selection = df["Label"].astype(int).values
X_train_all, X_test_all, y_train, y_test = train_test_split(
    X_all, y_for_selection, test_size=0.2, shuffle=False
)
sample_weights = compute_sample_weight(class_weight="balanced", y=y_train)

corr = X_train_all.corr().abs()
upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
corr_dropped = [column for column in upper.columns if any(upper[column] > 0.98)]
corr_features = [column for column in X_train_all.columns if column not in corr_dropped]

mi_scores = pd.Series(
    mutual_info_classif(X_train_all[corr_features], y_train, random_state=42),
    index=corr_features,
).sort_values(ascending=False)
filter_features = list(mi_scores.head(min(64, len(mi_scores))).index)

tscv = TimeSeriesSplit(n_splits=5, gap=1)
base_selector_params = {
    "verbosity": 0,
    "eval_metric": "logloss",
    "tree_method": "hist",
    "random_state": 42,
    "n_jobs": -1,
    "n_estimators": 120,
    "max_depth": 2,
    "learning_rate": 0.035,
    "subsample": 0.75,
    "colsample_bytree": 0.75,
    "min_child_weight": 5,
    "gamma": 1.0,
    "reg_alpha": 0.5,
    "reg_lambda": 3.0,
}

wrapper_rows = []
for n_features in [10, 15, 20, 25, 30, 35, 40, 50, len(filter_features)]:
    cols = filter_features[: min(n_features, len(filter_features))]
    selector_model = XGBClassifier(**base_selector_params)
    cv_scores = cross_val_score(
        selector_model,
        X_train_all[cols],
        y_train,
        cv=tscv,
        scoring="roc_auc",
        params={"sample_weight": sample_weights},
        n_jobs=1,
    )
    wrapper_rows.append({
        "n_features": len(cols),
        "cv_roc_auc_mean": cv_scores.mean(),
        "features": cols,
    })

wrapper_table = pd.DataFrame(wrapper_rows).drop_duplicates("n_features")
best_wrapper = wrapper_table.sort_values(["cv_roc_auc_mean", "n_features"], ascending=[False, True]).iloc[0]
wrapper_features = list(best_wrapper["features"])

embedded_model = XGBClassifier(**base_selector_params, importance_type="gain")
embedded_model.fit(X_train_all[wrapper_features], y_train, sample_weight=sample_weights)
gain_scores = pd.Series(embedded_model.feature_importances_, index=wrapper_features).sort_values(ascending=False)

embedded_rows = []
for n_features in [10, 15, 20, 25, 30, 35, 40, len(gain_scores)]:
    cols = list(gain_scores.head(min(n_features, len(gain_scores))).index)
    selector_model = XGBClassifier(**base_selector_params)
    cv_scores = cross_val_score(
        selector_model,
        X_train_all[cols],
        y_train,
        cv=tscv,
        scoring="roc_auc",
        params={"sample_weight": sample_weights},
        n_jobs=1,
    )
    embedded_rows.append({
        "n_features": len(cols),
        "cv_roc_auc_mean": cv_scores.mean(),
        "features": cols,
    })

embedded_table = pd.DataFrame(embedded_rows).drop_duplicates("n_features")
best_embedded = embedded_table.sort_values(["cv_roc_auc_mean", "n_features"], ascending=[False, True]).iloc[0]
final_features = list(best_embedded["features"])

X = df[final_features]

pd.DataFrame({
    "Rank": range(1, len(final_features) + 1),
    "Feature": final_features,
    "Gain": gain_scores.loc[final_features].round(6).values,
})"""
    ),
    md("#### (b) Target or Label Definition"),
    code(
        r"""# Define Target
y = df["Label"].astype(int).values
y"""
    ),
    code(
        r"""# label count
class_labels = np.bincount(y)
class_labels"""
    ),
    md("### (5) Boosting Ensemble"),
    code(
        r"""# Splitting the datasets into training and testing data.
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

# Output the train and test data size
print(f"Train and Test Size {len(X_train)}, {len(X_test)}")"""
    ),
    code(
        r"""# Scale and fit the classifier model

# For binary or multiclass classification
sample_weights = compute_sample_weight(class_weight="balanced", y=y_train)

base_model = XGBClassifier(
    verbosity=0,
    eval_metric="logloss",
)

base_model.fit(
    X_train,
    y_train,
    sample_weight=sample_weights,
)"""
    ),
    code(
        r"""# Predicting the test dataset
y_pred = base_model.predict(X_test)

# Predict Probabilities
y_proba = base_model.predict_proba(X_test)"""
    ),
    code(
        r"""# Accuracy Scores
acc_train = accuracy_score(y_train, base_model.predict(X_train))
acc_test = accuracy_score(y_test, y_pred)

print(f"Train Accuracy: {acc_train:0.4}, Test Accuracy: {acc_test:0.4}")"""
    ),
    code(
        r"""# Balanced Accuracy Scores
bal_acc_train = balanced_accuracy_score(y_train, base_model.predict(X_train))
bal_acc_test = balanced_accuracy_score(y_test, y_pred)

print(f"Train Balanced Accuracy: {bal_acc_train:0.4}, Test Balanced Accuracy: {bal_acc_test:0.4}")"""
    ),
    code(
        r"""# Display confussion matrix
disp_cm = ConfusionMatrixDisplay.from_estimator(
    base_model,
    X_test,
    y_test,
    display_labels=base_model.classes_,
    cmap=plt.cm.Blues,
)
disp_cm.ax_.set_title("Confusion matrix")
plt.show()"""
    ),
    code(
        r"""# Classification Report
print(classification_report(y_test, y_pred))"""
    ),
    code(
        r"""# Display ROCCurve
disp_roc = RocCurveDisplay.from_estimator(
    base_model,
    X_test,
    y_test,
    name="XGBoost",
)

disp_roc.ax_.set_title("ROC Curve")
plt.plot([0, 1], [0, 1], linestyle="--")
plt.show()"""
    ),
    code(
        r"""# Display PR Curve
disp_pr = PrecisionRecallDisplay.from_estimator(
    base_model,
    X_test,
    y_test,
    name="XGBoost",
)

disp_pr.ax_.set_title("Precision-Recall Curve")
plt.show()"""
    ),
    md("### (6) Hyperparameter Tuning"),
    md("#### (a) XGBoost's hyper-parameter"),
    code(
        r"""# Timeseries Cross Validation 2-split Demonstration
tscv_demo = TimeSeriesSplit(n_splits=2, gap=1)
for train, test in tscv_demo.split(X):
    print(f"Train: {train}, Test: {test}")"""
    ),
    code(
        r"""# Cross-validation
tscv = TimeSeriesSplit(n_splits=5, gap=1)"""
    ),
    code(
        r"""# Get params list
base_model.get_params()"""
    ),
    md("#### (b) Randomized Search"),
    code(
        r"""# Randomized search configuration
param_dist = {
    "n_estimators": randint(60, 350),
    "max_depth": randint(1, 4),
    "learning_rate": loguniform(0.01, 0.12),
    "subsample": uniform(0.60, 0.40),
    "colsample_bytree": uniform(0.60, 0.40),
    "min_child_weight": randint(2, 18),
    "gamma": uniform(0, 6),
    "reg_alpha": loguniform(1e-4, 8),
    "reg_lambda": loguniform(0.5, 20),
}

search = RandomizedSearchCV(
    estimator=XGBClassifier(verbosity=0, eval_metric="logloss", tree_method="hist", random_state=42, n_jobs=-1),
    param_distributions=param_dist,
    n_iter=50,
    scoring="roc_auc",
    cv=tscv,
    random_state=42,
    n_jobs=1,
)

search.fit(X_train, y_train, sample_weight=sample_weights)
best_params = search.best_params_

print("Best parameters found by randomized search:")
for k, v in best_params.items():
    print(f"  {k}: {v}")
print(f"Best cv/roc_auc_mean: {search.best_score_:.4f}")"""
    ),
    code(
        r"""# Create tuned model using best parameters
tuned_model = XGBClassifier(
    **best_params,
    verbosity=0,
    eval_metric="logloss",
    tree_method="hist",
    random_state=42,
    n_jobs=-1,
)

# Fit with evaluation tracking
tuned_model.fit(
    X_train,
    y_train,
    sample_weight=sample_weights,
    eval_set=[(X_train, y_train), (X_test, y_test)],
    verbose=False,
)

print("Tuned model training completed successfully!")"""
    ),
    code(
        r"""# Return the evaluation results
evals_result = tuned_model.evals_result()
pd.DataFrame({
    "train_logloss": evals_result["validation_0"]["logloss"],
    "test_logloss": evals_result["validation_1"]["logloss"],
}).tail()"""
    ),
    code(
        r"""# Cross validation score with tuned model
cv_scores = cross_val_score(
    tuned_model,
    X_train,
    y_train,
    cv=tscv,
    scoring="f1",
    params={"sample_weight": sample_weights},
    n_jobs=1,
)
print(f"Mean CV Score: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")"""
    ),
    code(
        r"""# Predicting the test dataset
y_pred = tuned_model.predict(X_test)
y_proba = tuned_model.predict_proba(X_test)

# Measure Accuracy
acc_train = accuracy_score(y_train, tuned_model.predict(X_train))
acc_test = accuracy_score(y_test, y_pred)

print(f"\n Training Accuracy \t: {acc_train :0.4} \n Test Accuracy \t\t: {acc_test :0.4}")"""
    ),
    code(
        r"""bal_acc_train = balanced_accuracy_score(y_train, tuned_model.predict(X_train))
bal_acc_test = balanced_accuracy_score(y_test, y_pred)

print(f"Train Balanced Accuracy: {bal_acc_train:0.4}, Test Balanced Accuracy: {bal_acc_test:0.4}")
print(f"Test ROC AUC: {roc_auc_score(y_test, y_proba[:, 1]):0.4}")
print(f"Test F1: {f1_score(y_test, y_pred):0.4}")
print(f"Test Precision: {precision_score(y_test, y_pred):0.4}")
print(f"Test Recall: {recall_score(y_test, y_pred):0.4}")"""
    ),
    code(
        r"""# Tuned Model: Evaluation

# Confusion Matrix
disp = ConfusionMatrixDisplay.from_estimator(
    tuned_model,
    X_test,
    y_test,
    display_labels=tuned_model.classes_,
    cmap=plt.cm.Blues,
)
disp.ax_.set_title("Confusion matrix")
plt.show()

# Classification Report
print(classification_report(y_test, y_pred))

# ROC Curve
disp_roc = RocCurveDisplay.from_estimator(
    tuned_model,
    X_test,
    y_test,
    name="Tuned XGBoost",
)
disp_roc.ax_.set_title("ROC Curve")
plt.plot([0, 1], [0, 1], linestyle="--")
plt.show()

# PR Curve
disp_pr = PrecisionRecallDisplay.from_estimator(
    tuned_model,
    X_test,
    y_test,
    name="Tuned XGBoost",
)
disp_pr.ax_.set_title("Precision-Recall Curve")
plt.show()"""
    ),
    md("### (7) Evaluation"),
    md("#### (a) Feature Importance"),
    code(
        r"""# Plot the feature importance of the tuned model
plot_importance(tuned_model, importance_type="weight", title="Tuned Model Feature Importance", show_values=False)
plt.tight_layout()
plt.grid(True, alpha=0.3)
plt.show()"""
    ),
    code(
        r"""# The Gain is the most relevant attribute to interpret the relative importance of each feature.
gain_importance = tuned_model.get_booster().get_score(importance_type="gain")
pd.Series(gain_importance).sort_values(ascending=False).to_frame("gain")"""
    ),
    code(
        r"""# Feature importance by gain
plot_importance(tuned_model, importance_type="gain", show_values=False)
plt.tight_layout()
plt.grid(True, alpha=0.3)
plt.show()"""
    ),
    md("#### (b) Backtest Analysis"),
    code(
        r"""# Optional add-on: simple backtest of predicted signals.
test_index = X_test.index
signal = pd.Series(y_pred, index=test_index, name="signal")
strategy_returns = signal * df.loc[test_index, "next_log_ret"]
buy_hold_returns = df.loc[test_index, "next_log_ret"]

def performance(log_returns, exposure):
    wealth = np.exp(log_returns.cumsum())
    annual_return = wealth.iloc[-1] ** (252 / len(log_returns)) - 1
    annual_volatility = log_returns.std() * np.sqrt(252)
    sharpe = annual_return / annual_volatility if annual_volatility > 0 else np.nan
    drawdown = wealth / wealth.cummax() - 1
    return pd.Series({
        "total_return": wealth.iloc[-1] - 1,
        "annual_return": annual_return,
        "annual_volatility": annual_volatility,
        "sharpe": sharpe,
        "max_drawdown": drawdown.min(),
        "exposure": exposure,
    })

backtest = pd.DataFrame({
    "strategy": performance(strategy_returns, signal.mean()),
    "buy_hold": performance(buy_hold_returns, 1.0),
})
backtest.round(4)"""
    ),
    code(
        r"""wealth = pd.DataFrame({
    "Strategy": np.exp(strategy_returns.cumsum()),
    "Buy & Hold": np.exp(buy_hold_returns.cumsum()),
})

fig, ax = plt.subplots(figsize=(9, 4.5))
wealth.plot(ax=ax, linewidth=2)
ax.set_title("Cumulative Wealth on Test Set")
ax.set_ylabel("Cumulative wealth")
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()"""
    ),
    md(
        "## Conclusion\n\n"
        "调参后的 XGBoost 在测试集上的 ROC AUC 高于 0.5，说明模型对下一交易日有效上涨具有一定排序能力，但预测能力仍然有限。"
        "这一结果符合短期指数收益噪声较高、方向预测困难的经验事实。回测结果用于检验预测信号的经济含义，"
        "但未考虑交易成本和滑点，因此应作为附加参考，而不是独立交易建议。"
    ),
]


def main() -> None:
    write_notebook("Answer1.ipynb", answer1_cells)
    write_notebook("Answer2.ipynb", answer2_cells)
    write_notebook("Answer3.ipynb", answer3_cells)
    print("Wrote Answer1.ipynb, Answer2.ipynb, Answer3.ipynb")


if __name__ == "__main__":
    main()
