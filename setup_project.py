#!/usr/bin/env python3
"""
Quick setup script for Claude Code Python projects
Creates the basic project structure with tracking files
"""

import os
from pathlib import Path
from datetime import date

def create_directory_structure(base_path: Path):
    """Create the project directory structure."""
    directories = [
        base_path / "src",
        base_path / "tests",
        base_path / "docs",
        base_path / ".claude" / "commands",
        base_path / "data",
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"Created: {directory}")

def create_gitignore(base_path: Path):
    """Create a Python .gitignore file."""
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
dist/
*.egg-info/
.pytest_cache/
.coverage
htmlcov/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
data/
models/
*.log

# Claude Code local settings
.claude/settings.local.json
"""
    
    gitignore_path = base_path / ".gitignore"
    gitignore_path.write_text(gitignore_content)
    print(f"Created: {gitignore_path}")

def create_requirements_txt(base_path: Path):
    """Create a basic requirements.txt file."""
    requirements_content = """# Core dependencies
numpy>=1.24.0
pandas>=2.0.0
scikit-learn>=1.3.0

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0

# Development
black>=23.0.0
flake8>=6.0.0
mypy>=1.4.0
"""
    
    requirements_path = base_path / "requirements.txt"
    requirements_path.write_text(requirements_content)
    print(f"Created: {requirements_path}")

def create_init_files(base_path: Path):
    """Create __init__.py files for Python packages."""
    init_files = [
        base_path / "src" / "__init__.py",
        base_path / "tests" / "__init__.py",
    ]
    
    for init_file in init_files:
        init_file.touch()
        print(f"Created: {init_file}")

def create_example_module(base_path: Path):
    """Create an example Python module with proper structure."""
    example_content = '''"""
Example module demonstrating project structure and coding standards.

This module shows how to structure Python code following the project
guidelines defined in CLAUDE.md.
"""

import logging
from typing import Optional

# Configure logging
logger = logging.getLogger(__name__)


class ExampleClass:
    """Example class demonstrating proper documentation.
    
    This class serves as a template for writing well-documented,
    type-hinted Python code.
    
    Attributes:
        name: A string representing the instance name
        value: An integer value associated with the instance
    """
    
    def __init__(self, name: str, value: int = 0):
        """Initialize the ExampleClass.
        
        Args:
            name: The name for this instance
            value: Initial value (default: 0)
        """
        self.name = name
        self.value = value
    
    def process_data(self, data: list[int]) -> Optional[float]:
        """Process a list of integers and return the average.
        
        Args:
            data: List of integers to process
            
        Returns:
            Average of the input data, or None if empty
            
        Raises:
            ValueError: If data contains non-numeric values
        """
        if not data:
            logger.warning("Empty data list provided")
            return None
        
        try:
            result = sum(data) / len(data)
            logger.info(f"Processed {len(data)} items, average: {result}")
            return result
        except TypeError as e:
            logger.error(f"Invalid data type in list: {e}")
            raise ValueError("All data items must be numeric") from e


def example_function(x: int, y: int) -> int:
    """Add two integers and return the result.
    
    Args:
        x: First integer
        y: Second integer
        
    Returns:
        Sum of x and y
    """
    return x + y
'''
    
    example_path = base_path / "src" / "example.py"
    example_path.write_text(example_content)
    print(f"Created: {example_path}")

def create_example_test(base_path: Path):
    """Create an example test file."""
    test_content = '''"""
Tests for the example module.

Demonstrates testing best practices including:
- Clear test names
- Arrange-Act-Assert pattern
- Edge case testing
- Error handling verification
"""

import pytest
from src.example import ExampleClass, example_function


class TestExampleClass:
    """Test suite for ExampleClass."""
    
    def test_initialization(self):
        """Test that ExampleClass initializes correctly."""
        obj = ExampleClass("test", 42)
        assert obj.name == "test"
        assert obj.value == 42
    
    def test_process_data_with_valid_input(self):
        """Test process_data with valid integer list."""
        obj = ExampleClass("test")
        result = obj.process_data([1, 2, 3, 4, 5])
        assert result == 3.0
    
    def test_process_data_with_empty_list(self):
        """Test process_data with empty list returns None."""
        obj = ExampleClass("test")
        result = obj.process_data([])
        assert result is None
    
    def test_process_data_with_invalid_data(self):
        """Test process_data raises ValueError for invalid data."""
        obj = ExampleClass("test")
        with pytest.raises(ValueError):
            obj.process_data([1, 2, "invalid", 4])


def test_example_function():
    """Test the example_function."""
    assert example_function(2, 3) == 5
    assert example_function(-1, 1) == 0
    assert example_function(0, 0) == 0
'''
    
    test_path = base_path / "tests" / "test_example.py"
    test_path.write_text(test_content)
    print(f"Created: {test_path}")

def main():
    """Main setup function."""
    print("=" * 60)
    print("Claude Code Python Project Setup")
    print("=" * 60)
    print()
    
    # Get project name
    project_name = input("Enter project name (or press Enter for current directory): ").strip()
    
    if project_name:
        base_path = Path.cwd() / project_name
        base_path.mkdir(exist_ok=True)
    else:
        base_path = Path.cwd()
    
    print(f"\nSetting up project in: {base_path}")
    print()
    
    # Create structure
    create_directory_structure(base_path)
    create_gitignore(base_path)
    create_requirements_txt(base_path)
    create_init_files(base_path)
    create_example_module(base_path)
    create_example_test(base_path)
    
    print()
    print("=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Copy CLAUDE.md to project root")
    print("2. Copy .claude/ directory with commands")
    print("3. Copy docs/ directory with tracking files")
    print("4. Create virtual environment: python -m venv venv")
    print("5. Activate it: source venv/bin/activate")
    print("6. Install dependencies: pip install -r requirements.txt")
    print("7. Run tests: pytest tests/")
    print("8. Start Claude Code: claude")
    print()
    print("Then use these commands:")
    print("  /review-status  - Review project state")
    print("  /update-status  - Update current status")
    print("  /log-progress   - Log completed work")
    print("  /update-roadmap - Update roadmap tasks")
    print()

if __name__ == "__main__":
    main()
