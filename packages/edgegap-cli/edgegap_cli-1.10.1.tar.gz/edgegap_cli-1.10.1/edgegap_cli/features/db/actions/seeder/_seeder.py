import sys
from logging import Logger

from pydantic import PostgresDsn, SecretStr

from ..._namespace import namespace
from ._handler import SeederHandler
from ._loader import SeederLoader


@namespace.view(
    name='seed',
    description='Seed the Data from the JSON in the database',
    confirm_message='Seed the Database with JSON?',
)
def db_seed(
        logger: Logger,
        uri: SecretStr,
        folder: str,
):
    uri = uri.get_secret_value()

    if uri == "stdin":
        uri = sys.stdin.read().strip()

    logger.info(f"Reading JSON files from {folder}")
    loader = SeederLoader(
        json_folder=folder,
        logger=logger,
    )
    seeds = loader.load()

    uri = PostgresDsn(uri)
    seeder = SeederHandler(
        uri=uri,
        logger=logger,
        seeds=seeds,
    )
    seeder.seed()
