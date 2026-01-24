# CQFLearning
CQF 学习

## 环境设置

以下命令用于设置 Python 开发环境：

```bash
# 创建 Python 虚拟环境，名为 venv
python3 -m venv venv

# 激活虚拟环境（macOS/Linux）
source venv/bin/activate

# 以可编辑模式安装项目包，方便开发时修改代码
pip install -e .

# 安装项目的开发依赖（如测试工具、代码检查工具等）
pip install -e ".[dev]"
```

**命令说明：**
- `python3 -m venv venv`：创建一个独立的 Python 虚拟环境，避免与系统 Python 环境冲突
- `source venv/bin/activate`：激活虚拟环境，之后的 pip 安装都会在这个环境中进行
- `pip install -e .`：以可编辑（editable）模式安装当前项目，代码修改后无需重新安装
- `pip install -e ".[dev]"`：安装项目的开发依赖包，用于开发、测试和调试