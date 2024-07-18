from logging import Logger

from alembic import command, config

from edgegap_cli.core.handlers import Depends

from .._config import get_or_raise_alembic_config
from .._namespace import namespace


@namespace.view(
    name='migrate',
    description='Create the database Migrations',
    confirm_message='Create the Database migration?',
)
def db_migrate(
    logger: Logger,
    message: str = 'Default Migration Message, please change me!',
    alembic_config: config.Config = Depends(get_or_raise_alembic_config),
):
    logger.info(f'Creating Migrations with message: {message}')
    command.revision(alembic_config, message=message, autogenerate=True)
    logger.info('Database upgrade complete!')
