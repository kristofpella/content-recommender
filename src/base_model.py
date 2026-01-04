import tensorflow as tf
from utils.common_functions import read_yaml_file
from src.logger import get_logger
from src.custom_exception import CustomException
import sys


# Import Keras components through tf.keras for better IDE resolution
Model = tf.keras.models.Model
Input = tf.keras.layers.Input
Embedding = tf.keras.layers.Embedding
Flatten = tf.keras.layers.Flatten
Dot = tf.keras.layers.Dot
Dense = tf.keras.layers.Dense
BatchNormalization = tf.keras.layers.BatchNormalization
Activation = tf.keras.layers.Activation

logger = get_logger(__name__)

class BaseModel:
    def __init__(self, config_path):
        try:
            self.config = read_yaml_file(config_path)
            logger.info(f"Config file loaded successfully")

        except Exception as e:
            raise CustomException(e, sys)

    def RecommenderNet(self, n_users, n_anime):
        try:
            embedding_size = self.config['model']['embedding_size']
            user = Input(name='user', shape=[1])

            user_embedding = Embedding(name='user_embedding', input_dim=n_users, output_dim=embedding_size)(user)

            anime = Input(name='anime', shape=[1])

            anime_embedding = Embedding(name='anime_embedding', input_dim=n_anime, output_dim=embedding_size)(anime)

            x = Dot(name='dot_product', normalize=True, axes=2)([user_embedding, anime_embedding])
            x = Flatten()(x)
            x = Dense(1, kernel_initializer='he_normal')(x)
            x = BatchNormalization()(x)
            x = Activation('sigmoid')(x)

            model = Model([user, anime], outputs=x)

            model.compile(loss=self.config['model']['loss'], optimizer=self.config['model']['optimizer'], metrics=self.config['model']['metrics'])

            logger.info(f"Model compiled successfully")

            return model
        
        except Exception as e:
            raise CustomException(e, sys)