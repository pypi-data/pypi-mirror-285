from logging import Logger

from alembic import command, config

from edgegap_cli.core.handlers import Depends

from .._config import get_or_raise_alembic_config
from .._namespace import namespace


@namespace.view(
    name='current',
    description='Show the Current Migrations',
)
def db_current(
    logger: Logger,
    alembic_config: config.Config = Depends(get_or_raise_alembic_config),
):
    logger.info('Current Database Migration')
    command.current(alembic_config)
