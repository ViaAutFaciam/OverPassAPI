# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OverPassAPI is a Python project for working with the OpenStreetMap Overpass API. It's a data exploration and analysis project using Jupyter notebooks for interactive analysis, with dependencies on pandas, matplotlib, and JupyterLab.

## Development Environment

### Setup
- **Package Manager**: Use `uv` for all dependency management and script execution
- **Virtual Environment**: The project uses `.venv` (created and managed by `uv`)
- **Python Version**: Requires Python >=3.14

### Running Commands
All Python scripts and tools must be executed through `uv`:
```bash
uv run <command>
```

Examples:
- `uv run jupyter lab` - Start Jupyter Lab for notebook development
- `uv run python script.py` - Run Python scripts
- `uv run pip install <package>` - Install additional dependencies (though prefer updating pyproject.toml)

### Dependency Management
- Dependencies are defined in `pyproject.toml`
- Lock file (`uv.lock`) should be committed to version control
- Current dependencies:
  - `jupyterlab>=4.4.10` - Interactive notebook environment
  - `matplotlib>=3.10.7` - Data visualization
  - `pandas>=2.3.3` - Data manipulation and analysis

## Project Structure

```
├── notebooks/           # Jupyter notebooks for data exploration
│   └── sample.ipynb    # Example notebook for Overpass API usage
├── pyproject.toml      # Project metadata and dependencies
├── uv.lock            # Dependency lock file
├── requirements.txt   # (Legacy, prefer pyproject.toml)
└── README.md          # Project documentation
```

## Key Development Workflows

### Working with Notebooks
1. Start Jupyter Lab: `uv run jupyter lab`
2. Open notebooks from the `notebooks/` directory
3. Notebooks are used for exploratory data analysis and testing against the Overpass API

### Adding Dependencies
1. Update `pyproject.toml` with the new dependency
2. Run `uv sync` to update the lock file
3. Commit both `pyproject.toml` and `uv.lock`

## Notes

- The project is in early stages (version 0.1.0)
- Primary focus is on data exploration with Jupyter notebooks
- The `.idea/` directory contains IDE configuration (IntelliJ/PyCharm)