import os
from logging import Logger

from alembic import command
from alembic.config import Config
from edgegap_logging import Color, Format

from edgegap_cli.core.handlers import Depends

from .._config import get_or_default_alembic_config
from .._namespace import namespace

init_message = f"""
    \nAlembic Migration Initialization Complete!
    You will need to edit those files:
    - {Format.squared('alembic.ini', Color.GREEN)}
       - Recommend to change the file template to:
            file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d%%(second).2d_%%(rev)s

    - {Format.squared('migrations/env.py', Color.GREEN)}
        - Change the URL for the database and the Target Model
            - you can simple change for sqlmodel.SQLModel if you are using sqlmodel

    - {Format.squared('migrations/script.py.mako', Color.GREEN)}
        - if you are using sqlmodel, you will need to add this at the top of the imports:
            import sqlmodel
    """


@namespace.view(
    name='init',
    description='Initialize the Alembic Migrations System',
    confirm_message='Initialize the Alembic Migrations?',
)
def db_init(
    logger: Logger,
    folder: str = '.',
    alembic_config: Config = Depends(get_or_default_alembic_config),
):
    logger.info('Running the Alembic migration init command')
    migrations_folder = os.path.join(folder, 'migrations')

    if alembic_config.config_file_name is None:
        alembic_config.config_file_name = os.path.join(folder, 'alembic.ini')

    command.init(alembic_config, migrations_folder)
    logger.info(init_message)
