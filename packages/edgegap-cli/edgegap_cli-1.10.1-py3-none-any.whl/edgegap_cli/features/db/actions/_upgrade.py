from logging import Logger

from alembic import command, config

from edgegap_cli.core.handlers import Depends

from .._config import get_or_raise_alembic_config
from .._namespace import namespace


@namespace.view(
    name='upgrade',
    description='Upgrade the database to the revision (head mean the last one)',
    confirm_message='Upgrade the database?',
)
def db_upgrade(
    logger: Logger,
    revision: str = 'head',
    alembic_config: config.Config = Depends(get_or_raise_alembic_config),
):
    logger.info(f'Upgrading database to {revision}')
    command.upgrade(alembic_config, revision)
    logger.info('Database upgrade complete!')
