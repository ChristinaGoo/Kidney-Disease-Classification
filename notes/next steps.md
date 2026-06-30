# Next Steps

Each of the 4 stages below follows the same pattern:
**research notebook → production code → wire into main.py → commit**

---

## Stage 1 — Data Ingestion
1. Research notebook: download and explore the kidney CT scan dataset
2. `config/config.yaml` — define artifact paths
3. `src/cnnClassifier/constants/__init__.py` — define paths to config/params files
4. `src/cnnClassifier/entity/config_entity.py` — dataclass for ingestion config
5. `src/cnnClassifier/config/configuration.py` — reads config.yaml, returns config objects
6. `src/cnnClassifier/components/data_ingestion.py` — download, extract, organise data
7. `src/cnnClassifier/pipeline/stage_01_data_ingestion.py` — runs the component
8. Update `main.py`, commit

## Stage 2 — Prepare Base Model
1. Research notebook: load pretrained VGG16, customise top layers
2. `config.yaml` — add base model config
3. `entity`, `configuration.py` — add base model config dataclass
4. `components/prepare_base_model.py` — load and modify VGG16
5. `pipeline/stage_02_prepare_base_model.py`
6. Update `main.py`, commit

## Stage 3 — Model Training
1. Research notebook: train model, validate results
2. `params.yaml` — define hyperparameters (epochs, batch size, etc.)
3. `entity`, `configuration.py` — add training config
4. `components/model_trainer.py` — training loop
5. `pipeline/stage_03_model_trainer.py`
6. Update `main.py`, commit

## Stage 4 — Model Evaluation
1. Research notebook: evaluate model, log metrics
2. Connect MLflow via DagsHub for experiment tracking
3. `entity`, `configuration.py` — add evaluation config
4. `components/model_evaluation_mlflow.py`
5. `pipeline/stage_04_model_evaluation_with_mlflow.py`
6. Update `main.py`, commit

---

## After All Stages
- `app.py` + `templates/index.html` — Flask web app for predictions
- `Dockerfile` — containerise the app
- GitHub Actions — CI/CD pipeline
- Deploy to AWS or Azure
