from config.paths_config import ANIMELIST_CSV, PROCESSED_DIR
from src.data_processing import DataProcessing
from src.model_training import ModelTraining


if __name__ == "__main__":
    data_processing = DataProcessing(ANIMELIST_CSV, PROCESSED_DIR)
    data_processing.run()

    model_training = ModelTraining(data_path=PROCESSED_DIR)
    model_training.train_model()
