import os
import numpy as np
import tensorflow as tf
from pathlib import Path
from zipfile import ZipFile
from cnnClassifier.entity.config_entity import ModelTrainingConfig


class Training:
    def __init__(self, config: ModelTrainingConfig):        
        self.config = config
        
        
    def get_base_model_config(self):
        self.model = tf.keras.models.load_model(
            self.config.updated_base_model_path,
            compile=False
        )
        self.model.compile(
            optimizer=tf.keras.optimizers.SGD(learning_rate=self.config.params_learning_rate),
            loss=tf.keras.losses.CategoricalFocalCrossentropy(),
            metrics=["accuracy"]
        )
        
    
    def train_valid_generator(self):
        
        datagenerator_kwargs = dict(
            rescale=1./255,
            validation_split=0.2
        )
        
        dataflow_kwargs = dict(
            target_size=self.config.params_image_size[:-1],
            batch_size=self.config.params_batch_size,
            interpolation="bilinear"
        )
        
        valid_datagenerator = tf.keras.preprocessing.image.ImageDataGenerator(**datagenerator_kwargs)

        self.valid_generator = valid_datagenerator.flow_from_directory(
            directory=self.config.training_data,
            subset="validation",
            shuffle=False,
            classes=["Normal", "Tumor"],
            **dataflow_kwargs
        )    
        
        
        if self.config.params_is_augmentation:
            train_datagenerator = tf.keras.preprocessing.image.ImageDataGenerator(
                rotation_range=40,
                horizontal_flip=True,
                width_shift_range=0.2,
                height_shift_range=0.2,
                shear_range=0.2,
                zoom_range=0.2,
                **datagenerator_kwargs
            )
            
        else:
            train_datagenerator = valid_datagenerator
            
        self.train_generator = train_datagenerator.flow_from_directory(
            directory=self.config.training_data,
            subset="training",
            shuffle=True,
            classes=["Normal", "Tumor"],
            **dataflow_kwargs
        )  
    
    
    @staticmethod
    def save_model(path: Path, model: tf.keras.Model):
        model.save(path)
    
    
    def train(self):
        self.steps_per_epoch = self.train_generator.samples // self.train_generator.batch_size
        self.validation_steps = self.valid_generator.samples // self.valid_generator.batch_size

        # dataset is class-imbalanced (~69% Normal / ~31% Tumor); without this the model
        # can minimize loss by just always predicting the majority class
        class_counts = np.bincount(self.train_generator.classes)
        n_classes = len(class_counts)
        class_weight = {i: len(self.train_generator.classes) / (n_classes * count) for i, count in enumerate(class_counts)}

        self.model.fit(
            self.train_generator,
            epochs=self.config.params_epochs,
            steps_per_epoch=self.steps_per_epoch,
            validation_steps=self.validation_steps,
            validation_data=self.valid_generator,
            class_weight=class_weight)
        
        self.save_model(
            path=self.config.trained_model_path, 
            model=self.model)