# Kidney Disease Classification

CNN-based image classification project to detect kidney disease from CT scans.

## Setup

Requires Python 3.12.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Adjusting .gitignore

Ensure you adjust the `.gitignore` file according to your project needs. For example, since this is a template, the `/data/` folder is commented out and data will not be exlucded from source control:

```plaintext
# exclude data from source control by default
# /data/
```

Typically, you want to exclude this folder if it contains either sensitive data that you do not want to add to version control or large files.

## Duplicating the .env File
To set up your environment variables, you need to duplicate the `.env.example` file and rename it to `.env`. You can do this manually or using the following terminal command:

```bash
cp .env.example .env # Linux, macOS, Git Bash, WSL
copy .env.example .env # Windows Command Prompt
```

This command creates a copy of `.env.example` and names it `.env`, allowing you to configure your environment variables specific to your setup.

`.env` includes `MLFLOW_TRACKING_URI`, `MLFLOW_TRACKING_USERNAME`, and `MLFLOW_TRACKING_PASSWORD` — credentials for logging experiment results to MLflow via DagsHub. See [Experiment Tracking](#experiment-tracking-mlflow--dagshub) below for what they're used for and where to get your own.


## Experiment Tracking (MLflow + DagsHub)

The Model Evaluation stage (`src/cnnClassifier/components/model_evaluation_mlflow.py`) logs each run's params and metrics (loss, accuracy) to [MLflow](https://mlflow.org/), remotely hosted on [DagsHub](https://dagshub.com/). This happens automatically whenever `main.py` reaches the evaluation stage — no separate command needed.

To view your logged runs, go to the **Experiments** tab of your DagsHub repo, e.g. `https://dagshub.com/<your-dagshub-username>/Kidney-Disease-Classification/experiments`.

Credentials are read from `.env` (see above). To get your own:
1. Create a repo on [DagsHub](https://dagshub.com/) (or connect an existing GitHub repo).
2. On the repo page, open the **Remote** dropdown → **Experiments**, which shows your `MLFLOW_TRACKING_URI` and a code snippet with the env vars to set.
3. For `MLFLOW_TRACKING_PASSWORD`, generate a token under your DagsHub **Settings → Tokens**.

Paste these into `.env` as `MLFLOW_TRACKING_URI`, `MLFLOW_TRACKING_USERNAME`, and `MLFLOW_TRACKING_PASSWORD`.

See [reports/model_evaluation.md](reports/model_evaluation.md) for current model results and known limitations.


## Pipeline (DVC)

The pipeline stages are defined in `dvc.yaml` (work in progress — currently only `data_ingestion` is wired up).

```bash
dvc init          # one-time: initializes the DVC repo (creates .dvc/)
dvc repro         # runs any pipeline stage whose deps/params/code changed since the last run
dvc dag           # prints the pipeline stage graph
dvc status        # shows which stages are out of date without running them
dvc metrics show  # prints tracked metrics (e.g. scores.json) for the current checkout
dvc metrics diff  # compares tracked metrics against a previous commit/branch
```

`dvc repro` is what you run instead of `python main.py` once the pipeline is fully wired up — it only reruns stages whose declared `deps`/`params` actually changed, skipping the rest.




## Dockerization & CI/CD (GitHub Actions + AWS ECR)

The app is containerized (see `Dockerfile`) and deployed via a GitHub Actions pipeline (`.github/workflows/main.yaml`) that builds the image, pushes it to Amazon ECR, and deploys it to an EC2 instance.

### 1. AWS setup (one-time)

1. **IAM user** — create a user with programmatic access and attach:
   - `AmazonEC2ContainerRegistryFullAccess`
   - `AmazonEC2FullAccess`
2. **ECR repository** — create a private repo to store the built image; note its URI (`<account-id>.dkr.ecr.<region>.amazonaws.com/<repo-name>`).
3. **EC2 instance** — launch an instance (Ubuntu) that will run the container; install Docker on it:
   ```bash
   sudo apt-get update -y && sudo apt-get upgrade -y
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker ubuntu
   newgrp docker
   ```
4. **Self-hosted runner** — in the GitHub repo, go to **Settings → Actions → Runners → New self-hosted runner** and follow the shown commands on the EC2 instance to register it. This lets the deployment job run directly on EC2.

### 2. GitHub repo secrets

Add these under **Settings → Secrets and variables → Actions**:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `AWS_ECR_LOGIN_URI` (registry URI, e.g. `<account-id>.dkr.ecr.<region>.amazonaws.com`)
- `ECR_REPOSITORY_NAME`

### 3. Pipeline stages (`.github/workflows/main.yaml`, triggered on push to `main`)

1. **Continuous Integration** — checkout code, lint, run unit tests (currently placeholder `echo` steps — to be filled in).
2. **Continuous Delivery** — authenticate to ECR, build the Docker image, tag it `latest`, push it to the ECR repo.
3. **Continuous Deployment** — runs on the self-hosted EC2 runner: pulls the latest image from ECR, runs it (`docker run -d -p 8080:8080 ...`) with AWS credentials injected as env vars, then prunes old images/containers.

### 4. Running locally with Docker

```bash
docker build -t kidney-disease-classifier .
docker run -p 8080:8080 kidney-disease-classifier
```

## Workflows

1. Update config.yaml
2. Update secrets.yaml
3. Update params.yaml
4. Update the entity
5. Update the configuration manager in src config
6. Update the components
7. Update the pipeline
8. Update main.py
9. Update dvc.yaml
