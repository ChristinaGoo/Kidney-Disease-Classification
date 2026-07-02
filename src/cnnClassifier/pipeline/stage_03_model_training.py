from cnnClassifier.config.configuration import ConfigurationManager
from cnnClassifier.components.model_training import Training
from cnnClassifier import logger

STAGE_NAME = "Model Training"

class ModelTrainingPipeline:
    def __init__(self):
        pass
    
    def main(self):
        config = ConfigurationManager()
        model_training_config = config.get_model_training_config()

        training = Training(config=model_training_config)
        training.get_base_model_config()
        training.train_valid_generator()
        training.train()

if __name__ == "__main__":
    try:
        logger.info(f"**************************************")
        logger.info(f">>>>> stage {STAGE_NAME} started <<<<<")
        model_training = ModelTrainingPipeline()
        model_training.main()
        logger.info(f">>>>> stage {STAGE_NAME} completed!<<<<<\n\nx==========x")
    except Exception as e:
        logger.exception(e)
        raise e
    
    