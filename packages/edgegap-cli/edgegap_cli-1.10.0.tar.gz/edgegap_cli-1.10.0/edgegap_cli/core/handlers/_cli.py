import logging
import sys

from edgegap_logging import Color, Format

from ..models import CLIModel
from ._namespace import Namespace

logger = logging.getLogger('scheduler.cli')


class CLI:
    def __init__(self, name: str, description: str, namespaces: list[Namespace] = None) -> None:
        self.__cli = CLIModel(
            name=name,
            description=description,
        )
        self.__namespace = {ns.name: ns for ns in namespaces} if namespaces else {}

    def add_namespace(self, namespace: Namespace):
        if namespace.name in self.namespaces.keys():
            raise ValueError(f'Namespace {namespace.name} already exists')

        self.namespaces[namespace.name] = namespace

    @property
    def namespaces(self) -> dict[str, Namespace]:
        return self.__namespace

    @property
    def name(self):
        return self.__cli.name

    @property
    def description(self):
        return self.__cli.description

    def run(self):
        try:
            if len(sys.argv) > 1:
                self.__run_cli()
            else:
                self.__run_ui()

            self.__exit_message()
        except KeyboardInterrupt:
            print(
                f"\n{Format.squared('Keyboard Interrupted', Color.YELLOW)}"
                f"\n{Format.color('See ya!', Color.MAGENTA)}",
            )
        except Exception as e:
            raise Exception(Format.color('What did you break again?', Color.RED)) from e

    def __run_cli(self):
        from ..builders import TerminalBuilder

        builder = TerminalBuilder(self)
        builder.run()

    def __run_ui(self):
        from ..builders import MenuBuilder

        builder = MenuBuilder(self)
        builder.run()

    def __exit_message(self):
        print(
            f"{Format.squared(self.__cli.name, Color.CYAN)}"
            f'\nThank you for using this CLI'
            f"\n{Format.color('Have a nice day!', Color.MAGENTA)}",
        )
