## Exam2 维护说明 - 2026-04-27

### 原始需求

`Assignments` 目录是 CQF 第二次考试题目：

- `Exam 2 - April 2026.pdf`：考试题
- `Exam 2_Resource on Milstein.pdf`：考试题附带参考资料

`Resources` 目录是 CQF 第二次考试对应课程资料：

- `9_montecarlo.ipynb`：与考试题非常吻合，是主要实现风格参考
- `JA26T5 Slides v.2.pdf`：主要对应 antithetic variates variance reduction technique

目标是阅读题目和课程资料，并将完整答案维护在 `Answer.ipynb` 中。

### 题目要求理解

考试题核心要求可拆为三部分：

1. 使用 Euler-Maruyama scheme、Milstein scheme 和 closed form solution 模拟 underlying stock price，并基于模拟终值计算 European call 和 binary call 价格。
2. Vary the data to see the effect on option price，即分析参数敏感性。
3. Examine antithetic variates variance reduction technique，即分析对偶变量方差缩减效果。

报告评分中 `Results - appropriate tables, error analysis and comparisons [40%]` 很重要，因此不仅需要代码，还需要表格、图和比较分析。

### 关键概念约定

`closed form solution` 在本题中指 **GBM stock price process 的闭式解 / exact path or terminal simulation**，不是 Black-Scholes option pricing formula。

原因是题目写的是：

```text
Use the Euler-Maruyama scheme, Milstein scheme and closed form solution for simulating the underlying stock price.
```

这里 closed form solution 与 Euler、Milstein 并列，都是模拟股价的方法。

Black-Scholes 公式可以后续作为 analytical benchmark 做误差分析，但不应作为三种模拟方法之一。若使用，应明确写作：

```text
Black-Scholes formulas are used only as analytical benchmark values for error analysis, not as the pricing method required by the task.
```

European call 解析基准可用 Black-Scholes call formula；binary cash-or-nothing call 解析基准可用：

```text
exp(-rT) * N(d2)
```

### 当前 `Answer.ipynb` 结构

当前 notebook 已按报告逻辑整理：

- 第 1 节：Introduction
- 第 2 节：模型与方法
- 第 3 节：基础参数，只保留依赖和初始参数
- 第 4 节：标的股价模拟与初始参数定价结果
- 第 5 节：参数敏感性分析
- 第 6 节：对偶变量方差缩减效果
- 第 7 节：Interesting Observations & Problems Encountered
- 第 8 节：Conclusion
- 第 9 节：References

第三节不再放“完整代码”。代码按首次使用位置拆分：

- 第 4 节定义路径模拟、payoff、Monte Carlo pricing 等函数
- 第 5 节定义 `sensitivity_analysis()` 和 `make_price_table()`
- 第 6 节定义 `simulate_stock_terminal()` 和 `antithetic_variates()`

### 全局参数约定

当前统一使用：

```python
S0 = 100
K = 100
r = 0.05
sigma = 0.2
T = 1
N = 100000
M = 252
dt = T / M
```

说明：

- `N=100000` 与 `9_montecarlo.ipynb` 中路径示例一致。
- 第 4 节 `baseline_n_paths = N`。
- 路径可视化只绘制前 `100` 条路径，参考 `9_montecarlo.ipynb` 的 `plt.plot(paths[:100].T)`。
- 对偶变量法中 `N=100000` 表示 antithetic pairs 数量，实际生成 `2N=200000` 条路径。
- AV 的标准误差按 `N` 个 pair average 样本计算。

### 第 4 节实现状态

第 4 节按 `9_montecarlo.ipynb` 风格实现：

1. 生成 paths 的 `DataFrame`
2. 绘制前 100 条 simulated paths
3. 使用终值 `S_T` 计算 European call 和 binary call 的价格与标准误差
4. 最后汇总三种方法结果

小节安排：

- `4.1 GBM closed-form solution 路径模拟`
- `4.2 Euler-Maruyama 路径模拟`
- `4.3 Milstein 路径模拟`
- `4.4 初始参数下的欧式与二元期权定价结果`

4.1、4.2、4.3 每节都在路径图之后立即输出本方法的定价表：

