from logging import config

from edgegap_logging import LoggingConfiguration

from edgegap_cli import CLI, features

log_config = LoggingConfiguration()
config.dictConfig(log_config.model_dump())

cli = CLI(
    name='Edgegap',
    description='The Official Edgegap CLI since 2024',
)
cli.add_namespace(features.db.namespace)

if __name__ == '__main__':
    cli.run()
