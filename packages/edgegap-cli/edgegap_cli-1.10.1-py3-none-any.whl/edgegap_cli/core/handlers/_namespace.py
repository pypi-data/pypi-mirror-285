import inspect
import logging

from ..models import NamespaceModel
from ._view import View


class Namespace:
    def __init__(self, name: str, description: str, views: list[View] = None):
        self.__namespace = NamespaceModel(
            name=name,
            description=description,
        )
        self.__views = {view.name: view for view in views} if views else {}

    @property
    def name(self) -> str:
        return self.__namespace.name

    @property
    def description(self) -> str:
        return self.__namespace.description

    @property
    def views(self) -> dict[str, View]:
        return self.__views

    def view(
        self,
        name: str = None,
        description: str = None,
        confirm_message: str = None,
        wait_on_exit: bool = True,
    ):
        def decorator(func):
            _description = description or inspect.getdoc(func)
            _name = name or func.__name__
            _name = _name.replace(' ', '-').lower()
            _view = View(
                name=_name,
                description=_description,
                func=func,
                confirm_message=confirm_message,
                wait_on_exit=wait_on_exit,
                logger=logging.getLogger(f'{self.name}.{_name}'),
            )
            self.add_view(_view)

        return decorator

    def add_view(self, view: View):
        if view.name in self.__views.keys():
            raise ValueError(f'View {view.name} already exists')

        self.__views[view.name] = view
