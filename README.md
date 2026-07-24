# Simple Agent

A small educational Python coding agent built with the OpenAI-compatible
tool-calling API. It can inspect files, read and write file contents, execute
Python files, and iterate over tool results until it completes a task.

## Setup

This project uses Python 3.12 and `uv`.

```bash
uv sync
```

Create a `.env` file containing:

```text
OPENROUTER_API_KEY=your_api_key
```

## Usage

```bash
uv run python main.py "Explain how the calculator works"
```

Add `--verbose` to see token usage, tool calls, and tool results.

## Tests

```bash
uv run python -m unittest \
  test_agent_loop.py \
  test_call_function.py \
  test_function_declaration.py
```
