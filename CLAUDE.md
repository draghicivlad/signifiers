# Python Project Configuration

## CRITICAL RULE: NO EMOJIS
NEVER use emojis in ANY code, comments, commit messages, documentation, or output. Use plain text only.

## Project Context
This is a Python machine learning project. All code should follow Python best practices and be well-documented.

## Development Environment
- Python version: 3.10+
- Package manager: pip (or uv if preferred)
- Virtual environment: venv
- Dependency file: requirements.txt

## Python Coding Standards

### Code Style
- Follow PEP 8 style guidelines
- Use type hints for function parameters and return types
- Maximum line length: 88 characters (Black default)
- Use docstrings for all functions, classes, and modules (Google style)
- Import order: standard library, third-party, local imports

### Naming Conventions
- Variables and functions: snake_case
- Classes: PascalCase
- Constants: UPPER_SNAKE_CASE
- Private methods/attributes: _leading_underscore

### Code Quality
- Write comprehensive error handling with specific exception types
- Include input validation for functions
- Add logging using Python's logging module (not print statements)
- Keep functions focused and single-purpose (max ~50 lines)
- Avoid deeply nested code (max 3 levels)

### Documentation
- Every function must have a docstring explaining:
  - Purpose
  - Parameters with types
  - Return value with type
  - Raises (exceptions)
  - Example usage (for complex functions)

### Testing
- Write tests for all new functionality
- Test file naming: test_<module_name>.py
- Use pytest framework
- Aim for meaningful test coverage on critical paths
- Include edge cases and error conditions

## File Organization
- Main source code: src/
- Tests: tests/
- Documentation: docs/
- Configuration files: root directory
- Data files: data/ (if applicable)

## Git Workflow
- Write clear, descriptive commit messages
- Format: "verb: brief description" (e.g., "add: implement SVM classifier")
- No emojis in commit messages
- Make small, focused commits
- Test code before committing

## Development Process

### Before Starting Work
1. Read docs/STATUS.md to understand current project state
2. Check docs/ROADMAP.md for what needs to be done
3. Use /review-status command to get context

### During Development
1. Make incremental changes
2. Test frequently
3. Keep STATUS.md updated as you work

### After Completing Work
1. Use /log-progress command to document what was done
2. Update ROADMAP.md to mark tasks as complete
3. Ensure all tests pass

## Project Tracking Files

### docs/STATUS.md
- Current project state and what's being worked on
- Active issues or blockers
- Recent changes (last 3-5 items)
- Next immediate steps

### docs/ROADMAP.md  
- High-level features and milestones
- Organized by priority (High/Medium/Low)
- Use [ ] for todo, [IN PROGRESS] for in-progress, [DONE] for completed
- Include dates when tasks are started and completed (YYYY-MM-DD)

### docs/IMPLEMENTATION_LOG.md
- Detailed log of what was implemented, when, and in which files
- Helps maintain project history
- Format: Date, Task, Files Modified, Description

## Commands Available
- /update-status: Update project STATUS.md with current state
- /log-progress: Log completed work to IMPLEMENTATION_LOG.md
- /review-status: Review all status files to understand project state

## Machine Learning Specific Guidelines
- Document model architecture choices
- Include data preprocessing steps in comments
- Log hyperparameters and training metrics
- Save model checkpoints with clear naming
- Document evaluation metrics and results
- Keep reproducibility in mind (set random seeds)

## Common Patterns

### Function Template
```python
def function_name(param1: str, param2: int) -> bool:
    """Brief description of function purpose.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When parameter is invalid
    """
    # Implementation
    pass
```

### Error Handling
```python
try:
    # Code that might fail
    result = operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    raise
```

### Logging Setup
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
```

## What NOT to Do
- Do not use emojis anywhere
- Do not use print() for logging (use logging module)
- Do not commit untested code
- Do not write functions longer than 50 lines without good reason
- Do not ignore type hints
- Do not skip docstrings
- Do not use global variables without justification
- Do not hardcode configuration values (use config files/env vars)

## Communication Style
- Be clear and concise
- Ask clarifying questions when requirements are ambiguous
- Explain technical decisions
- Highlight potential issues or trade-offs
- Suggest improvements when appropriate
