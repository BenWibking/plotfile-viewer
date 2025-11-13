# Repository Guidelines

## Project Structure & Module Organization
Source code lives in `plotfile_viewer/`, with `openpmd_timeseries/` holding the data reader, plotting, and interactive widgets that power `OpenPMDTimeSeries`. Notebook bootstrap assets sit in `plotfile_viewer/notebook_starter`, while user-facing docs and screenshots are under `docs/`. Tests reside in `tests/` (see `tests/test_tutorials.py` for patterns), and packaging metadata is tracked in `setup.py`, `MANIFEST.in`, and the Pixi metadata (`pyproject.toml`, `pixi.lock`). Binder configuration files describe the reference Jupyter environment; keep them in sync whenever dependencies change.

## Build, Test, and Development Commands
- `pixi install`: creates the managed environment with pyAMReX and friends.
- `pixi run python -m pip install -e .`: performs an editable install inside the Pixi environment so local changes are importable without rebuilding.
- `pixi run python -m pytest tests`: runs the regression suite; use `-k <pattern>` to focus on specific tutorials.
- `pixi run plotfile_notebook`: launches the prefilled notebook experience for exploring plotfile time series.
- `pixi run python -m plotfile_viewer.openpmd_timeseries.main --help`: inspects CLI options when scripting readers directly.

## Coding Style & Naming Conventions
Follow PEP 8 with 4-space indentation, descriptive snake_case identifiers for functions and variables, and UpperCamelCase for classes such as `OpenPMDTimeSeries`. Keep module-level constants uppercase, prefer f-strings for formatting, and preserve relative imports (`from .data_reader import DataReader`) to avoid circular dependencies. Docstrings should use triple double quotes with parameter sections mirroring existing files, and optional kwargs belong at the end of signatures. When touching widgets or NumPy code paths, favor explicit comments that explain intent rather than mechanics.

## Testing Guidelines
All new features need at least one `pytest` test in `tests/`, named `test_<feature>.py` or grouped inside existing modules when related. Use lightweight synthetic plotfiles or fixtures to reproduce AMReX edge cases; avoid committing large data. Tests should assert both numerical correctness (array shapes, field presence) and visualization hooks (e.g., ensuring `Plotter` receives expected metadata). Run `pixi run python -m pytest --maxfail=1` locally before opening a PR, and document any skipped cases with a reason.

## Commit & Pull Request Guidelines
Commits follow short, imperative summaries similar to `add animation output` or `update pixi lockfile`. Each PR should describe the motivation, link issues (e.g., `Fixes #42`), list testing evidence, and include screenshots or GIFs when the GUI changes. Keep diffs focused: refactors, dependency bumps, and UI tweaks belong in separate PRs. Request reviews once CI is green and the branch rebases cleanly onto the latest main.

## Security & Configuration Tips
This viewer consumes plotfiles from untrusted simulations, so do not execute arbitrary notebook cells pasted alongside datasets. Validate file paths before passing them to `OpenPMDTimeSeries`, and prefer read-only mounts when inspecting production outputs. When sharing notebooks, strip local paths or credentials from saved widgets to avoid accidental disclosure.
