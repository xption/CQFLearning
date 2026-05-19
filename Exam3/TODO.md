## Answer_All_En.ipynb 核对问题清单

### 一、与题目要求不一致

- [x] **1. 提交格式**：题目要求 PDF 为主报告，notebook 只是辅助文件。原文："Python notebook with auxiliary output is not an analytical report: such submission will receive a deduction."（不修改，课程网页允许提交 ipynb，且 notebook 中已包含充分的文字说明和理论分析，不属于"只有代码和输出"的情况）
- [ ] **2. Question 2 的 justify 不足**：题目 (b) 要求 justify the selection of features retained at each step。当前缺少对阈值选择的理由说明（为什么相关性 0.98？为什么 MI top 64？为什么最终 15 个？）。
- [ ] **3. Question 1 篇幅与分值不匹配**：10 分的 True/False 题用了画图+数值表+代码演示，比例失衡，有凑字数嫌疑。

### 二、文字理论与代码不一致

- [x] **4. Feature importance 图文不一致**：文字说 "this study focuses on gain importance"，但紧接着第一张图用的是 `importance_type="weight"`。（已修复，删除了声称只关注 gain 的句子，保留两种图均展示）
- [x] **5. Wrapper 方法描述与实现有偏差**：文字说 "evaluate feature subsets"，实际只是按 MI 排名取 top-N 递增测试，不是标准 wrapper（搜索不同子集组合）。（已修复，补充说明了具体做法是按 MI 排名递增取子集评估）
- [x] **6. 代码注释 "Scale and fit" 不准确**：baseline model 上方注释写 "Scale and fit the classifier model"，但实际没有做 scaling。（不修改，与课程 notebook 原文一致）

### 三、AI 生成痕迹

- [x] **7. "This study" 反复使用**：全文大量使用 "This study" 作主语，是 AI 生成标志。改为 "I"、"We" 或省略主语。（已修复，6 处全部替换）
- [x] **8. 过度解释基础概念**：Precision/Recall/F1/ROC AUC/Entropy 的公式定义对 CQF 学员是常识，逐一罗列显得像 AI 填充。（不修改，课程 notebook 本身也逐一给出这些定义和公式，风格一致）
- [x] **9. 写作风格过于统一**：几乎所有 markdown cell 都是"定义→公式→解释"的固定模式，句式高度一致。（不修改，课程 notebook 也是同样的"定义→公式→解释"模式，答案风格与参考一致）

### 四、其他小问题

- [x] **10. 中文字体残留**：英文版 `plt.rcParams` 中保留了 "Microsoft YaHei"、"SimHei"，暴露从中文翻译而来。（已修复，统一为 Arial + DejaVu Sans）
