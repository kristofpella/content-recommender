import os
import sys
import pandas as pd
from google.cloud import storage
from google.oauth2 import service_account
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *
from utils.common_functions import read_yaml_file

logger = get_logger(__name__)

class DataIngestion:
    def __init__(self, config):
        self.config = config["data_ingestion"]
        self.bucket_name = self.config["bucket_name"]
        self.credentials_file_name = self.config["credentials_file_name"]
        self.file_names = self.config["bucket_file_names"]

        os.makedirs(RAW_DIR, exist_ok=True)

    def download_csv_from_gcp(self):
        try:
            # Get the path to the credentials file
            credentials_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                          self.credentials_file_name)
            
            # Load credentials and create client
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            client = storage.Client(credentials=credentials, project=credentials.project_id)
            bucket = client.bucket(self.bucket_name)

            for file_name in self.file_names:
                file_path = os.path.join(RAW_DIR, file_name)

                if file_name == 'animelist.csv':
                    blob = bucket.blob(file_name)
                    blob.download_to_filename(file_path)

                    data = pd.read_csv(file_path, nrows=5000000)
                    data.to_csv(file_path, index=False)

                    logger.info(f"Large file detected and only first 5000000 rows are loaded")
                else:
                    blob = bucket.blob(file_name)
                    blob.download_to_filename(file_path)

                    logger.info(f"File {file_name} downloaded successfully")

        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            raise CustomException(f"Error downloading file: {e}", sys)
    
    def run(self):
        try:
            logger.info(f"Data ingestion started")
            self.download_csv_from_gcp()
        except CustomException as ce:
            logger.error(f"Error in data ingestion: {str(ce)}")
            raise CustomException(f"Error in data ingestion: {str(ce)}", sys)
        finally:
            logger.info(f"Data ingestion completed")

if __name__ == "__main__":
    config = read_yaml_file(CONFIG_PATH)
    data_ingestion = DataIngestion(config)
    data_ingestion.run()