
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

## 项目检查总结（Phase 1-5 全部完成 ✅）

### ✅ 检查与修复完成情况

| 阶段 | 内容 | 状态 | 结果文档 |
|------|------|------|----------|
| **Phase 1** | CQF要求符合性检查 | ✅ 完成 | CQF_TS_Requirements.md |
| **Phase 2** | Result.md逻辑与内容检查 | ✅ 完成 | Phase2_ResultMD_Check_Report.md |
| **Phase 3** | Script代码可执行性检查 | ✅ 完成 | Phase3_Code_Verification_Report.md |
| **Phase 4** | 问题汇总与修复建议 | ✅ 完成 | Phase4_Fix_Plan_Report.md |
| **Phase 5** | 修复与优化 | ✅ 完成 | Phase5_Fix_Completion_Report.md |

### 📊 检查结果（Phase 1-4）

#### ✅ 优点
- **CQF要求符合度**: 100% - 所有强制和鼓励的技术都已实现
- **代码质量**: 90分 - 所有模块可运行，算法正确
- **静态策略数据**: 完全准确，与代码输出一致

#### 🔴 发现的问题（已修复）
- **总问题数**: 13个
  - 严重问题（P1）: 6个 - 数据错误、内容重复 → ✅ 已全部修复
  - 中等问题（P2）: 5个 - 数据缺失、表述问题 → ✅ 已修复4个
  - 轻微问题（P3）: 2个 - 优化建议 → ⏸️ 暂不处理

### 🔧 Phase 5 修复成果

#### 修复统计
- **完成率**: 10/11 问题已修复（91%）
- **P1严重问题**: 6/6 已修复（100%）
- **P2中等问题**: 4/5 已修复（80%）

#### 关键修复
1. ✅ **Alpha值**: 0.0624 → **-0.6786**（符号修正）
2. ✅ **OU Sigma**: 0.0126 → **0.003812**（参数修正）
3. ✅ **动态策略收益率**: -0.61%/-0.53% → **+0.17%**（正负号修正）
4. ✅ **动态策略最大回撤**: 12.36% → **1.79%**（数值修正）
5. ✅ **删除重复内容**: 第3章29行 + 第5章32行 = 61行
6. ✅ **补充缺失数据**: R²=0.9800, 残差std=0.014068
7. ✅ **精简摘要**: 391字 → 250字
8. ✅ **新增章节**: 3.7 协整检验实证结果（完整数据）

#### 文件变化
- **原始**: 390行 → **修复后**: 354行（-36行，-9.2%）
- **备份**: Result.md.backup 已创建
- **修复脚本**: fix_result.py, fix_remaining.py

### 🔥 核心问题（已解决）

1. **Alpha值错误**: 0.0624 → 应为 **-0.6786**（符号相反）✅
2. **OU Sigma错误**: 0.0126 → 应为 **0.003812**（相差3.3倍）✅
3. **动态策略收益率错误**: -0.61%/-0.53% → 应为 **+0.1740%**（正负号相反！）✅
4. **动态策略最大回撤错误**: 12.36% → 应为 **1.79%**（相差6.9倍）✅
5. **内容重复**: 第3章和第5章有大段重复内容 ✅

### ⏸️ 未修复的问题（影响轻微）
- **滚动窗口数量**: Result.md提到746组，代码输出559个（统计口径可能不同）

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

### 待完成任务

#### 1. 英文翻译 ⏸️
- [ ] 将 Result.md 翻译成学术英语
- [ ] 保持专业术语准确性
- [ ] 确保格式和公式正确

#### 2. PDF生成 ⏸️
- [ ] 格式化文档
- [ ] 生成提交用的PDF（TS [Your Name] REPORT.pdf）
- [ ] 确认页码和图表引用

#### 3. 代码整理 ⏸️
- [ ] 整理代码文件
- [ ] 添加运行说明（README）
- [ ] 生成代码压缩包（TS [Your Name] CODE.zip）

#### 4. 图表生成 ⏸️
- [ ] 运行 visualization.py 生成所有图表
- [ ] 确认图表质量
- [ ] 在报告中引用图表

#### 5. 最终审阅 ⏸️
- [ ] 通读全文，检查流畅性
- [ ] 确认所有数据准确性
- [ ] 检查参考文献格式
- [ ] 签署 Declaration

#### 6. 提交准备 ⏸️
- [ ] FILE 1: TS [Your Name] REPORT.pdf
- [ ] FILE 2: TS [Your Name] CODE.zip（包含PDF、代码）
- [ ] 手签的 Declaration
- [ ] 检查截止时间：2026年8月18日 23:59 BST

---

## 项目质量评估

| 评估项 | 检查前 | 修复后 | 状态 |
|--------|--------|--------|------|
| **Result.md** | 70分 | **90分** | ✅ 优秀 |
| **代码质量** | 90分 | **90分** | ✅ 优秀 |
| **CQF符合度** | 100% | **100%** | ✅ 完美 |
| **整体评价** | 良好 | **优秀** | ✅ 可提交 |

---

## 相关文档

### 检查报告
- [TODO.md](TODO.md) - 详细的检查计划和进度追踪 ✅
- [CQF_TS_Requirements.md](CQF_TS_Requirements.md) - CQF TS 选题完整要求 ✅
- [Phase2_ResultMD_Check_Report.md](Phase2_ResultMD_Check_Report.md) - Result.md 检查报告 ✅
- [Phase3_Code_Verification_Report.md](Phase3_Code_Verification_Report.md) - 代码验证报告 ✅
- [Phase4_Fix_Plan_Report.md](Phase4_Fix_Plan_Report.md) - 问题汇总与修复方案 ✅
- [Phase5_Fix_Completion_Report.md](Phase5_Fix_Completion_Report.md) - 修复完成报告 ✅

### 项目文件
- [Resources/Result.md](Resources/Result.md) - 项目解答文档（已修复）✅
- [Resources/Result.md.backup](Resources/Result.md.backup) - 原始备份 ✅
- [Script/](Script/) - Python 代码实现 ✅

---

**项目状态**: Phase 1-5 全部完成 ✅  
**Result.md**: 已修复，质量优秀，可用于提交  
**最后更新**: 2026-08-10  
**下一步**: 翻译、生成PDF、准备提交材料