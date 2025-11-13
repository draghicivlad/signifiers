# Quick Start Guide

## What You Got

A complete Claude Code setup for Python projects with:
- Comprehensive CLAUDE.md configuration
- Project tracking system (STATUS.md, ROADMAP.md, IMPLEMENTATION_LOG.md)
- 4 custom commands for easy project management
- Example Python code and tests
- Setup script

## Files Overview

```
Your Files:
├── CLAUDE.md                    # Main config (Python rules, NO EMOJIS)
├── README.md                    # Complete documentation
├── setup_project.py            # Quick setup script
├── .claude/
│   ├── commands/
│   │   ├── review-status.md   # Review project state
│   │   ├── update-status.md   # Update current status
│   │   ├── log-progress.md    # Log work done
│   │   └── update-roadmap.md  # Update tasks
│   └── settings.json          # Optional settings
└── docs/
    ├── STATUS.md              # Current state
    ├── ROADMAP.md            # Feature planning
    └── IMPLEMENTATION_LOG.md # History
```

## Setup in 3 Steps

### 1. Copy Files to Your Project

```bash
# Create your project directory
mkdir my-ml-project
cd my-ml-project

# Copy all files from this folder to your project
# - CLAUDE.md
# - .claude/ directory
# - docs/ directory
# - setup_project.py (optional)
```

### 2. Initialize Python Environment

```bash
# Run the setup script (creates src/, tests/, requirements.txt)
python setup_project.py

# Or manually:
mkdir -p src tests data
touch src/__init__.py tests/__init__.py

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Create requirements.txt with your dependencies
pip install numpy pandas scikit-learn pytest
pip freeze > requirements.txt
```

### 3. Start Using Claude Code

```bash
# Start Claude Code
claude

# Inside Claude Code, try the commands:
/review-status      # See project overview
/update-roadmap     # Add tasks to roadmap
```

## The 4 Essential Commands

### `/review-status`
**When:** Start of every coding session
**What:** Shows current state, blockers, next priorities
```
> /review-status
[Gets complete project overview]
```

### `/update-status`
**When:** Starting new work or hitting blockers
**What:** Updates STATUS.md with current info
```
> /update-status
[Prompts for updates, then saves]
```

### `/log-progress`
**When:** After completing significant work
**What:** Documents what was built and where
```
> /log-progress
[Adds entry to IMPLEMENTATION_LOG.md]
```

### `/update-roadmap`
**When:** Starting/completing tasks or adding new ones
**What:** Manages task status in ROADMAP.md
```
> /update-roadmap
[Interactive menu for roadmap updates]
```

## Daily Workflow

### Morning
```bash
1. cd your-project
2. source venv/bin/activate
3. claude
4. /review-status
5. Pick a task from roadmap
6. /update-roadmap (mark as IN PROGRESS)
```

### During Work
```python
# Write code with:
# - Type hints
# - Docstrings
# - Tests
# - NO EMOJIS

# Run tests
pytest tests/

# Commit often
git commit -m "add: feature description"
```

### Evening
```bash
1. /log-progress (document what you built)
2. /update-roadmap (mark as DONE)
3. /update-status (update current state)
4. git push
```

## Key Rules (from CLAUDE.md)

1. **NO EMOJIS** - Anywhere, ever, period
2. **Type hints** - All function parameters and returns
3. **Docstrings** - Every function, Google style
4. **Tests** - pytest for all new code
5. **PEP 8** - Follow Python style guidelines
6. **Line length** - 88 characters max
7. **Error handling** - Specific exceptions, with logging
8. **Small commits** - Clear, focused changes

## Python Code Template

```python
"""Module description."""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def my_function(param1: str, param2: int = 0) -> bool:
    """Brief function description.
    
    Args:
        param1: Description of param1
        param2: Description of param2 (default: 0)
        
    Returns:
        True if success, False otherwise
        
    Raises:
        ValueError: If param1 is empty
    """
    if not param1:
        raise ValueError("param1 cannot be empty")
    
    try:
        # Implementation
        result = do_something(param1, param2)
        logger.info(f"Operation completed: {result}")
        return True
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        return False
```

