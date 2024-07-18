import logging
import os

from alembic.config import Config

logger = logging.getLogger('cli.alembic')


def get_or_default_alembic_config() -> Config:
    cwd = os.getcwd()

    for dir_path, dir_names, file_names in os.walk(cwd):
        for file_name in [f for f in file_names if f.endswith('.ini')]:
            if file_name == 'alembic.ini':
                return Config(os.path.join(dir_path, file_name))

    return Config()


def get_or_raise_alembic_config() -> Config:
    alembic_config = get_or_default_alembic_config()

    if alembic_config is None or alembic_config.config_file_name is None:
        raise RuntimeError("Please run the 'edgegap db init' command first!")

    return alembic_config
