# Agent Development Guidelines

## Build/Lint/Test Commands
- `just fmt` - Format code and fix linting issues (runs `ruff format` and `ruff check --fix`)
- `just lint` - Check for linting issues without fixing
- `just fix` - Fix linting issues automatically
- `just format-check` - Check code formatting without making changes
- `ruff check path/to/file.py` - Lint specific file
- `ruff format path/to/file.py` - Format specific file
- No test framework configured - add pytest if needed

## Code Style Guidelines
- **Line length**: 135 characters (configured in pyproject.toml)
- **Python version**: 3.13+ (target-version)
- **Imports**: Use `ruff` isort rules, group standard library, third-party, then local imports
- **Formatting**: Double quotes, space indentation, LF line endings
- **Types**: Use type hints consistently, prefer `str | None` over `Optional[str]`
- **Naming**: snake_case for variables/functions, PascalCase for classes
- **Error handling**: Raise ValueError for configuration issues, use Pydantic for data validation
- **LLM integration**: Inherit from BaseAgent, implement `process()` method, use observability callbacks
- **State management**: Use TypedDict for workflow state, pass between agents in LangGraph