- 方法
- 欧式价格
- 欧式 SE
- 二元价格
- 二元 SE

4.4 再汇总三种方法，并打印简短比较分析。

三种路径模拟使用同一组随机数 `baseline_random_normals`，便于公平比较路径差异。

### 第 5 节实现状态

第 5 节完成参数敏感性分析，分析参数包括：

- `S0`
- `K`
- `r`
- `sigma`
- `T`

每个参数小节都包含：

- 调用 `sensitivity_analysis()`
- 输出价格结果表
- 欧式期权价格走势图
- 二元期权价格走势图

价格表包含六列方法结果：

- European GBM
- European Euler
- European Milstein
- Binary GBM
- Binary Euler
- Binary Milstein

关于题目中 `Then vary the data to see the effect on the option price`，当前共识是：每个参数给出价格表和价格曲线即可，不强制要求每个敏感性点都列 SE。

### 第 6 节实现状态

第 6 节已经覆盖 European call 和 binary call，不只计算欧式期权。

当前流程：

- 普通 MC 使用 Euler/Milstein 终值模拟，计算 European 和 binary 的价格与 SE
- AV 使用 `phi` 和 `-phi` 构造对偶路径
- 每个 pair 的 payoff 先取平均，再计算价格和 SE
- 输出自动生成的结果表，不再在 markdown 中写死数值

结果表列：

- 方法
- 欧式价格
- 欧式 SE
- 二元价格
- 二元 SE

方法行：

- 欧拉法
- 欧拉法+AV
- 米尔斯坦法
- 米尔斯坦法+AV

### 已完成 todo

已修复或完成：

- T01 参数敏感性函数临时参数未正确传入
- T02 GBM closed-form terminal simulation 改为用 Brownian increments 构造 `W_T`
- T03 标准误差公式统一加入贴现因子
- T04 `M=252` 前后一致，并解释为交易日离散
- T05 AV 引用未定义变量问题
- T06 AV 覆盖 binary call
- T07 AV 中 `N` 表示 pair count，实际路径数为 `2N`
- T08 payoff/pricing 函数改为显式传参
- T09 敏感性分析补充价格结果表
- 第 4 节新增 baseline stock path simulation 与 baseline option pricing results
- 全局路径数统一为 `N=100000`
- 第 6 节硬编码 markdown 表格改为代码自动生成

### 仍需注意或待完善

T10：闭式解表述仍需全篇谨慎检查。

- 避免把 `GBM closed-form simulation` 写成“期权价格闭式解”
- 更推荐写：
  - `GBM closed-form path`
  - `GBM exact terminal simulation`
  - `基于 GBM 闭式股价解的 MC 价格`

T11：结论中的断言需要结果支撑。

当前第 7 节仍有类似：

```text
Milstein整体精度高于Euler，尤其在高波动率下更明显
参数影响强度排序：波动率 > S0 > K > T > r
二元期权的方差缩减幅度更大
```

这些结论最好后续用表格或误差分析支持；如果不加证据，应改成更保守的表达。

T12：最终提交版结构还可继续 polish。

建议后续新增一节：

```text
Analytical Benchmarks and Error Analysis
```

使用：

- Black-Scholes European call formula
- Binary cash-or-nothing call analytical formula

作为 analytical benchmark，比较三种 MC 方法的 absolute error：

```text
| MC price - analytical benchmark |
```

这将更好回应题目 `appropriate tables, error analysis and comparisons`。

### 运行注意事项

- notebook 中使用 `%pip install numpy matplotlib pandas`
- 安装后可能需要重启 kernel
- 若想复现实验结果，可在 import 后添加：

```python
np.random.seed(42)
```

- 第 4 节会生成三组三维路径矩阵，每组约 `100000 x 253`，运行会占用一定内存和时间。
- 第 5 节每个参数敏感性分析都会做多次 Monte Carlo，完整运行耗时较长。

### 推荐下一步

1. 修复 T10：统一 closed form wording。
2. 新增 analytical benchmark 和 error analysis，顺便解决 T11。
3. 重新审视第 7 节 observations，删除或弱化没有数据支撑的强断言。
4. 最后统一 notebook 输出，确认所有表格、图和文本顺序适合提交。
