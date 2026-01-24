# CLAUDE.md - AI 助手项目指南

## 项目概述

这是一个 **CQF (Certificate in Quantitative Finance) 证书培训考试**的学习项目。项目专注于量化金融领域的学习和实践。

**项目关键信息：**
- **项目名称**: CQFLearning
- **版本**: 0.1.0
- **Python 版本要求**: >= 3.11
- **许可证**: MIT
- **主要用途**: CQF 课程学习、量化金融研究、金融数据分析

## 项目结构

```
CQFLearning/
├── app/                   # 主应用代码目录
│   ├── __init__.py        # 包初始化文件
│   └── run.py             # 主运行入口
├── venv/                  # Python 虚拟环境
├── pyproject.toml         # 项目配置和依赖管理
├── README.md              # 项目说明文档
├── CLAUDE.md              # AI 助手指南（本文件）
├── LICENSE                # MIT 许可证
└── .gitignore             # Git 忽略文件配置
```

## 技术栈

### 核心依赖

**数据处理与分析：**
- `pandas` (>=2.0.0) - 数据分析和处理
- `numpy` (>=1.24.0) - 数值计算
- `pyarrow` (>=21.0.0) - 高性能数据格式
- `fastparquet` (>=2024.11.0) - Parquet 文件支持

**金融数据与技术分析：**
- `yfinance` (>=0.2.0) - Yahoo Finance 数据获取
- `ta` (>=0.10.0) - 技术分析指标库

**可视化：**
- `matplotlib` (>=3.7.0) - 基础绘图
- `seaborn` (>=0.12.0) - 统计可视化

**Web 应用：**
- `flask` (>=3.1.2) - Web 框架
- `flask-cors` (>=6.0.1) - 跨域资源共享
- `gunicorn` (>=23.0.0) - WSGI HTTP 服务器

**数据库：**
- `pymysql` (>=1.1.0) - MySQL 数据库驱动
- `sqlalchemy` (>=2.0.0) - ORM 框架
- `redis` (>=4.5.0) - Redis 缓存

**任务调度与工具：**
- `apscheduler` (>=3.11.0) - 定时任务调度
- `loguru` (>=0.7.0) - 日志记录
- `python-dotenv` (>=1.0.0) - 环境变量管理
- `pyyaml` (>=6.0) - YAML 配置文件
- `pyhumps` (>=3.8.0) - 命名风格转换

### 开发工具（dev 依赖）

- `pytest` - 单元测试框架
- `pytest-cov` - 测试覆盖率
- `black` - 代码格式化
- `flake8` - 代码风格检查
- `mypy` - 静态类型检查
- `isort` - import 语句排序
- `autoflake` - 自动删除未使用的导入

## 开发环境设置

### 1. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows
```

### 2. 安装依赖

```bash
# 安装基础依赖
pip install -e .

# 安装开发依赖
pip install -e ".[dev]"
```

### 3. 运行应用

```bash
# 直接运行 Python 模块
python3 -m app.run

# 或使用 Makefile
make run
```

## 代码风格指南

### Black 配置
- **行长度**: 999 字符（非常宽松，适合复杂的金融公式）
- **目标版本**: Python 3.13
- 自动格式化命令: `black app/`

### isort 配置
- **配置文件**: black 兼容模式
- **行长度**: 999 字符
- **已知第一方包**: app
- 排序命令: `isort app/`

### mypy 配置
- **Python 版本**: 3.13
- **严格模式**: 启用未类型化定义检查
- 类型检查命令: `mypy app/`

## 常见开发任务

### 代码质量检查

```bash
# 格式化代码
black app/

# 排序 imports
isort app/

# 代码风格检查
flake8 app/

# 类型检查
mypy app/

# 删除未使用的导入
autoflake --remove-all-unused-imports --in-place --recursive app/
```

### 测试

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=app --cov-report=html

# 运行特定测试文件
pytest tests/test_specific.py
```

## AI 助手工作指南

### 重要注意事项

1. **金融领域特性**
   - 这是量化金融项目，涉及金融数据分析和交易策略
   - 代码可能包含复杂的数学公式和金融模型
   - 注意数值精度和浮点数计算问题

2. **数据安全**
   - 不要在代码中硬编码 API 密钥、数据库密码等敏感信息
   - 使用 `.env` 文件和 `python-dotenv` 管理环境变量
   - 确保 `.env` 文件在 `.gitignore` 中

3. **代码风格**
   - 行长度限制为 999 字符（非常宽松）
   - 使用 black 进行代码格式化
   - 保持类型注解的完整性（mypy 检查）

4. **测试要求**
   - 为新功能编写单元测试
   - 确保测试覆盖率合理
   - 金融计算函数必须有测试验证

### 修改代码前的检查清单

- [ ] 阅读相关的现有代码
- [ ] 理解金融业务逻辑和数学模型
- [ ] 确认修改不会影响数值计算精度
- [ ] 检查是否需要更新测试
- [ ] 验证代码符合项目风格指南

### 添加新功能的步骤

1. **理解需求**: 明确功能的金融业务含义
2. **设计方案**: 考虑数据流、计算逻辑、性能影响
3. **编写代码**: 遵循项目代码风格
4. **添加测试**: 编写单元测试，特别是边界情况
5. **文档更新**: 更新相关文档和注释
6. **代码检查**: 运行 black, isort, flake8, mypy

## 项目特定知识

### 技术架构

项目采用以下技术架构：
- 使用 Flask 提供 Web API（如需要）
- 使用 APScheduler 进行定时任务调度
- 支持 MySQL 数据持久化
- 使用 Redis 进行缓存和消息队列

### 数据处理流程

1. **数据获取**: 使用 yfinance 获取金融市场数据
2. **数据存储**: Parquet 格式存储（高性能）+ MySQL（持久化）
3. **技术分析**: 使用 ta 库计算技术指标
4. **可视化**: matplotlib/seaborn 生成图表

## 常见问题

### Q: 为什么行长度设置为 999？
A: 金融公式和计算逻辑往往很长，过短的行长度会影响可读性。

### Q: 如何处理金融数据的时区问题？
A: 使用 pandas 的时区感知功能，确保所有时间戳都有明确的时区信息。

### Q: 如何确保数值计算的精度？
A: 对于货币计算，考虑使用 `decimal.Decimal`；对于百分比，注意浮点数精度问题。

## 相关资源

- **CQF 官网**: https://www.cqf.com/
- **Python 金融分析**: https://www.python.org/
- **Pandas 文档**: https://pandas.pydata.org/
- **TA-Lib 文档**: https://ta-lib.org/

## 更新日志

- 2026-01-24: 创建 CLAUDE.md 文件，添加项目指南
