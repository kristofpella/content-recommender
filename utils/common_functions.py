import os
from src.logger import get_logger
from src.custom_exception import CustomException
import yaml

logger = get_logger(__name__)

def read_yaml_file(file_path: str) -> dict:
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist")
        
        with open(file_path, 'r') as yaml_file:
            file = yaml.safe_load(yaml_file)
            logger.info(f"File loaded successfully from {file_path}")
            return file

    except Exception as e:
        logger.error(f"Error loading file {file_path}: {e}")
        raise CustomException(f"Error loading file {file_path}", e)