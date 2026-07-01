# Data Ingestion

## Goal
Download the kidney CT scan dataset from Kaggle and extract it into `artifacts/data_ingestion`, driven entirely by config — no hardcoded paths in the logic itself.

---

## How the pieces link together

```
config/config.yaml          <- dataset id + all paths (root_dir, local_data_file, unzip_dir)
        │
src/cnnClassifier/constants <- CONFIG_FILE_PATH, PARAMS_FILE_PATH (where to find the yaml files)
        │
ConfigurationManager        <- reads config.yaml via constants, returns a DataIngestionConfig
        │
DataIngestionConfig (entity)<- frozen dataclass; just a typed container for the 4 config values
        │
DataIngestion (component)   <- does the actual work, using only what's in the config object
   ├── download_file()      <- calls the venv's kaggle CLI, saves zip to local_data_file
   └── extract_zip_file()   <- unzips local_data_file into unzip_dir
```

Nothing in `DataIngestion` or `ConfigurationManager` hardcodes a dataset id or path — change `config.yaml` and the whole chain picks it up.

---

## Why `download_file` looks the way it does

- Calls `kaggle` via `subprocess.run([...], check=True)`, pointed at `Path(sys.executable).with_name("kaggle")` — the venv's own binary, not whatever `kaggle` resolves to on `$PATH`. Using bare `"kaggle"` risks silently picking up an unrelated system-wide install (this bit us once already).
- Downloads without `--unzip`, so the zip is kept at `local_data_file`. Extraction is a separate step (`extract_zip_file`) using Python's `zipfile`, so re-running extraction doesn't require re-downloading.
- Kaggle auth comes from `~/.kaggle/kaggle.json` (or `~/.kaggle/access_token`), outside the repo — not something the code manages.

---

## Where this is headed

This logic currently lives in `research/1_data_ignestion.ipynb` for experimentation. Per the standard pattern (see `next steps.md`), it still needs to graduate into:
- `src/cnnClassifier/entity/config_entity.py` — the `DataIngestionConfig` dataclass
- `src/cnnClassifier/config/configuration.py` — the `ConfigurationManager`
- `src/cnnClassifier/components/data_ingestion.py` — the `DataIngestion` class
- `src/cnnClassifier/pipeline/stage_01_data_ingestion.py` — runs it, called from `main.py`
