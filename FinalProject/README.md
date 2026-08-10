
# CQF Final Project - TS (Pairs Trading)

## 项目概述

本项目是 CQF（Certificate in Quantitative Finance）最终考试项目，选题为 **TS（配对交易 Pairs Trading）**。

**研究标的**：螺纹钢期货（RB）、热轧卷板期货（HC）  
**样本区间**：2023.01.03 – 2025.12.31（727个交易日）  
**研究主题**：基于协整与OU均值回归的黑色系期货配对交易策略

---

## 目录结构

```
FinalProject/
├── Assignments/              # CQF 考试要求文档
│   ├── CQF Final Project Brief - Jan 26 v.4.pdf
│   └── Jan 26 Final Project Declaration.pdf
│
├── Resources/                # 数据和解答文档
│   ├── data.py              # 获取期货日K线数据的脚本
│   ├── rb.csv               # 螺纹钢期货完整日K线数据
│   ├── rb-2023-2025.csv     # 螺纹钢期货 2023-2025 数据
│   ├── hc.csv               # 热轧板期货完整日K线数据
│   ├── hc-2023-2025.csv     # 热轧板期货 2023-2025 数据
│   └── Result.md            # 📝 项目解答文档（中文）
│
├── Script/                   # Python 代码实现
│   ├── data_loader.py       # 数据加载和预处理
│   ├── cointegration.py     # 协整检验（EG/Johansen/VECM）
│   ├── ou_process.py        # OU过程拟合（MLE）
│   ├── strategy.py          # 交易策略和阈值优化
│   ├── backtest.py          # 回测引擎
│   ├── rolling.py           # 滚动窗口动态协整分析
│   ├── visualization.py     # 可视化模块
│   ├── main.py              # 主执行脚本
│   ├── data/                # 数据文件
│   └── README.md            # 代码说明
│
├── TODO.md                   # 📋 检查计划和进度追踪
├── CQF_TS_Requirements.md   # 📄 CQF TS 选题完整要求
├── Phase2_ResultMD_Check_Report.md      # Phase 2 检查报告
├── Phase3_Code_Verification_Report.md   # Phase 3 验证报告
└── Phase4_Fix_Plan_Report.md            # Phase 4 修复方案
```

---

## 项目检查总结（Phase 1-4 完成）

### ✅ 检查完成情况

| 阶段 | 内容 | 状态 | 结果文档 |
|------|------|------|----------|
| **Phase 1** | CQF要求符合性检查 | ✅ 完成 | CQF_TS_Requirements.md |
| **Phase 2** | Result.md逻辑与内容检查 | ✅ 完成 | Phase2_ResultMD_Check_Report.md |
| **Phase 3** | Script代码可执行性检查 | ✅ 完成 | Phase3_Code_Verification_Report.md |
| **Phase 4** | 问题汇总与修复建议 | ✅ 完成 | Phase4_Fix_Plan_Report.md |
| **Phase 5** | 修复与优化 | ⏸️ 待开始 | - |

### 📊 检查结果

#### ✅ 优点
- **CQF要求符合度**: 100% - 所有强制和鼓励的技术都已实现
- **代码质量**: 90分 - 所有模块可运行，算法正确
- **静态策略数据**: 完全准确，与代码输出一致

#### 🔴 发现的问题
- **总问题数**: 13个
  - 严重问题（P1）: 6个 - 数据错误、内容重复
  - 中等问题（P2）: 5个 - 数据缺失、表述问题
  - 轻微问题（P3）: 2个 - 优化建议

### 🔥 核心问题

1. **Alpha值错误**: 0.0624 → 应为 **-0.6786**（符号相反）
2. **OU Sigma错误**: 0.0126 → 应为 **0.003812**（相差3.3倍）
3. **动态策略收益率错误**: -0.61%/-0.53% → 应为 **+0.1740%**（正负号相反！）
4. **动态策略最大回撤错误**: 12.36% → 应为 **1.79%**（相差6.9倍）
5. **内容重复**: 第3章和第5章有大段重复内容

---

## 实现的技术要点

### 强制技术（CQF要求）✅
- ✅ 矩阵形式 VAR 向量自回归
- ✅ EG 两步法协整检验（自主编码）
- ✅ 均值回归评估（theta, 半衰期）
- ✅ Z-score 阈值优化（网格遍历）

### 扩展技术（鼓励实现）✅
- ✅ Johansen 多元协整检验
- ✅ VECM 向量误差修正模型
- ✅ OU 过程 MLE 拟合
- ✅ 滚动窗口动态参数重估（8个月窗口，10日滚动）
- ✅ 协整结构断裂识别

---

## 核心研究结果

### 静态策略（准确）
- **对冲比率 β**: 1.078
- **半衰期**: 18.2天
- **最优阈值**: 入场 2.4σ, 出场 0.8σ
- **总收益率**: 4.79%
- **夏普比率**: 0.30
- **最大回撤**: 7.45%
- **交易次数**: 4次
- **胜率**: 100%

### 动态策略（需修正）
- **总收益率**: +0.17% (Result.md错误写为负值)
- **夏普比率**: 0.028
- **最大回撤**: 1.79% (Result.md错误写为12.36%)
- **结论**: 虽为正收益，但显著弱于静态策略

---

## 下一步工作

### Phase 5: 执行修复（待开始）

**推荐方案**: 方案B（标准修复）
- 修复所有 P1 严重问题（6个）
- 修复所有 P2 中等问题（5个）
- 预计时间: 3.5-5 小时

**修复清单**:
1. 修正 Alpha、OU Sigma、动态策略数据
2. 删除重复内容
3. 补充缺失数据（R²、残差std等）
4. 精简摘要
5. 生成 Result_Fixed.md

### 后续任务
- [ ] 翻译成英文
- [ ] 生成 PDF 文件
- [ ] 准备提交材料

---

## 提交要求

**截止日期**: 2026年8月18日 23:59 BST

**提交文件**:
1. **TS [Your Name] REPORT.pdf** - 项目报告（PDF）
2. **TS [Your Name] CODE.zip** - 代码压缩包

**必需内容**:
- ✅ 手签的声明（Declaration）
- ✅ 可运行的代码（working code）
- ✅ 充分的数学模型和数值方法
- ✅ 详细的分析和结论

---

## 相关文档

- [TODO.md](TODO.md) - 详细的检查计划和进度
- [CQF_TS_Requirements.md](CQF_TS_Requirements.md) - CQF TS 选题完整要求
- [Phase2_ResultMD_Check_Report.md](Phase2_ResultMD_Check_Report.md) - Result.md 检查报告
- [Phase3_Code_Verification_Report.md](Phase3_Code_Verification_Report.md) - 代码验证报告
- [Phase4_Fix_Plan_Report.md](Phase4_Fix_Plan_Report.md) - 问题汇总与修复方案

---

**项目状态**: 检查完成（Phase 1-4 ✅），待修复（Phase 5 ⏸️）  
**最后更新**: 2026-08-10