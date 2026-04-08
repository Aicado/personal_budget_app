# UV Package Manager Guide

This project uses `uv` for Python package and environment management. Here's a comprehensive guide.

## 📦 What is uv?

`uv` is a fast, reliable Python package installer and environment manager written in Rust. It's a replacement for pip, venv, and similar tools.

**Benefits:**
- ⚡ 10-100x faster than pip
- 📦 Automatic dependency resolution
- 🔒 Lock file for reproducible builds
- 🎯 Single tool for all Python management
- 🚀 Zero-config project setup

## 🚀 Installation

```bash
# macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (via winget)
winget install uv

# Or download from: https://github.com/astral-sh/uv/releases
```

Verify installation:
```bash
uv --version
```

## 🔧 Common Commands

### Environment Management

```bash
# Create a new virtual environment
uv venv

# Activate the environment
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Create environment with specific Python version
uv venv --python 3.10
uv venv --python 3.11
```

### Dependency Management

```bash
# Sync dependencies from pyproject.toml
uv sync

# Sync with dev dependencies included
uv sync --all-groups

# Add a new package
uv add fastapi
uv add "pandas>=2.0"  # With version constraint

# Add dev dependency
uv add --dev pytest black ruff

# Remove a package
uv remove fastapi

# List installed packages
uv pip list

# Upgrade packages
uv sync --upgrade
uv sync --upgrade-package pandas  # Specific package
```

### Lock File Management

```bash
# Create/update lock file (uv.lock)
uv lock

# Lock with all dependencies
uv lock --all-groups

# Upgrade dependencies in lock file
uv lock --upgrade

# Upgrade specific package in lock file
uv lock --upgrade-package pandas
```

### Running Code

```bash
# Run Python scripts
uv run python script.py
uv run python -c "print('hello')"

# Run Python modules
uv run -m uvicorn src.backend.main:app
uv run -m pytest

# Run with specific Python version
uv run --python 3.10 script.py

# Use a pip-style requirement
uv run --with requests script.py
uv run --with pytest --with black
```

## 📝 Project Configuration

### pyproject.toml Structure

```toml
[project]
name = "ynab-analyzer"
version = "0.1.0"
description = "YNAB transaction analyzer"
requires-python = ">=3.10"

# Main dependencies
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "pandas>=2.2.0",
]

# Optional dependency groups
[project.optional-dependencies]
dev = [
    "pytest>=7.4.3",
    "black>=23.11.0",
    "ruff>=0.1.8",
]

# Build system
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

# Tool configurations
[tool.black]
line-length = 100

[tool.ruff]
line-length = 100
```

## 🔄 Workflow

### Development Workflow

```bash
# 1. Clone/create project
git clone <repo>
cd project

# 2. Install dependencies
uv sync

# 3. Activate environment (optional)
source .venv/bin/activate

# 4. Development work
uv run python script.py

# 5. Add dependencies when needed
uv add new-package

# 6. Commit lock file
git add uv.lock pyproject.toml
git commit -m "Update dependencies"
```

### Testing Workflow

```bash
# Add test dependencies
uv add --dev pytest pytest-asyncio

# Run tests
uv run pytest

# Run with coverage
uv add --dev pytest-cov
uv run pytest --cov

# Run with specific markers
uv run pytest -m "not slow"
```

### Formatting & Linting

```bash
# Add tools
uv add --dev black ruff

# Format code
uv run black src/

# Lint code
uv run ruff check src/
uv run ruff check src/ --fix  # Auto-fix

# Both
uv run black src/ && uv run ruff check src/ --fix
```

## 📦 Building & Publishing

```bash
# Build package
uv build

# Build wheel only
uv build --wheel

# Build sdist only
uv build --sdist

# Publish to PyPI
uv publish dist/*
```

## 🎯 In This Project

### Running the Backend

```bash
# Start development server
uv run -m uvicorn src.backend.main:app --reload

# Or using npm script (which calls uv)
npm run dev:backend
```

### Adding Dependencies to This Project

```bash
# Add production dependency
uv add numpy matplotlib

# Add development dependency
uv add --dev pytest pytest-asyncio

# Update lock file
uv lock

# Install everything
uv sync
```

### Working with Different Python Versions

```bash
# Check available Python versions
uv python list

# Install specific Python version
uv python install 3.10
uv python install 3.11

# Create environment with specific version
uv venv --python 3.10
uv venv --python 3.11
```

## 🚀 Performance Tips

```bash
# Use --no-cache for clean builds
uv sync --no-cache

# Show what's being installed
uv sync --verbose

# Use pre-built wheels when available
# (uv automatically prefers wheels)

# Pin versions for reproducibility
uv lock --locked
```

## 🐛 Troubleshooting

### Build failures
```bash
# Clear cache
rm -rf .venv/
uv venv

# Try with specific Python
uv venv --python 3.10

# Reinstall
uv sync --force-reinstall
```

### Package conflicts
```bash
# Check dependencies
uv pip list

# Show dependency tree
uv tree

# Resolve conflicts
uv lock --upgrade
uv sync
```

### Performance issues
```bash
# Check if old Python is being used
uv python list

# Update to latest uv
uv self update
```

## 📚 Advanced Features

### Dependency Groups

```toml
[project.optional-dependencies]
dev = ["pytest", "black"]
docs = ["sphinx", "sphinx-rtd-theme"]
all = ["pytest", "black", "sphinx", "sphinx-rtd-theme"]
```

```bash
# Install specific group
uv sync --group dev

# Install all groups
uv sync --all-groups
```

### Git Dependencies

```toml
dependencies = [
    "my-package @ git+https://github.com/user/repo"
]
```

### Path Dependencies

```toml
dependencies = [
    "my-local-package @ file:///path/to/local/package"
]
```

## 🔗 Resources

- **Official Docs**: https://docs.astral.sh/uv/
- **GitHub**: https://github.com/astral-sh/uv
- **Migration Guide**: https://docs.astral.sh/uv/migration/
- **FAQ**: https://docs.astral.sh/uv/reference/settings/

## 💡 Pro Tips

1. **Always commit uv.lock** for reproducible builds
2. **Use dependency groups** for dev/prod separation
3. **Run with `uv run`** instead of activating venv
4. **Check `uv help`** for more commands
5. **Use `uv tree`** to visualize dependencies

---

Happy Python packaging! 🐍
