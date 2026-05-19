## Exam3 维护说明 - 2026-05-19

### 原始需求

`Assignments` 目录是 CQF 第三次考试题目：

- `Exam3_Jan2026_Original.pdf`：考试题

`Resources` 目录是 CQF 第三次考试对应课程资料：
- `14_gradientboosting_ks.ipynb`：与考试题非常吻合，是主要参考（尤其第三题）
- `spy.csv`：是 14_gradientboosting_ks.ipynb 使用的数据

目标是阅读题目和课程资料，并将完整答案维护在 `Answer.ipynb` 中（三道题的答案分别存入三个 Answer 文件）。

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