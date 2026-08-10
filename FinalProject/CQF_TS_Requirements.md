# CQF Final Project - TS (Pairs Trading) 完整要求

## 来源
- 文档：CQF Final Project Brief - Jan 26 v.4.pdf
- 选题代码：TS
- 负责导师：Richard Diamond
- 截止日期：2026年8月18日 23:59 BST

---

## 总体项目要求

### 提交文件要求
1. **FILE 1**: 报告文件
   - 格式：PDF 或 HTML
   - 命名：`TS [Your Name] REPORT.pdf`（例如：TS John Smith REPORT.pdf）
   - 必须包含页码

2. **FILE 2**: 代码压缩包
   - 格式：ZIP
   - 命名：`TS [Your Name] CODE.zip`（例如：TS John Smith CODE.zip）
   - 包含：转换后的PDF、Python代码和其他代码文件
   - **不要**提交未压缩的 .py, .cpp 文件
   - **不要**使用通用文件名（如 CODE.zip, FinalProject.zip）

3. **必需内容**：
   - 手签的声明（Declaration）
   - 可运行的代码（working code）
   - 缺少任何一项视为项目不完整

### 报告撰写要求

**强制要求**：
- ✅ 不要直接提交 Python Notebook "as is"
- ✅ 移除大量表格/输出的打印
- ✅ 使用 LaTeX 标记编写数学部分
- ✅ 详细分析和比较结果、压力测试
- ✅ 解释所有图表
- ✅ 像量化分析师一样思考：收敛性/准确性/方差和偏差
- ✅ 制作数值技术表格（列出你编码/使用的技术）
- ✅ 必须包含充分的数学模型、数值方法和充分的结论（讨论优缺点、进一步发展）
- ✅ 解释你的图表

**页数**：无固定要求，根据内容需要

---

## TS (Pairs Trading) 具体要求

### 项目标题
**Pairs Trading Strategy Design & Backtest v2026**

### 核心概念
协整关系打开了围绕特殊残差均值回归构建套利的途径。配备平稳性测试（ADF, KPSS, AZ），并通过均值回归扩展 EG/Johansen 程序。

### 必须实现的数值技术
**强制编码要求**：
1. ✅ **矩阵形式的自回归（VAR）** - Matrix form autoregression
2. ✅ **EG 程序（两步法）** - EG Procedure (two steps)
3. ✅ **均值回归评估** - Mean-reversion evaluation (theta, half-life)
4. ✅ **Z 值优化** - Optimizing Z at least iteratively

**鼓励扩展**：
5. ✅ **多元协整（Johansen, VECM）** - Multivariate cointegration
6. ✅ **权重稳健性（自适应估计）** - Robustness of weights by adaptive estimation

### Part I: 配对交易设计 - 预备协整分析

#### 1. VAR 矩阵回归
- 将回归估计重新编码为矩阵形式（作为练习）
- 可以实现向量自回归规格检验：
  - (a) 特征值稳定性检查
  - (b) 用 AIC BIC 测试识别最优滞后阶数 p
- **注意**：这些仅适用于平稳变化之间的结构模型；本项目不预测收益

#### 2. Engle-Granger 程序
- 对每个配对运行 EG 程序
- 可以将数据集分割为多个时期，呈现更动态的结果
- **Step 1**: 使用 lag=1 的增广 DF 检验
- **Step 2**: 编写简短分析，例如分析 EC 项的显著性，它在每个时期是否保持不变

#### 3. "Step 3" - 均值回归评估（扩展）
- 这不是原始 Engle-Granger 中的步骤，是本项目的扩展
- 允许交易设计：
  - 在边界 ±ε = Z·σₑ 入场
  - 在 eₜ 回归到水平 ±ε 时出场

#### 4. Z 值优化
- **不要假设 Z = 1**
- 实现某种优化，或简单的迭代选择：
  - 以递增方式向上和向下改变 Z
  - 生成图表/表格分析每个 Z 水平的交易次数 Nₜᵣₐdₑₛ
- **权衡**：
  - 更宽的边界 → 最高 P&L，低交易次数
  - 但更有风险，因为 eₜ 远超 ±ε
  - 这本身有结构性断裂的潜力：价差转移到新水平

#### 5. 结构性断裂测试
- 更像艺术而非科学 - 大多超出 FP 研究范围
- 有量化工具在协整讲座和终身学习中
- 呈现你的思考：你选择的配对协整关系如何可能断裂

**工具建议**：
- 如果熟悉 R，可以使用专业的多元分析（package urca）识别协整案例
- 总体上，研究应考虑 2-3 个不同的配对

### Part II: 回测

**最低要求**：2 年回测期（取决于协整情况的现实）

#### 6. 系统化回测
- 从配对交易中获取收益（已使用 Z 值）
- 生成：
  - 回撤图
  - 滚动夏普比率
- 讨论你的图表
- **可选**：可以省略关于 S&P500 收益和因子的滚动 beta

#### 7. 交叉验证
- 考虑类似 scikit-learn 的回测：
  - 分割训练/测试子集
  - 其他适用于高频和高频金融时间序列的交叉验证

#### 8. 动态参数重估（重要！）
- 协整的优势：Cₒᵢₙₜ 稳定，价差在 3-6 个月内保持平稳，权重无需更新
- 这是否是现实假设取决于你在协整应用中的经验
- **实验要求**：
  - 重新估计协整关系
  - 例如：**8 个月滚动窗口，每 10-15 天移动一次**
  - 讨论发现

