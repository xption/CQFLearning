# Answer.ipynb 待完善问题清单

## 高优先级

- [x] T01 参数敏感性函数逻辑错误：`sensitivity_analysis()` 创建了 `S0_temp`、`K_temp`、`r_temp`、`sigma_temp`、`T_temp`，但除 `T_temp` 外大部分临时参数没有真正传入模拟和 payoff 计算。
- [x] T02 GBM 闭式解模拟方式需要调整：当前使用 `phi[:, -1]`，更清晰的做法是为闭式终值单独生成 `N` 个标准正态随机数，或用同一组 Brownian increments 做公平比较。
- [x] T03 标准误差公式文字和代码不一致：文字写作 `std(Payoff) / sqrt(N)`，代码实际使用贴现后的 `exp(-rT) * std(Payoff) / sqrt(N)`，报告中应统一为贴现后的标准误差。
- [x] T04 基础参数中的 `M=50` 与代码中的 `M=252` 前后不一致，需要统一并解释选择。
- [x] T05 后续代码引用未定义变量：对偶变量部分使用了 `euler_se`、`mil_se`，但前文没有稳定定义这些变量。

## 中优先级

- [x] T06 Antithetic Variates 覆盖不完整：当前主要计算默认 European payoff，没有完整覆盖 binary call。
- [ ] T07 Antithetic Variates 中 `N` 的含义需要明确：当前可解释为 `N` 对 antithetic pairs，实际使用 `2N` 条路径，报告和代码需统一说明。
- [x] T08 `calculate_payoff()`、`monte_carlo_pricing()` 依赖全局变量，例如 `K`、`r`、`T`，容易导致敏感性分析出错，应改为显式传参。
- [ ] T09 敏感性分析缺少标准误差和结果表：目前主要输出价格，不足以支撑考试要求中的 tables、error analysis、comparisons。

## 低优先级 / 报告表达

- [ ] T10 闭式解表述需要谨慎：考试中的 closed form solution 指 GBM 标的价格的 exact terminal simulation，不是 Black-Scholes option formula。
- [ ] T11 结论中的部分断言需要用结果支撑，例如参数影响强度排序、二元期权方差缩减幅度、Milstein 整体精度优于 Euler。
- [ ] T12 Notebook 结构还需要整理成最终提交版，建议结构为 Introduction、Model and methods、Implementation、Baseline results、Sensitivity analysis、Antithetic variates、Observations、Conclusion、References。
