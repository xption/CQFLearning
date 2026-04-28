# Answer.ipynb 审阅待修正问题

审阅范围：

- `Assignments/Exam 2 - April 2026.pdf`
- `Assignments/Exam 2_Resource on Milstein.pdf`
- `Resources/9_montecarlo.ipynb`
- `Resources/JA26T5 Slides v.2.pdf`
- `Answer.ipynb`

总体判断：`Answer.ipynb` 已基本覆盖考试题核心要求，包括 European call、binary call、Euler-Maruyama、Milstein、GBM closed-form stock simulation、参数敏感性分析、antithetic variates、报告结构和 references。以下问题建议后续讨论后再修改。

## T01 已完成：第 4.4 节保存输出与代码不一致

Cell 19 的源码里已经加入了：

- `error_analysis_table`
- Black-Scholes European call benchmark
- cash-or-nothing binary call benchmark
- 每种 MC 方法相对解析价格的绝对误差

原问题：notebook 保存的输出中没有显示 error analysis table，只显示了 baseline pricing table 和两行对比文字。

风险：

- Conclusion 中提到 analytical benchmark 和 error analysis，但读者在当前保存输出中看不到对应误差表。
- 容易被认为 `Results - appropriate tables, error analysis and comparisons [40%]` 支撑不足。

建议：

- 重新运行并保存第 4.4 节，确保 `error_analysis_table` 出现在 notebook 输出中。

完成记录：

- 2026-04-28 复核 `Answer.ipynb` 后确认 Cell 19 已保存 3 个输出：baseline pricing table、`error_analysis_table`、benchmark 说明文字。
- `error_analysis_table` 已正常显示 Black-Scholes European call benchmark、cash-or-nothing binary call benchmark，以及三种 MC 方法的 absolute error。

## T02 已完成：Antithetic Variates 未覆盖 GBM closed-form simulation

原问题：第 6 节 AV 只比较：

- Euler-Maruyama
- Milstein

没有包含：

- GBM closed-form terminal simulation + AV

说明：

- 考试题没有明确要求 AV 必须应用到三种模拟方法全部。
- 但 JA26T5 slides 中的 AV 示例是基于 exact terminal GBM option pricing framework，即 `ST = S0 exp(...)`。

风险：

- 阅卷者可能期待看到 GBM closed-form simulation 的 AV 结果。

建议：

- 方案 A：补充 `GBM closed-form + AV` 结果。
- 方案 B：在文字中明确说明第 6 节只用 Euler/Milstein 离散路径演示 AV 技术。

完成记录：

- 2026-04-28 已采用方案 A。
- `Answer.ipynb` 第 6 节的 `antithetic_variates()` 已补充 GBM closed-form terminal simulation 的 AV 计算。
- 第 6 节结果表已更新为 6 行：`GBM closed-form path`、`GBM closed-form path+AV`、`欧拉法`、`欧拉法+AV`、`米尔斯坦法`、`米尔斯坦法+AV`。
- European call 和 binary call 均已覆盖 GBM/Euler/Milstein 的普通 MC 与 AV 对比。

## T03 已完成：Antithetic Variates 的比较口径改为固定总路径数

原设置：

- 普通 MC 使用 `N=100000` 条路径。
- AV 使用 `N=100000` 对 antithetic pairs，实际生成 `2N=200000` 条路径。
- AV 标准误差按 `N` 个 pair average 样本计算。

这个定义本身合理，也符合 lecture 中 pair estimator 的写法。

风险：

- 如果直接比较普通 MC 的 `N` 条路径和 AV 的 `2N` 条路径，SE 下降既来自负相关，也可能部分来自更多模拟路径。

处理方式：

- 不再沿用 lecture 中“`N` 表示 pair count、实际生成 `2N` 条路径”的比较口径。
- 改为固定总路径数 `N`，让普通 MC 和 AV 的路径预算一致。

完成记录：

