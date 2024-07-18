from typing import Callable

import click

from ..handlers import Namespace, View
from ._interface import BuilderInterface


class TerminalBuilder(BuilderInterface):
    no_input = False

    def _build(self) -> Callable:
        return self.__build_cli()

    def __build_cli(self) -> Callable:
        @click.group(name=self._cli.name)
        @click.option('--no-input', '-n', is_flag=True)
        def cli(no_input: bool):
            """Main CLI entry point."""
            self.no_input = no_input

        for namespace in self._cli.namespaces.values():
            self.__build_namespace(namespace, cli)

        return cli

    def __build_namespace(self, namespace: Namespace, cli: click.Group):
        @click.group(name=namespace.name)
        def namespace_cli():
            """Namespace"""

        for view in namespace.views.values():
            self.__build_view(view, namespace_cli)

        cli.add_command(namespace_cli)

    def __build_view(self, view: View, namespace_cli: click.Group):
        params = []

        for name, attribute in view.signature.parameters.items():
            if attribute.annotation in view.accepted_cls:
                options = [f'--{attribute.name}']

                option = click.Option(
                    options,
                    is_flag=attribute.annotation is bool,
                    type=attribute.annotation,
                )
                params.append(option)

        @namespace_cli.command(view.name, params=params)
        def cli_function(*args, **kwargs):
            view.exec(no_input=self.no_input, *args, **kwargs)
