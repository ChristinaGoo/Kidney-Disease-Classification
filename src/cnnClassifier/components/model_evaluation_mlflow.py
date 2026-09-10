import os
import numpy as np
import tensorflow as tf
from pathlib import Path
from urllib.parse import urlparse
import mlflow
import mlflow.keras

from cnnClassifier.entity.config_entity import EvaluationConfig
from cnnClassifier.utils.common import save_json

class Evaluation:
    def __init__(self, config: EvaluationConfig):
        self.config = config

    def _valid_generator(self):
        datagenerator_kwargs = dict(
            rescale=1./255,
            validation_split=0.30
        )

        dataflow_kwargs = dict(
            target_size=self.config.params_image_size[:-1],
            batch_size=self.config.params_batch_size,
            interpolation="bilinear"
        )

        valid_datagenerator = tf.keras.preprocessing.image.ImageDataGenerator(
            **datagenerator_kwargs
        )

        self.valid_generator = valid_datagenerator.flow_from_directory(
            directory=self.config.training_data,
            subset="validation",
            shuffle=False,
            classes=["Normal", "Tumor"],
            **dataflow_kwargs
        )

    @staticmethod
    def load_model(path: Path) -> tf.keras.Model:
        return tf.keras.models.load_model(path)

    def evaluation(self):
        self.model = self.load_model(self.config.path_of_model)
        self._valid_generator()
        self.score = self.model.evaluate(self.valid_generator)
        self._per_class_recall()
        self.save_score()

    def _per_class_recall(self):
        # plain accuracy is misleading on an imbalanced dataset (a model that always
        # predicts the majority class scores ~69% "accuracy" without learning anything);
        # per-class recall exposes that a class is never being predicted correctly
        y_true = self.valid_generator.classes
        y_pred = np.argmax(self.model.predict(self.valid_generator), axis=-1)
        class_names = list(self.valid_generator.class_indices.keys())

        self.per_class_recall = {}
        for class_idx, name in enumerate(class_names):
            mask = y_true == class_idx
            recall = float((y_pred[mask] == class_idx).mean()) if mask.any() else 0.0
            self.per_class_recall[f"{name.lower()}_recall"] = recall

    def save_score(self):
        scores = {"loss": self.score[0], "accuracy": self.score[1], **self.per_class_recall}
        save_json(path=Path("scores.json"), data=scores)

    def log_into_mlflow(self):
        mlflow.set_tracking_uri(self.config.mlflow_uri)
        tracking_url_type_store = urlparse(mlflow.get_tracking_uri()).scheme

        with mlflow.start_run():
            mlflow.log_params(self.config.all_params)
            mlflow.log_metrics({
                "loss": self.score[0],
                "accuracy": self.score[1],
                **self.per_class_recall
            })

            if tracking_url_type_store != "file":
                mlflow.keras.log_model(
                    self.model, "model",
                    registered_model_name="VGG16Model"
                )
            else:
                mlflow.keras.log_model(self.model, "model")