<div align="center">

![Logo of Maxwell, a brain with ](./assets/brain_logo.png)

<div align="left">

# **Maxwell Tools**
This document provides a comprehensive guide for setting up sophisticated tools for [Maxwell](https://github.com/joaomdmoura/Maxwell) agents, facilitating the creation of bespoke tooling to empower your AI solutions.

In the realm of Maxwell agents, tools are pivotal for enhancing functionality. This guide outlines the steps to equip your agents with an arsenal of ready-to-use tools and the methodology to craft your own.

</div>

<h3>

[Homepage](https://arvos.ai/) | [Documentation](https://docs.arvos.ai/maxwell) | [Chat with Docs]() | [Examples](https://github.com/ARVOS.AI/maxwell-examples) | [Discord](https://discord.com/invite/X4JWnZnxPb)

</h3>

</div>

## Table of contents

- [Creating Your Tools](#creating-your-tools)
	- [Subclassing `BaseTool`](#subclassing-basetool)
	- [Utilizing the `tool` Decorator](#utilizing-the-tool-decorator)
- [Contribution Guidelines](#contribution-guidelines)
- [Development Setup](#development-setup)

## Creating Your Tools

Tools are always expect to return strings, as they are meant to be used by the agents to generate responses.

There are three ways to create tools for Maxwell agents:
- [Subclassing `BaseTool`](#subclassing-basetool)
- [Using the `tool` decorator](#utilizing-the-tool-decorator)

### Subclassing `BaseTool`

```python
from maxwell_tools import BaseTool

class MyCustomTool(BaseTool):
    name: str = "Name of my tool"
    description: str = "Clear description for what this tool is useful for, you agent will need this information to use it."

    def _run(self, argument: str) -> str:
        # Implementation goes here
        pass
```

Define a new class inheriting from `BaseTool`, specifying `name`, `description`, and the `_run` method for operational logic.


### Utilizing the `tool` Decorator

For a simpler approach, create a `Tool` object directly with the required attributes and a functional logic.

```python
from maxwell_tools import tool
@tool("Name of my tool")
def my_tool(question: str) -> str:
    """Clear description for what this tool is useful for, you agent will need this information to use it."""
    # Function logic here
```

The `tool` decorator simplifies the process, transforming functions into tools with minimal overhead.

## Contribution Guidelines

We eagerly welcome contributions to enrich this toolset. To contribute:

1. **Fork the Repository:** Begin with forking the repository to your GitHub account.
2. **Feature Branch:** Create a new branch in your fork for the feature or improvement.
3. **Implement Your Feature:** Add your contribution to the new branch.
4. **Pull Request:** Submit a pull request from your feature branch to the main repository.

Your contributions are greatly appreciated and will help enhance this project.

## **Development Setup**

**Installing Dependencies:**

```bash
poetry install
```

**Activating Virtual Environment:**

```bash
poetry shell
```

**Setting Up Pre-commit Hooks:**

```bash
pre-commit install
```

**Running Tests:**

```bash
poetry run pytest
```

**Static Type Checking:**

```bash
poetry run pyright
```

**Packaging:**

```bash
poetry build
```

**Local Installation:**

```bash
pip install dist/*.tar.gz
```

Thank you for your interest in enhancing the capabilities of AI agents through advanced tooling. Your contributions make a significant impact.
