import comet_ml
import joblib
import numpy as np
import os
import tensorflow as tf
from src.base_model import BaseModel
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *
import sys

ModelCheckpoint = tf.keras.callbacks.ModelCheckpoint
EarlyStopping = tf.keras.callbacks.EarlyStopping
TensorBoard = tf.keras.callbacks.TensorBoard
LearningRateScheduler = tf.keras.callbacks.LearningRateScheduler

logger = get_logger(__name__)

class ModelTraining:
    def __init__(self, data_path):
        self.data_path = data_path

        self.experiment = comet_ml.Experiment(project_name="content-recommender-system", workspace="kristofpella", api_key="OVp5Lo2BPhB6J0TAiAVaEfrx6")

        logger.info(f"Model training & experiment initialized")
    
    def load_data(self):
        try:
            X_train_array = joblib.load(X_TRAIN_ARRAY)
            X_test_array = joblib.load(X_TEST_ARRAY)
            y_train = joblib.load(Y_TRAIN)
            y_test = joblib.load(Y_TEST)

            logger.info(f"Data loaded successfully")

            return X_train_array, X_test_array, y_train, y_test
            
        except Exception as e:
            logger.error(f"Error in loading data: {e}")
            raise CustomException(e, sys)
    
    def train_model(self):
        try:
            X_train_array, X_test_array, y_train, y_test = self.load_data()

            n_users = len(joblib.load(USER_TO_USER_ENCODED))
            n_anime = len(joblib.load(ANIME_TO_ANIME_ENCODED))

            base_model = BaseModel(config_path=CONFIG_PATH)

            model = base_model.RecommenderNet(n_users, n_anime)

            start_learning_rate = 0.00001
            min_learning_rate = 0.00001
            max_learning_rate = 0.00005
            batch_size = 10000

            ramup_epochs = 5
            sustain_epochs = 0
            exp_decay = 0.8

            def learning_rate_scheduler(epoch):
                if epoch < ramup_epochs:
                    return (max_learning_rate - start_learning_rate) / ramup_epochs * epoch + start_learning_rate
                elif epoch < ramup_epochs + sustain_epochs:
                    return max_learning_rate
                else:
                    return (max_learning_rate - min_learning_rate) * exp_decay ** (epoch - ramup_epochs - sustain_epochs) + min_learning_rate

            lr_callback = LearningRateScheduler(lambda epoch: learning_rate_scheduler(epoch) , verbose=0)

            model_checkpoint = ModelCheckpoint(filepath=CHECKPOINT_FILE_PATH,save_weights_only=True,monitor="val_loss",mode="min",save_best_only=True)

            early_stopping = EarlyStopping(patience=3,monitor="val_loss",mode="min",restore_best_weights=True)

            my_callbacks = [model_checkpoint, lr_callback, early_stopping]

            os.makedirs(os.path.dirname(CHECKPOINT_FILE_PATH), exist_ok=True)
            os.makedirs(MODEL_DIR, exist_ok=True)
            os.makedirs(WEIGHTS_DIR, exist_ok=True)

            try:
                history = model.fit(x = X_train_array, y = y_train, epochs=20, batch_size=batch_size, validation_data=(X_test_array, y_test), callbacks=my_callbacks, verbose=1)

                model.load_weights(CHECKPOINT_FILE_PATH)

                self.save_mode_weights(model)

                for epoch in range(len(history.history['loss'])):
                    train_loss = history.history['loss'][epoch]
                    val_loss = history.history['val_loss'][epoch]

                    self.experiment.log_metric("train_loss", train_loss, epoch=epoch)
                    self.experiment.log_metric("val_loss", val_loss, epoch=epoch)

                logger.info(f"Model trained successfully and saved at {MODEL_PATH}")
            except Exception as e:
                raise CustomException(e, sys)
            
        except Exception as e:
            logger.error(f"Error in training model: {e}")
            raise CustomException(e, sys)
    
    def extract_weights(self, layer_name, model):
        try:
            weight_layer = model.get_layer(layer_name)
            weights = weight_layer.get_weights()[0]
            weights = weights/np.linalg.norm(weights, axis=1).reshape(-1, 1)

            logger.info(f"Weights extracted successfully for {layer_name}")
            return weights
        except Exception as e:
            raise CustomException(e, sys)

    def save_mode_weights(self, model):
        try:
            model.save(MODEL_PATH)

            logger.info(f"Model saved at {MODEL_PATH}")

            user_weights = self.extract_weights('user_embedding', model)
            anime_weights = self.extract_weights('anime_embedding', model)

            joblib.dump(user_weights, USER_WEIGHTS_PATH)
            joblib.dump(anime_weights, ANIME_WEIGHTS_PATH)

            self.experiment.log_asset(MODEL_PATH)
            self.experiment.log_asset(USER_WEIGHTS_PATH)
            self.experiment.log_asset(ANIME_WEIGHTS_PATH)

            logger.info(f"Weights saved at {USER_WEIGHTS_PATH} and {ANIME_WEIGHTS_PATH}")
        except Exception as e:
            logger.error(f"Error in saving model weights: {e}")
            raise CustomException(e, sys)

if __name__ == "__main__":
    model_training = ModelTraining(data_path=PROCESSED_DIR)
    model_training.train_model()