import glob
import json
import logging
import os

from ._models import SeederModel


class SeederLoader:
    def __init__(self, json_folder: str, logger: logging.Logger):
        if not os.path.isdir(json_folder):
            raise ValueError(f"'{json_folder}' is not a directory")

        self.json_folder = json_folder
        self.__logger = logger

    def __find_json_files(self) -> list[str]:
        base_dir = glob.glob(os.path.join(self.json_folder, "*.json"))
        sub_dir = glob.glob(os.path.join(self.json_folder, "*", '*.json'))

        files = base_dir + sub_dir
        self.__logger.debug(f"Loaded {len(files)} files to seed")

        return files

    @staticmethod
    def __load(json_file: str) -> SeederModel:
        if not os.path.isfile(json_file):
            raise ValueError(f"'{json_file}' is not a file")

        with open(json_file, "r") as f:
            return SeederModel(**json.load(f))

    def load(self) -> [SeederModel]:
        models = []

        for json_file in self.__find_json_files():
            try:
                self.__logger.debug(f"Loading {json_file}")
                models.append(self.__load(json_file))
            except Exception as e:
                self.__logger.error(f"Error loading {json_file} Skipping!: {e}")

        return models
