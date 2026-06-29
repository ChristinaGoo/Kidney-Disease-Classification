# Project Setup Notes

## Goal
End-to-end CNN classification project for kidney disease detection from CT scans.
Follows [this tutorial](https://www.youtube.com/watch?v=86BKEv0X2xU) with a custom template.

---

## 1. Template vs Tutorial Structure

The template (Datalumina/Cookiecutter) provides a generic data science layout. The tutorial expects a specific Python package called `cnnClassifier`. These are compatible — the template's folder structure (`data/`, `models/`, `reports/`) aligns well, but the `src/` package needed to be adapted.

**Deleted template files not used by this project:**
- `src/config.py`, `src/dataset.py`, `src/features.py`, `src/plots.py`
- `src/modeling/`, `src/services/`

---

## 2. Files Needed Before Coding

Only 3 things are required upfront. Everything else (config.yaml, params.yaml, app.py, dvc.yaml, Dockerfile) gets created as the tutorial reaches each stage.

### `setup.py` (at project root)
Makes your own code (`cnnClassifier`) importable as a Python package.
Without it, `from cnnClassifier.utils.common import read_yaml` would fail with `ModuleNotFoundError`.
The key lines:
```python
package_dir={"": "src"},
packages=setuptools.find_packages(where="src")
```
Tells Python: look inside `src/` to find packages.

### `requirements.txt`
Lists all external dependencies. The last line `-e .` triggers `setup.py` during install,
registering `cnnClassifier` in editable mode (changes reflected immediately, no reinstall needed).

### `src/cnnClassifier/` package skeleton
The package the entire project is built inside. Created with empty `__init__.py` files.
Structure:
```
src/cnnClassifier/
├── __init__.py
├── components/      # data ingestion, model training, evaluation
├── config/          # reads config.yaml
├── constants/       # file path constants
├── entity/          # dataclasses for config objects
├── pipeline/        # pipeline stages + prediction
└── utils/           # shared helpers (yaml reader, etc.)
```
These modules are filled in progressively as the tutorial advances.

---

## 3. Environment Setup

Requires **Python 3.12**.

```bash
python3.12 -m venv .venv          # create virtual environment
source .venv/bin/activate          # activate it
pip install -r requirements.txt    # install dependencies + register cnnClassifier
```

**Why a virtual environment?** Isolates project dependencies from your system Python so packages don't conflict across projects.

**Why not just `pip install` each package manually in the notebook?**
External packages (tensorflow, flask, etc.) can be installed with pip. But `cnnClassifier` is your own local code — it's not on PyPI. `setup.py` + `-e .` is what makes it importable without hardcoded `sys.path` hacks.

### Version fixes applied (Python 3.12 compatibility)
The tutorial was written for Python 3.8–3.10. Two pinned versions were incompatible:

| Package | Tutorial version | Fixed version | Reason |
|---|---|---|---|
| tensorflow | 2.12.0 | 2.17.0 | No wheel for Python 3.12 |
| mlflow | 2.2.2 | 2.19.0 | Required pyarrow<12 which fails to build on Python 3.12 |

---

## 4. Git Workflow

```bash
git status              # see what changed
git add .               # stage all changes
git commit -m "message" # save snapshot locally
git push                # publish to GitHub
```

`git add` must come before `git commit` — nothing is committed until explicitly staged.

---

## 5. What Comes Next

The tutorial follows a repeating pattern for each of the 4 pipeline stages:

1. Create a research notebook in `research/` — experiment and validate the logic
2. Translate working notebook code into production structure:
   - `config/config.yaml` — artifact paths and settings
   - `params.yaml` — model hyperparameters
   - `src/cnnClassifier/entity/config_entity.py` — dataclasses
   - `src/cnnClassifier/config/configuration.py` — reads yaml files
   - `src/cnnClassifier/components/` — actual logic
   - `src/cnnClassifier/pipeline/` — pipeline stage
3. Wire into `main.py`

The 4 stages are: **Data Ingestion → Prepare Base Model → Training → Evaluation**
