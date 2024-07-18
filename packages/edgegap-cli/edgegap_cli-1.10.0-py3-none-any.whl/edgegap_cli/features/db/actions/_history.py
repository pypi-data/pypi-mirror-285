from logging import Logger

from alembic import command, config

from edgegap_cli.core.handlers import Depends

from .._config import get_or_raise_alembic_config
from .._namespace import namespace


@namespace.view(
    name='history',
    description='Show the History of Migrations',
)
def db_history(
    logger: Logger,
    alembic_config: config.Config = Depends(get_or_raise_alembic_config),
):
    logger.info('Getting History of Migrations')
    command.history(alembic_config, indicate_current=True)