- 2026-04-28 已决定采用固定总路径数口径。
- 普通 MC 使用 `N=100000` 条路径。
- AV 也使用总计 `N=100000` 条路径，即 `N/2=50000` 对 antithetic pairs，包含 `50000` 条正向路径和 `50000` 条负向路径。
- AV 标准误差按 `N/2=50000` 个 pair average 样本计算。
- `Answer.ipynb` 第 2.7 节、第 3 节、第 6 节说明和第 6 节代码/输出已同步更新。

## T04 已完成：“二元期权在深度虚值时方差极高”表述不准确

原问题：第 7.2 节有类似表述：

```text
二元期权在深度虚值时方差极高，模拟不稳定，需增加路径数提升稳定性。
```

问题：

- cash-or-nothing binary payoff 是 Bernoulli payoff。
- 绝对方差为 `p(1-p)`，在 `p≈0.5` 时最大。
- 深度虚值时 `p` 很小，绝对方差反而不高。

更准确的表述：

```text
二元期权在深度虚值时命中事件很少，价格估计的相对误差可能较大，因此可能需要更多路径提升尾部概率估计的稳定性。
```

完成记录：

- 2026-04-28 已按讨论结果直接从 `Answer.ipynb` 第 7.2 节删除该条表述。
- 后续 Problems Encountered 中的编号已顺延调整。

## T05 部分结论表述偏强

当前有几处表述方向合理，但证据支撑略弱：

- “三种方法趋势完全一致，说明数值方案稳定可靠。”
- “M=252 可有效降低误差。”
- “二元期权对离散误差更敏感。”

问题：

- notebook 当前没有做不同 `M` 的收敛测试。
- 也没有系统展示离散误差随时间步长变化。

建议：

- 弱化为：

```text
在本实验参数范围和 M=252 的设置下，三种方法给出的价格和趋势较为接近。
```

或补充不同 `M` 下的误差/价格比较后再保留较强结论。

## T06 已完成：可复现性不足

原问题：notebook 没有实际设置随机种子，只在补充说明中提到：

```python
np.random.seed(42)
```

风险：

- 重新运行后，敏感性分析、AV 结果和误差分析表会发生变化。
- 文本结论和保存输出可能不完全一致。

建议：

- 在 import 后显式加入 `np.random.seed(42)`。
- 或说明所有结果为一次随机实验结果，重新运行会有 Monte Carlo sampling variation。

完成记录：

- 2026-04-28 已在 `Answer.ipynb` 的 import 单元格后显式加入 `np.random.seed(42)`。
- 已重新运行并保存整本 notebook，使敏感性分析、AV 结果和误差分析表与固定随机种子后的输出一致。

## T07 敏感性分析部分缺少 SE 或 benchmark error

当前第 5 节敏感性分析包含：

- price tables
- European price curves
- binary price curves

但没有列出：

- 每个敏感性点的 SE
- 每个敏感性点相对 analytical benchmark 的 error

说明：

- 题目未强制要求每个敏感性点都列 SE。
- 但 `Results - appropriate tables, error analysis and comparisons [40%]` 权重较高。

建议：

- 至少确保第 4.4 节 baseline error analysis table 正常显示。
- 如需进一步增强报告，可在敏感性分析中补充 benchmark line 或 error summary。

## T08 已完成：Markdown 显示细节需要 polish

原问题：Cell 34 中有转义/HTML 实体残留，例如：

```text
# 7. Interesting Observations \&amp; Problems Encountered
Kloeden, P. E., \&amp; Platen, E.
```

风险：

- 渲染后可能显示成不自然的 `&amp;`。

建议：

- 改成正常 Markdown：

```text
# 7. Interesting Observations & Problems Encountered
Kloeden, P. E., & Platen, E.
```

完成记录：

- 2026-04-28 已清理 `Answer.ipynb` Cell 34 中的 `\&amp;` / `&amp;` 残留。
- 同步清理了同一 cell 中不必要的 Markdown 转义，例如 `\(15%\)`、`\_`、`np.random.seed\(42\)`。
- 第 7 节标题、Conclusion/References 标题和 references 显示已改为正常 Markdown。
