## Exam3 维护说明 - 2026-05-19

### 原始需求

`Assignments` 目录是 CQF 第三次考试题目：

- `Exam3_Jan2026_Original.pdf`：考试题

`Resources` 目录是 CQF 第三次考试对应课程资料：
- `14_gradientboosting_ks.ipynb`：与考试题非常吻合，是主要参考（尤其第三题）
- `spy.csv`：是 14_gradientboosting_ks.ipynb 使用的数据

目标是阅读题目和课程资料，先将三道题的答案分别维护在独立 Answer 文件中，再合并为完整答案文件，并在确认中文版本后生成英文版本。

### 题目要求


### 特别约定

1. 约定 1

14_gradientboosting_ks.ipynb 中使用了以下两项服务：
- google.colab：用于存储 spy.csv 数据
- wandb：用于存储模型搭建的数据，以及用于调优模型

这两项服务我均不需要，数据文件存储在本地，搭建模型过程中的数据和调优模型均在本地进行。

2. 约定 2

我的模型的测试数据使用沪深 300 指数数据，存储在 CSI300_2005_2026.csv。

3. 约定 3

虽然题目是英文，但是你与我沟通以及答案全部用中文，我会在全部完成之后确认无误再让你帮我翻译为英文。

4. 约定 4
在 14_gradientboosting_ks.ipynb 中的 Section 2: The workflow 有 7 个 Step 的表格，这个表格很重要，原封不动的拷贝到我的 Answer 3 中合适位置。

Answer 3 的结构，需要与 14_gradientboosting_ks.ipynb 一致，例如：
- Install Packages
- Import Libraries
- Section 1: Experiment Tracking
- Section 2: The workflow

14_gradientboosting_ks.ipynb 的内容与考试内容高度一致，只是我使用沪深 300 数据，并且不使用 google.colab 和 wandb 两个服务，你完全可以照葫芦画瓢，严格按照 14_gradientboosting_ks.ipynb 的内容结构解答。

### 本次完成情况

本次已经完成 CQF Exam3 答案的主要撰写、合并、英文翻译和最终格式调整：

- 已阅读并参考考试题目、`README.md` 约定以及课程 notebook `14_gradientboosting_ks.ipynb`。
- 已先形成三道题的独立答案 notebook：`Answer1.ipynb`、`Answer2.ipynb`、`Answer3.ipynb`。
- 已将三道题合并为中文完整答案：`Answer_All.ipynb`。
- 已将中文完整答案翻译为英文完整答案：`Answer_All_En.ipynb`。
- 已修复 notebook 中曾出现的连续问号显示问题，避免中文编码异常。
- 已修复英文版本中的 KaTeX parse error，确保数学公式可正常渲染。
- 已将 `## Install Packages` 移动到合并答案开头，使第一题、第二题、第三题共用同一安装环境准备步骤。
- 已按要求在安装代码中直接使用 `pip install`，显式安装阅卷环境可能缺失的第三方库。

### 最终文件说明

- `Answer1.ipynb`：第一题中文答案。
- `Answer2.ipynb`：第二题中文答案，包含特征构造、分析和筛选思路。
- `Answer3.ipynb`：第三题中文答案，按 `14_gradientboosting_ks.ipynb` 的章节结构组织，并使用沪深 300 数据完成建模与回测。
- `Answer_All.ipynb`：三道题合并后的中文完整答案，是中文提交前的主文件。
- `Answer_All_En.ipynb`：三道题合并后的英文完整答案，是英文提交版本。
- `build_answer_notebooks.py`：用于生成或维护答案 notebook 的辅助脚本，当前仍保留。

### 答案结构与实现口径

第三题的章节结构需要贴近 `14_gradientboosting_ks.ipynb`，尤其保留以下内容顺序和风格：

- `Install Packages`
- `Import Libraries`
- `Section 1: Experiment Tracking`
- `Section 2: The workflow`
- `Section 2: The workflow` 中 7 个 Step 的 workflow 表格需原封不动拷贝到 Answer 3 的合适位置。

但“严格参考课程 notebook”主要指章节组织、答题逻辑和机器学习 workflow，而不是机械复制课程 notebook 的全部特征集和参数。最终方案已经确认：

- 数据使用本地 `CSI300_2005_2026.csv`。
- 不使用 `google.colab`。
- 不使用 `wandb`。
- 答案正文中避免出现“按照 README”“不使用 W&B”“参考 notebook”这类内部说明或元叙述。
- 特征集和模型设置可以根据沪深 300 数据实际表现进行优化。

### 第三题建模方案摘要

第三题最终采用更丰富的沪深 300 特征集，而不是只使用课程 notebook 中较小的示例特征集。候选特征包括：

- 收益率特征
- 波动率特征
- 移动均线偏离特征
- 成交量 z-score
- rolling min/max return
- K 线结构特征
- RSI
- MACD
- ATR
- day-of-week

目标变量定义为下一交易日对数收益率是否超过 `0.0015`，即是否出现有效上涨。模型流程保留课程 notebook 的主要思路，包括：

- `train_test_split(..., test_size=0.2, shuffle=False)`
- `compute_sample_weight`
- `TimeSeriesSplit`
- `RandomizedSearchCV`
- `XGBClassifier`

最终 Answer 3 中保留的关键结果大致为：

- Test ROC AUC：约 `0.5693`
- Test balanced accuracy：约 `0.5557`
- Test F1：约 `0.4939`
- Strategy total return：约 `13.08%`
- Buy & hold total return：约 `1.97%`
- Strategy max drawdown：约 `-9.13%`
- Buy & hold max drawdown：约 `-26.63%`

### 已处理的问题

- 曾发现三个答案文档中出现连续问号，判断为中文编码或 notebook 写入编码问题，后续已修复。
- 曾发现 Answer 3 初版过度使用内部说明性文字，已改为更像正式考试答案的表达。
- 曾发现 Answer 3 初版未充分贴近 `14_gradientboosting_ks.ipynb` 的实现风格，后续补入课程 notebook 中的关键 workflow、训练/验证方式和样本权重处理。
- 曾发现完全照搬课程 notebook 的较小特征集后，回测表现变差；最终确认应保留课程 notebook 的结构和 workflow，但特征工程与模型设置可根据 CSI300 数据优化。
- 曾将三个答案合并为 `Answer_All.ipynb`，并仅调整章节编号，不改动主要内容。
- 曾比对课程 notebook 的理论说明，补齐部分文字解释和公式，例如 target/label definition 等。
- 曾删除一次性修改脚本 `augment_answer_all_theory.py`，避免保留不再使用的临时文件。
- 曾生成英文版 `Answer_All_En.ipynb`，并修复其中的公式渲染问题。

### 后续维护注意事项

- 如果继续修改答案，应优先维护 `Answer_All.ipynb` 和 `Answer_All_En.ipynb` 两个最终合并文件。
- 如果需要重新生成独立答案文件，应确认 `build_answer_notebooks.py` 与当前最终 notebook 内容是否仍一致。
- 不要在正式答案正文中写入面向协作过程的内部备注。
- 修改英文版时，需要重新检查是否存在中文残留、连续问号和 KaTeX parse error。
- 修改安装依赖时，应同步更新合并 notebook 开头的 `## Install Packages` 代码单元。
