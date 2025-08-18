# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Code Formatting and Linting
- `just fmt` - Format code and fix linting issues (runs `ruff format` and `ruff check --fix`)
- `ruff format` - Format code using ruff
- `ruff check --fix` - Run linter and auto-fix issues

### Running the Application
- `uv run python main.py generate --profile path/to/profile.txt` - Generate a cover letter using job search
- `uv run python main.py generate --profile path/to/profile.txt --location "San Francisco, CA" --max-results 30` - Generate cover letter with specific search parameters
- `python main.py generate --help` - Show CLI help for generate command
- `python main.py create-profile-template --output my_profile.txt` - Create example profile template

### Environment Setup
- `uv install` - Install dependencies using uv
- `cp .env.example .env` - Set up environment variables (requires OPENAI_API_KEY)

### Git Operations
- `just push "commit message"` - Stage, commit, and push changes

## Architecture Overview

This is a multi-agent AI cover letter generator built with LangChain and LangGraph. The application uses a workflow-based architecture with specialized agents:

### Core Workflow (src/resume_generator/workflows/graph.py)
The LangGraph workflow orchestrates four sequential agents:
1. **ProfileExtractorAgent** - Parses user profiles into structured data
2. **JobSearchAgent** - Searches for relevant jobs using jobspy integration
3. **SkillsMatcherAgent** - Matches user skills with job requirements
4. **CoverLetterGeneratorAgent** - Generates tailored cover letters based on analysis

The workflow is defined as a StateGraph that passes a WorkflowState between agents.

### Agent Architecture (src/resume_generator/agents/)
- **BaseAgent** (base.py) - Abstract base class that all agents inherit from
  - Uses ChatOpenAI with configurable model (defaults to gpt-4o-mini)
  - Supports OpenRouter API via configurable base_url
  - Provides common prompt creation utilities
- All agents follow the same pattern: inherit from BaseAgent and implement the `process()` method

### State Management (src/resume_generator/workflows/state.py)
WorkflowState is a TypedDict that maintains data flow between agents throughout the workflow.

### Configuration (src/resume_generator/config.py)
Centralized configuration management for API keys, models, and other settings.

### Entry Points
- **main.py** - Simple entry point that imports and calls the CLI
- **src/resume_generator/cli.py** - Click-based CLI interface with commands for generation and template creation

## Key Dependencies
- **LangChain** - LLM framework and agent orchestration
- **LangGraph** - Workflow and state graph management  
- **Click** - CLI interface
- **Pydantic** - Data validation and schemas
- **OpenAI/OpenRouter** - LLM API access
- **uv** - Fast Python package manager (preferred over pip)

## Environment Variables
- `OPENAI_API_KEY` - Required for LLM access
- `OPENAI_MODEL` - Model to use (default: gpt-4o-mini)
- `OPENAI_BASE_URL` - API endpoint (default: https://openrouter.ai/api/v1)