from typing import Callable

from consolemenu import ConsoleMenu
from consolemenu.items import FunctionItem, SubmenuItem
from edgegap_logging import Color, Format

from ..handlers import Namespace, View
from ._interface import BuilderInterface


class MenuBuilder(BuilderInterface):
    def _build(self) -> Callable:
        menu = self.__build_menu()

        return menu.show

    def __build_menu(self) -> ConsoleMenu:
        main_menu = ConsoleMenu(
            title=Format.squared(self._cli.name, Color.CYAN),
            subtitle=self._cli.description,
            clear_screen=False,
            exit_option_text='Quit',
            exit_menu_char='q',

        )

        for namespace in self._cli.namespaces.values():
            self.__build_submenu(namespace, main_menu)

        return main_menu

    def __build_submenu(self, namespace: Namespace, menu: ConsoleMenu):
        namespace_menu = ConsoleMenu(
            title=f'Namespace {Format.squared(namespace.name, Color.CYAN)}',
            subtitle=namespace.description,
            clear_screen=False,
            exit_menu_char='q',
        )

        for view in namespace.views.values():
            self.__build_function_item(view, namespace_menu)

        submenu = SubmenuItem(
            text=f'{Format.squared(namespace.name, Color.CYAN)} - {namespace.description}',
            submenu=namespace_menu,
            menu=menu,
        )
        menu.append_item(submenu)

    @staticmethod
    def __build_function_item(view: View, sub_menu: ConsoleMenu):
        item = FunctionItem(
            text=f'{Format.squared(view.name, Color.CYAN)} - {view.description}',
            function=view.exec,
        )
        sub_menu.append_item(item)
