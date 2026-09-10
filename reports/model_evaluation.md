# Model Evaluation Report

## Dataset

- Source: Kaggle [`nazmul0087/ct-kidney-dataset-normal-cyst-tumor-and-stone`](https://www.kaggle.com/datasets/nazmul0087/ct-kidney-dataset-normal-cyst-tumor-and-stone)
- Restricted to 2 of the dataset's 4 classes: **Normal** (5,077 images) and **Tumor** (2,283 images) — a ~69% / 31% split. Cyst and Stone are not used.
- Model: VGG16 (ImageNet weights, frozen) + a single trainable `Dense(2, softmax)` head.

## Problem: a misleading accuracy number

The first trained model reported **69.0% accuracy** in `scores.json` and MLflow — a plausible-looking result that was actually meaningless.

69% is *exactly* the fraction of Normal images in the dataset. Manual per-image testing (bypassing `model.evaluate()` and calling the same `PredictionPipeline` the app uses) showed the model predicted **"Normal" for every single image tested, including true Tumor cases**, with ~100% confidence regardless of input.

**Root cause:** only the final `Dense` layer is trainable (the VGG16 base is frozen), leaving very little capacity to learn a real decision boundary. Combined with `CategoricalFocalCrossentropy` loss and no correction for the 69/31 class imbalance, the cheapest loss-minimizing solution was to always predict the majority class. Plain accuracy doesn't expose this failure mode on an imbalanced dataset — it looks like a working, reasonably-accurate model.

## Fix

1. **Class-weighted loss** (`src/cnnClassifier/components/model_training.py`) — training samples are weighted inversely by class frequency, so Tumor examples aren't drowned out by the more numerous Normal examples.
2. **Lower learning rate** (`params.yaml`: `LEARNING_RATE` 0.01 → 0.001) — class weighting alone overcorrected into the *opposite* collapse (always predicting Tumor, 0% Normal recall). A 10x lower learning rate let training converge to a real boundary instead of oscillating between two degenerate solutions.
3. **Per-class recall tracking** (`src/cnnClassifier/components/model_evaluation_mlflow.py`) — accuracy alone can't catch this. `scores.json` and MLflow now also record per-class recall, so a future regression back to a collapsed model would be immediately visible instead of hiding behind a fine-looking aggregate number.

## Results

| Metric | Before (collapsed) | After (fixed) |
|---|---|---|
| Accuracy | 69.0% | 85.9% |
| Normal recall | 100% | 90.5% |
| Tumor recall | 0% | 75.7% |
| Loss | 1.249 | 0.023 |

Verified two ways:
- `model.evaluate()` over the full held-out validation split (2,207 images) via the DVC `evaluation` stage.
- The actual inference path (`PredictionPipeline`, same code the Flask app calls) on a held-out sample of 20 images (10 Normal, 10 Tumor): 8/10 Normal and 5/10 Tumor correctly classified — real variation across both classes, no collapse.

Runs are tracked in MLflow via DagsHub — see [Experiment Tracking](../README.md#experiment-tracking-mlflow--dagshub) in the README.

## Known limitations

- **Tumor recall (75.7%) is meaningfully lower than Normal recall (90.5%)** — the model still misses roughly 1 in 4 real Tumor cases. For a medical screening use case this asymmetry is the one that matters most (a missed Tumor is costlier than a false alarm), and isn't fully resolved by this fix. Further work could include unfreezing more of the VGG16 backbone for additional trainable capacity, gathering more Tumor examples, or tuning a per-class decision threshold instead of raw `argmax`.
- This model only distinguishes Normal vs. Tumor; Cyst and Stone (present in the source dataset) are excluded entirely.
- This is a learning/tutorial project's result, not a clinically validated model.
