import pandas as pd
import os
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *
import sys

logger = get_logger(__name__)

class DataProcessing:
    def __init__(self, input, output_dir):
        self.input_file = input
        self.output_dir = output_dir

        self.rating_df = None
        self.anime_df = None
        self.X_train_array = None
        self.X_test_array = None
        self.y_train = None
        self.y_test = None

        self.user_to_user_encoded = {}
        self.user_to_user_decoded = {}
        self.anime_to_anime_encoded = {}
        self.anime_to_anime_decoded = {}

        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info(f"Data processing initialized")

    
    def load_data(self, usecols):
        try:
            self.rating_df = pd.read_csv(self.input_file, usecols=usecols, low_memory=True)
            logger.info(f"Rating data loaded successfully")
        except Exception as e:
            raise CustomException(e, sys)

    def filter_users(self, min_ratings = 400):
        try:
            n_ratings = self.rating_df['user_id'].value_counts()
            self.rating_df = self.rating_df[self.rating_df['user_id'].isin(n_ratings[n_ratings >= min_ratings].index)].copy()
            logger.info(f"Users filtered successfully")
        
        except Exception as e:
            raise CustomException(e, sys)

    def scale_rating(self):
        try:
            min_rating = min(self.rating_df['rating'])
            max_rating = max(self.rating_df['rating'])
            self.rating_df['rating'] = self.rating_df['rating'].apply(lambda x: (x-min_rating)/(max_rating-min_rating)).values.astype(np.float64)
            logger.info(f"Rating scaled successfully")
        except Exception as e:
            raise CustomException(e, sys)

    def encode_data(self):
        try:
            user_ids = self.rating_df['user_id'].unique().tolist()
            self.user_to_user_encoded = {x: i for i, x in enumerate(user_ids)}
            self.user_to_user_decoded = {i: x for i, x in enumerate(user_ids)}
            self.rating_df['user'] = self.rating_df['user_id'].map(self.user_to_user_encoded)
            logger.info(f"Users encoded successfully")

            anime_ids = self.rating_df['anime_id'].unique().tolist()
            self.anime_to_anime_encoded = {x: i for i, x in enumerate(anime_ids)}
            self.anime_to_anime_decoded = {i: x for i, x in enumerate(anime_ids)}
            self.rating_df['anime'] = self.rating_df['anime_id'].map(self.anime_to_anime_encoded)
            logger.info(f"Animes encoded successfully")

        except Exception as e:
            raise CustomException(e, sys)
    
    def split_data(self, test_size = 1000, random_state = 43):
        try:
            self.rating_df = self.rating_df.sample(frac=1, random_state=random_state).reset_index(drop=True)

            X = self.rating_df[['user', 'anime']].values
            y = self.rating_df['rating'].values

            train_indices = self.rating_df.shape[0] - test_size

            X_train, X_test, y_train, y_test = (
                X[:train_indices],
                X[train_indices:],
                y[:train_indices],
                y[train_indices:]
            )

            self.X_train_array = [X_train[:, 0], X_train[:, 1]]
            self.X_test_array = [X_test[:, 0], X_test[:, 1]]
            self.y_train = y_train
            self.y_test = y_test

            logger.info(f"Data split successfully")
        except Exception as e:
            raise CustomException(e, sys)

    def save_artifacts(self):
        try:
            artifacts = {
                'user_to_user_encoded': self.user_to_user_encoded,
                'user_to_user_decoded': self.user_to_user_decoded,
                'anime_to_anime_encoded': self.anime_to_anime_encoded,
                'anime_to_anime_decoded': self.anime_to_anime_decoded,
            }

            for name, data in artifacts.items():
                joblib.dump(data, os.path.join(self.output_dir, f"{name}.pkl"))
                logger.info(f"Artifact {name} saved successfully")

            joblib.dump(self.X_train_array, X_TRAIN_ARRAY)
            joblib.dump(self.X_test_array, X_TEST_ARRAY)
            joblib.dump(self.y_train, Y_TRAIN)
            joblib.dump(self.y_test, Y_TEST)

            self.rating_df.to_csv(RATING_DF, index=False)
            logger.info(f"Artifacts saved successfully")
        except Exception as e:
            raise CustomException(e, sys)

    def process_anime_data(self):
        try:
            anime_df = pd.read_csv(ANIME_CSV)
            cols = ['MAL_ID', 'Name', 'Genres', 'synopsis']
            synopsis_df = pd.read_csv(ANIME_WITH_SYNOPSIS_CSV, usecols=cols)

            anime_df = anime_df.replace('Unknown', np.nan)

            def get_anime_name(anime_id):
                try:
                    name = anime_df[anime_df['anime_id'] == anime_id].eng_version.values[0]

                    if name is np.nan:
                        name = anime_df[anime_df['anime_id'] == anime_id].Name.values[0]
    
                except:
                    print(f'{anime_id} not found')

                return name

            anime_df['anime_id'] = anime_df['MAL_ID']
            anime_df['eng_version'] = anime_df['English name']
            anime_df['eng_version'] = anime_df.anime_id.apply(lambda x: get_anime_name(x))

            anime_df.sort_values(by='Score', inplace=True, ascending=False, kind='quicksort', na_position='last')

            anime_df = anime_df[['anime_id', 'eng_version', 'Score', "Genres", 'Episodes', 'Type', 'Premiered', 'Members']]

            anime_df.to_csv(ANIME_DF, index=False)
            synopsis_df.to_csv(SYNOPSIS_DF, index=False)

            logger.info(f"Anime data processed successfully")
        except Exception as e:
            raise CustomException(e, sys)

    def run(self):
        try:
            self.load_data(usecols=['user_id', 'anime_id', 'rating'])
            self.filter_users()
            self.scale_rating()
            self.encode_data()
            self.split_data()
            self.save_artifacts()
            self.process_anime_data()

            logger.info(f"Data processing completed successfully")
        except Exception as e:
            raise CustomException(e, sys)

if __name__ == "__main__":
    data_processing = DataProcessing(ANIMELIST_CSV, PROCESSED_DIR)
    data_processing.run()

