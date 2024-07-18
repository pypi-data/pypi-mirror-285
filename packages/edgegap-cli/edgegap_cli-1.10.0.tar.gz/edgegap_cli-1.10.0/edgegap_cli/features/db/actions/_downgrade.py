from logging import Logger

from alembic import command, config

from edgegap_cli.core.handlers import Depends

from .._config import get_or_raise_alembic_config
from .._namespace import namespace


@namespace.view(
    name='downgrade',
    description='Allow to downgrade the database (-1 means one step back)',
    confirm_message='Downgrade the database?',
)
def db_downgrade(
    logger: Logger,
    revision: str = '-1',
    alembic_config: config.Config = Depends(get_or_raise_alembic_config),
):
    logger.info(f'Downgrading database to {revision}')
    command.downgrade(alembic_config, revision)
    logger.info('Database downgrade complete!')