---

## 信号生成和回测要点

### 标的选择建议
- 考虑协整持续的经济和事件驱动原因
- **示例 1**：公司及其潜在收购目标（例如 MAR vs IHG）
- **示例 2**：大宗商品风险期的国家 ETF（例如 EWA vs EWC）
- 超越股票配对：
  - FX 和 FX vs 加密货币
  - UST/UKT 收益率
  - 商品期货
  - VIX 期货

### 配对筛选量化工具
1. 高相关性
2. 残差平稳性测试
3. 多元协整直接检验
- 每种方法都可以改进

### 套利实现
- 通过协整作为配置进行入场/出场决策
- **所有项目应涵盖**：
  - (a) OU 过程拟合的交易信号生成实验和方案开发
  - (b) 风险回测

### 分析问题
- 累积 P&L 是否符合套利交易的预期？
- P&L 由少数还是多次交易产生？
- 半衰期是多少？
- 最大回撤和波动性/VaR 的行为？

---

## 编码要求

### 禁止的做法
- ❌ 不要仅使用 Excel 电子表格函数（不稳健、极慢、不理解底层数值方法）
- ❌ 不要使用 "脚本化解决方案"（仅调用工具箱和库的现成功能，自己编码的数值方法极少或不存在）
- ❌ 不要使用 EViews（这不是编码）

### 应该编码什么？
- ✅ 预期重新编码**对模型核心的数值方法**
- ✅ 在识别这些方法时运用判断
- ✅ 平衡使用库是自己作为量化分析师的自由裁量权
- ✅ 在报告中生成一个小表格，列出你实现/调整的方法
- ✅ 如果对某项技术使用现成函数/借用代码，请说明并描述该代码/标准库中实现的数值方法的局限性

### 代码质量要求
- ✅ 代码必须经过彻底测试和良好记录
- ✅ 每个函数必须有描述
- ✅ 必须使用注释
- ✅ 提供如何运行代码的说明
- ✅ 开发自己的测试用例、合理性检查和验证
- ✅ 在真实数据上实现模型时观察到不规则性是正常的
- ✅ 如有疑问，在项目报告中反思该问题

### 编程语言选择
- Python、R、Matlab、C++、Java、C# 都可以
- 选择具有适当优势和设施来实现主题（定价模型）的编程环境
- 运用量化分析师的判断：哪种语言有库可以让你编码更快、验证更容易

---

## 关键资源

### 推荐的 Advanced Electives
- Energy Trading
- R for Data Science and Machine Learning

### 阅读清单（Reading List: Cointegrated Pairs）
1. **Cointegration Lecture** - 介绍多个平稳性测试
   - ADF 简单但要小心软件的临界值
   - Critical Values for Cointegration Tests by J MacKinnon (2010)
   - Mathematics of Dickey Fuller Test 附加说明

2. **Tutorial: Nonstationarity** - 有用的 R notebook

3. **Tutorial: Cointegration in Rates - Multivariate Cointegration** - R notebook (2023)

4. **Efficient Pair Selection for Pair-Trading Strategies** by P. McSharry
   - 应用 ADF 测试筛选和搜索市场中的协整配对

5. **Explaining Cointegration Analysis: Part I** by D. Hendry & K. Juselius
   - 可以代替计量经济学教科书阅读
   - Part II 涉及 VECM 细节和确定性项

6. **Learning and Trusting Cointegration in Statistical Arbitrage** by R. Diamond (2014), WILMOTT
   - 直接查看 OU 过程数学附录
   - 交易次数附录

### Workshop & Tutorials
- **Workshop**: 11/07/2026, 13:00-16:30 BST (Final Project Workshop II - TS)
- **Tutorial**: 20/07/2026, 18:00-19:30 BST (Final Project Tutorial III - TS, LV & AL)

---

## 评分重点

**分数主要取决于**：
1. ✅ 数值技术的编码
2. ✅ 如何探索和测试量化模型的呈现
3. ✅ 报告（PDF 或 HTML）

**注意事项**：
- 所有项目都会检查原创性
- 保留在授予资格前进行口试（viva voce）的选择权

---

## 总结检查清单

### 必须包含的核心内容
- [ ] 矩阵形式 VAR 回归
- [ ] EG 两步法协整检验（自主编码）
- [ ] ADF 平稳性检验
- [ ] OU 过程均值回归评估（theta, 半衰期）
- [ ] Z 值阈值迭代优化
- [ ] 完整回测（至少 2 年）
- [ ] 滚动窗口动态参数重估（8个月窗口，10-15天滚动）
- [ ] 回撤分析
- [ ] 滚动夏普比率
- [ ] 结构性断裂讨论

### 鼓励包含的扩展内容
- [ ] Johansen 多元协整检验
- [ ] VECM 向量误差修正模型
- [ ] 自适应权重估计
- [ ] 2-3 个不同配对的比较研究
- [ ] 交叉验证方法

### 报告质量要求
- [ ] 数学公式（LaTeX）
- [ ] 充分的图表和解释
- [ ] 数值技术汇总表
- [ ] 优缺点讨论
- [ ] 进一步发展建议
- [ ] 结论部分

### 代码质量要求
- [ ] 可运行的完整代码
- [ ] 详细注释
- [ ] 函数说明
- [ ] 运行指南
- [ ] 测试用例

---

**文档创建时间**: 2026-08-10  
**提取自**: CQF Final Project Brief - Jan 26 v.4.pdf
