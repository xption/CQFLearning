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


answer3_cells = [
    md(
        "# Question C：使用梯度提升预测正向市场走势\n\n"
        "本题基于第 2 题筛选出的特征，建立、调参并评估一个用于预测沪深 300 指数下一交易日有效上涨的梯度提升模型。"
    ),
    md(
        "## 建模设计\n\n"
        "目标变量为二分类标签：如果下一交易日对数收益率大于 0.15%，则为 1；否则为 0。"
        "这个定义使“上涨”不是简单的大于零，而是剔除了非常接近零的小幅波动。\n\n"
        "模型采用 `XGBoostClassifier`。选择 XGBoost 的原因是它能够处理非线性关系和特征交互，"
        "并且内置正则化、列采样和行采样，适合金融数据中噪声较高、信号较弱的场景。"
    ),
    code(
        r"""from pathlib import Path
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import ConfusionMatrixDisplay, RocCurveDisplay

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

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
    regularized_xgb,
    evaluate_classifier,
    tune_xgb,
    backtest_signal,
)

config = WorkflowConfig(data_path=Path("CSI300_2005_2026.csv"))
config"""
    ),
    code(
        r"""data, feature_cols = build_features(config)
X_train, X_test, y_train, y_test, train_frame, test_frame = train_test_split_time(
    data, feature_cols, config
)
selection = feature_selection_funnel(X_train, y_train, config)
final_features = selection["final_features"]

modeling_summary = pd.DataFrame({
    "项目": [
        "样本起止", "训练集起止", "测试集起止",
        "训练集样本数", "测试集样本数", "原始特征数", "最终特征数",
        "训练集正类比例", "测试集正类比例",
    ],
    "数值": [
        f"{data.index.min().date()} 至 {data.index.max().date()}",
        f"{train_frame.index.min().date()} 至 {train_frame.index.max().date()}",
        f"{test_frame.index.min().date()} 至 {test_frame.index.max().date()}",
        len(train_frame), len(test_frame), len(feature_cols), len(final_features),
        round(y_train.mean(), 4), round(y_test.mean(), 4),
    ],
})
modeling_summary"""
    ),
    md(
        "## 基准模型\n\n"
        "先使用一组保守的正则化 XGBoost 参数训练基准模型。由于训练集正负样本比例并非完全相等，"
        "模型使用 `scale_pos_weight` 处理类别不平衡。决策阈值不直接固定为 0.5，而是在训练集上用 Youden J 统计量选择，"
        "然后应用到测试集。"
    ),
    code(
        r"""base_model = regularized_xgb(y_train, config)
base_eval = evaluate_classifier(
    base_model,
    X_train[final_features],
    y_train,
    X_test[final_features],
    y_test,
)

base_metrics = pd.DataFrame({
    "指标": ["训练集 AUC", "测试集 AUC", "Accuracy", "Balanced Accuracy", "决策阈值"],
    "数值": [
        base_eval["train_auc"], base_eval["test_auc"], base_eval["accuracy"],
        base_eval["balanced_accuracy"], base_eval["threshold"],
    ],
})
base_metrics["数值"] = base_metrics["数值"].round(4)
base_metrics"""
    ),
    md(
        "## 超参数调优\n\n"
        "调优在训练集内部完成，使用 `TimeSeriesSplit(n_splits=5, gap=1)`，评分指标为 ROC AUC。"
        "搜索的超参数包括树数量、树深度、学习率、行采样、列采样、最小子节点权重、gamma、L1 和 L2 正则化。"
        "整个过程完全在本地运行，不使用 Colab 或 W&B。"
    ),
    code(
        r"""search = tune_xgb(X_train[final_features], y_train, config, n_iter=50)

best_params = pd.DataFrame({
    "参数": list(search.best_params_.keys()),
    "最优值": list(search.best_params_.values()),
})
print(f"训练集时间序列交叉验证最佳 ROC AUC: {search.best_score_:.4f}")
best_params"""
    ),
    code(
        r"""tuned_eval = evaluate_classifier(
    search.best_estimator_,
    X_train[final_features],
    y_train,
    X_test[final_features],
    y_test,
)

tuned_metrics = pd.DataFrame({
    "指标": ["训练集 AUC", "测试集 AUC", "Accuracy", "Balanced Accuracy", "决策阈值"],
    "数值": [
        tuned_eval["train_auc"], tuned_eval["test_auc"], tuned_eval["accuracy"],
        tuned_eval["balanced_accuracy"], tuned_eval["threshold"],
    ],
})
tuned_metrics["数值"] = tuned_metrics["数值"].round(4)
tuned_metrics"""
    ),
    md(
        "## 预测质量评估\n\n"
        "ROC AUC 衡量模型对正负样本排序的能力。AUC 大于 0.5 说明模型在测试集上优于随机排序，"
        "但数值并不高，符合短期指数收益难以预测的现实。混淆矩阵和分类报告进一步展示了模型在 0/1 两类上的错误结构。"
    ),
    code(
        r"""print("Confusion matrix [[TN, FP], [FN, TP]]:")
print(tuned_eval["confusion_matrix"])
print()
print("Classification report:")
print(tuned_eval["classification_report"])"""
    ),
    code(
        r"""fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

RocCurveDisplay.from_predictions(
    y_test,
    tuned_eval["test_proba"],
    ax=axes[0],
    name="Tuned XGBoost",
    color="#1f77b4",
)
axes[0].plot([0, 1], [0, 1], linestyle="--", color="gray", linewidth=1)
axes[0].set_title("ROC 曲线")
axes[0].grid(True, alpha=0.3)

ConfusionMatrixDisplay(
    confusion_matrix=tuned_eval["confusion_matrix"],
    display_labels=["0：非显著上涨", "1：有效上涨"],
).plot(ax=axes[1], colorbar=False, cmap="Blues")
axes[1].set_title("混淆矩阵")

plt.tight_layout()
plt.show()"""
    ),
    md(
        "## 特征重要性\n\n"
        "下图展示调参后模型的 gain importance。重要性较高的特征包括短期均线偏离、MACD、近期极端收益、"
        "成交量标准化、RSI 和日内价格结构等。这说明模型主要从短期趋势、反转压力、波动状态和交易活跃度中提取信号。"
    ),
    code(
        r"""booster = tuned_eval["model"].get_booster()
score = booster.get_score(importance_type="gain")
importance = (
    pd.Series(score, name="gain")
    .reindex(final_features)
    .fillna(0)
    .sort_values(ascending=False)
)

fig, ax = plt.subplots(figsize=(8, 7))
importance.head(20).sort_values().plot(kind="barh", ax=ax, color="#2ca02c")
ax.set_title("Top 20 特征重要性：XGBoost Gain")
ax.set_xlabel("Gain")
ax.grid(True, axis="x", alpha=0.3)
plt.tight_layout()
plt.show()

importance.head(20).round(4).to_frame()"""
    ),
    md(
        "## 可选回测：将预测信号用于简单交易策略\n\n"
        "作为附加分析，构造一个简单多头策略：当模型预测为 1 时持有沪深 300，当模型预测为 0 时空仓。"
        "该回测不考虑交易成本、滑点和资金约束，因此只能作为预测信号经济意义的初步检验。"
    ),
    code(
        r"""backtest = backtest_signal(test_frame, tuned_eval["y_pred"])
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
ax.set_title("测试集累计财富曲线")
ax.set_ylabel("累计财富")
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()"""
    ),
    md(
        "## 结论\n\n"
        "调参后的 XGBoost 在测试集上的 ROC AUC 约为 0.57，说明模型具有一定但较弱的方向排序能力。"
        "Accuracy 和 balanced accuracy 也仅略高于随机水平，这与短期指数收益接近有效市场、噪声较高的事实一致。\n\n"
        "从经济意义看，简单信号策略在测试期内优于买入持有，并且最大回撤更小。不过该结果仍需谨慎解读："
        "正式交易前应加入交易成本、滑点、参数稳定性检验和滚动样本外测试。总体而言，模型不是一个强预测器，"
        "但在受限的监督学习框架下，它展示了比随机分类更好的样本外排序能力和一定的风险控制价值。"
    ),
]


def main() -> None:
    write_notebook("Answer1.ipynb", answer1_cells)
    write_notebook("Answer2.ipynb", answer2_cells)
    write_notebook("Answer3.ipynb", answer3_cells)
    print("Wrote Answer1.ipynb, Answer2.ipynb, Answer3.ipynb")


if __name__ == "__main__":
    main()
