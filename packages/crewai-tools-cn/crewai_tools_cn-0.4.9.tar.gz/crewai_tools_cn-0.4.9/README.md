<div align="center">

![crewAI 的 Logo，两个人在一艘船上划船](./assets/crewai_logo.png)

<div align="left">

# **crewAI 工具**
本文档全面介绍了如何为 [crewAI](https://github.com/joaomdmoura/crewai) 代理设置复杂的工具，方便创建定制工具以增强您的 AI 解决方案。

在 CrewAI 代理领域，工具对于增强功能至关重要。本指南概述了为您的代理配备一系列现成工具的步骤，以及创建您自己的工具的方法。

</div>

<h3>

[主页](https://www.crewai.io/) | [文档](https://docs.crewai.com/) | [与文档聊天](https://chatg.pt/DWjSBZn) | [示例](https://github.com/joaomdmoura/crewai-examples) | [Discord](https://discord.com/invite/X4JWnZnxPb)

</h3>

</div>

## 目录

- [创建您的工具](#创建您的工具)
	- [继承 `BaseTool`](#继承-basetool)
	- [使用 `tool` 装饰器](#使用-tool-装饰器)
- [贡献指南](#贡献指南)
- [开发设置](#开发设置)

## 创建您的工具

工具始终应返回字符串，因为它们旨在供代理用于生成响应。

创建 crewAI 代理工具的方法有三种：
- [继承 `BaseTool`](#继承-basetool)
- [使用 `tool` 装饰器](#使用-tool-装饰器)

### 继承 `BaseTool`

```python
from crewai_tools_cn import BaseTool

class MyCustomTool(BaseTool):
    name: str = "我的工具名称"
    description: str = "对该工具用途的清晰描述，您的代理将需要此信息才能使用它。"

    def _run(self, argument: str) -> str:
        # 实现代码在此处
        pass
```

定义一个继承自 `BaseTool` 的新类，指定 `name`、`description` 和用于操作逻辑的 `_run` 方法。


### 使用 `tool` 装饰器

对于更简单的方法，请直接使用所需的属性和功能逻辑创建 `Tool` 对象。

```python
from crewai_tools_cn import tool
@tool("我的工具名称")
def my_tool(question: str) -> str:
    """对该工具用途的清晰描述，您的代理将需要此信息才能使用它。"""
    # 函数逻辑在此处
```

`tool` 装饰器简化了流程，以最小的开销将函数转换为工具。

## 贡献指南

我们热烈欢迎您为丰富此工具集做出贡献。要做出贡献：

1. **Fork 仓库：**首先将仓库 fork 到您的 GitHub 帐户。
2. **功能分支：**在您的 fork 中为功能或改进创建一个新分支。
3. **实现您的功能：**将您的贡献添加到新分支中。
4. **拉取请求：**从您的功能分支向主仓库提交拉取请求。

我们非常感谢您的贡献，这将有助于增强此项目。

## **开发设置**

**安装依赖项：**

```bash
poetry install
```

**激活虚拟环境：**

```bash
poetry shell
```

**设置预提交钩子：**

```bash
pre-commit install
```

**运行测试：**

```bash
poetry run pytest
```

**静态类型检查：**

```bash
poetry run pyright
```

**打包：**

```bash
poetry build
```

**本地安装：**

```bash
pip install dist/*.tar.gz
```

感谢您有兴趣通过高级工具增强 AI 代理的功能。您的贡献将产生重大影响。
