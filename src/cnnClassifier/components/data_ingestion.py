import os
import subprocess
import sys
import zipfile
from pathlib import Path
from cnnClassifier import logger
from cnnClassifier.entity.config_entity import (DataIngestionConfig)


class DataIngestion:
    def __init__(self, config: DataIngestionConfig):
        self.config = config

    def download_file(self):
        """
        Fetch data from Kaggle
        """
        try:
            dataset_id = self.config.source_URL
            root_dir = Path(self.config.root_dir)
            zip_download_path = Path(self.config.local_data_file)
            os.makedirs(root_dir, exist_ok=True)

            logger.info(f"Downloading data from Kaggle dataset {dataset_id} into {root_dir}")

            kaggle_cli = Path(sys.executable).with_name("kaggle")
            subprocess.run(
                [str(kaggle_cli), "datasets", "download", "-d", dataset_id, "-p", str(root_dir)],
                check=True,
            )

            downloaded_zip = next(root_dir.glob("*.zip"))
            if downloaded_zip != zip_download_path:
                downloaded_zip.rename(zip_download_path)

            logger.info(f"Downloaded data from Kaggle dataset {dataset_id} into file {zip_download_path}")

        except Exception as e:
            raise e

    def extract_zip_file(self):
        """
        zip_file_path: str
        Extracts the zip file into the data directory
        Function returns None
        """
        unzip_path = self.config.unzip_dir
        os.makedirs(unzip_path, exist_ok=True)
        with zipfile.ZipFile(self.config.local_data_file, 'r') as zip_ref:
            zip_ref.extractall(unzip_path)