## Tracking Files Cheat Sheet

### STATUS.md
- **Purpose:** Current snapshot
- **Update when:** Starting work, hitting blockers
- **Contains:** Active work, blockers, recent changes, next steps

### ROADMAP.md  
- **Purpose:** Feature planning
- **Update when:** Planning features, completing tasks
- **Contains:** Tasks by priority, with status and dates

### IMPLEMENTATION_LOG.md
- **Purpose:** Detailed history
- **Update when:** After completing significant work
- **Contains:** Date, files changed, description, notes

## Example Session

```bash
$ claude

> /review-status
PROJECT STATUS REVIEW
====================
Current: Ready to implement SVM classifier
Next: Build baseline model, add cross-validation

> /update-roadmap
What would you like to update?
> 1. Mark task as started
Which task? Implement SVM classifier
[Updates roadmap with IN PROGRESS status]

[... write code, tests ...]

> /log-progress
What work was completed?
1. Feature: SVM classifier with RBF kernel
2. Files: src/models/svm.py, tests/test_svm.py  
3. Description: Implemented SVM with cross-validation
4. Notes: Used scikit-learn, set random_state=42
[Logs to IMPLEMENTATION_LOG.md]

> /update-roadmap
What would you like to update?
> 2. Mark task as completed
Which task? Implement SVM classifier
[Updates roadmap with DONE status and date]

> /update-status
What updates? 
Active: Working on hyperparameter tuning
Next: Grid search for optimal parameters
[Updates STATUS.md]
```

## Troubleshooting

**Commands not working?**
- Ensure `.claude/commands/*.md` files exist
- Restart Claude Code
- Check file permissions

**Claude not following rules?**
- Remind: "Please check CLAUDE.md for project guidelines"
- Emphasize: "Remember: NO EMOJIS"

**Tests failing?**
```bash
# Run with verbose output
pytest -v tests/

# Run specific test
pytest tests/test_example.py::test_function_name

# With coverage
pytest --cov=src tests/
```

## Customization Tips

### Add Your Own Command
Create `.claude/commands/my-command.md`:
```markdown
# /my-command

Description of command

## Usage
How to use it

## Process
Steps to execute
```

### Adjust Python Version
Edit `CLAUDE.md` and update:
```markdown
## Development Environment
- Python version: 3.11+  # Change this
```

### Different Package Manager
If using `uv` instead of `pip`, update CLAUDE.md:
```markdown
- Package manager: uv
- Install: uv add <package>
- Run: uv run python script.py
```

## Best Practices

1. **Start each session with `/review-status`**
2. **Keep STATUS.md current** (update when things change)
3. **Log significant work** (use `/log-progress`)
4. **Update roadmap regularly** (mark progress)
5. **Write tests first** (TDD when possible)
6. **Commit often** (small, focused commits)
7. **Document decisions** (in log notes)
8. **NO EMOJIS** (seriously, none!)

## Resources

- **Full documentation:** See README.md
- **Python guidelines:** See CLAUDE.md
- **Command details:** Check `.claude/commands/*.md`
- **Claude Code docs:** https://docs.claude.com

## Need Help?

1. Read the README.md (comprehensive guide)
2. Check CLAUDE.md (all Python rules)
3. Look at command files (detailed instructions)
4. Ask Claude: "What's in CLAUDE.md?" or "How do I use /review-status?"

## Remember

This setup is intentionally simple:
- Plain markdown files (no complex tools)
- Clear structure (easy to understand)
- Focused on Python ML projects
- Emphasizes good practices
- **NO EMOJIS** (worth repeating!)

Start small, use the commands, and adjust as needed. The tracking system works best when you actually use it!

---

**Most Important:** Start with `/review-status` and keep your tracking files updated!
