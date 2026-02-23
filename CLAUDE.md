# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CrewAI is a Python framework for orchestrating autonomous AI agents. It provides a hierarchy of abstractions (Agent → Task → Crew) plus an event-driven Flow system for complex workflows.

## Repository Structure

This is a **UV workspace monorepo** with four packages under `lib/`:

- **`lib/crewai/`** — Core framework (agents, tasks, crews, flows, memory, knowledge, LLM integration)
- **`lib/crewai-tools/`** — Pre-built integration tools
- **`lib/crewai-files/`** — File handling and multimodal input support
- **`lib/devtools/`** — Internal development utilities (version bumping)

Source code lives in `lib/crewai/src/crewai/`. Python >=3.10, <3.14.

## Common Commands

```bash
# Install all dependencies (dev + extras)
uv sync --all-groups --all-extras

# Run all tests (parallel by default via pytest-xdist)
uv run pytest .

# Run a single test file
uv run pytest lib/crewai/tests/test_task.py -v

# Run a single test function
uv run pytest lib/crewai/tests/test_task.py::test_function_name -v

# Run tests for a specific package
uv run pytest lib/crewai/tests/
uv run pytest lib/crewai-tools/tests/
uv run pytest lib/crewai-files/tests/

# Lint
uv run ruff check --config pyproject.toml

# Format
uv run ruff format --config pyproject.toml

# Type check
uv run mypy --config-file pyproject.toml lib/crewai/src/
```

## Test Configuration

- Tests use `--block-network` — external API calls are blocked; use VCR cassettes for HTTP fixtures
- Tests run with `-n auto` (parallel) and `--timeout=60`
- Environment variable `CREWAI_TESTING=true` is set automatically in conftest
- Storage is redirected via `CREWAI_STORAGE_DIR` to a temp directory per test session
- The root `conftest.py` resets the event system and cleans up handlers after each test
- Marker `@pytest.mark.telemetry` for tests that should not mock telemetry
- Async tests require `@pytest.mark.asyncio(loop_scope="function")` (strict mode)

## Code Style

- **2-space indentation** for Python files (see `.editorconfig`)
- **Ruff** for linting and formatting (config in `pyproject.toml`)
- **MyPy** in strict mode with Pydantic plugin
- Line length: no hard limit (E501 ignored), but ruff format applies reasonable wrapping
- Imports sorted by isort rules via ruff
- Conventional commits enforced via commitizen pre-commit hook
- `from __future__ import annotations` is enforced by ruff (`future-annotations = true`)

## Architecture

### Core Abstractions

**Crew** (`crew.py`) orchestrates execution. It holds a list of **Agents** and **Tasks**, manages memory/knowledge, and runs tasks via a **Process** (sequential or hierarchical).

**Agent** (`agent/core.py`) wraps an LLM with tools, memory, and knowledge. Agents execute tasks by calling the LLM, parsing tool selections, executing tools (with hooks), and updating memory.

**Task** (`task.py`) defines work with a description, expected output, assigned agent, and optional context from other tasks (dependency chaining). Supports guardrails, conditional execution, and callbacks.

**Flow** (`flow/flow.py`) is an independent event-driven workflow system with state management. Uses decorators `@start`, `@listen`, `@router` to define method-based workflows with conditional routing (`or_()`, `and_()`). Supports persistence, human feedback (HITL), and visualization.

### Key Systems

- **LLM** (`llm.py`) — Multi-provider wrapper using LiteLLM. Handles streaming, structured output, token counting, context window management. Provider-specific configs in `llms/providers/`.
- **Memory** (`memory/unified_memory.py`) — Unified system with LLM-driven analysis, adaptive-depth recall, composite scoring (recency + semantic + importance), and LanceDB storage.
- **Knowledge** (`knowledge/`) — RAG system with pluggable sources and vector store backends (ChromaDB, Qdrant, LanceDB).
- **Tools** (`tools/base_tool.py`) — Abstract base with schema validation, caching, and usage tracking. MCP tool wrapping in `mcp/`.
- **Events** (`events/`) — Central event bus with typed events for all operations (agents, tasks, crews, flows, LLM, memory, tools, MCP).
- **Hooks** (`hooks/`) — Before/after interceptors for LLM calls and tool execution.
- **A2A** (`a2a/`) — Agent-to-Agent communication protocol for remote agent delegation.

### Execution Flow

`Crew.kickoff()` → prepares agents/tasks → initializes memory/knowledge → iterates tasks per process type → each task calls `Agent.execute()` (LLM call → tool execution → memory update) → guardrails → callbacks → returns `CrewOutput`.

### Extending

- Custom tools: subclass `BaseTool` or use the `@tool` decorator
- Custom knowledge sources: subclass `BaseKnowledgeSource`
- Custom storage: implement storage backend interfaces
- Hooks: register before/after interceptors via decorators
- Event listeners: subscribe to typed events on the event bus
