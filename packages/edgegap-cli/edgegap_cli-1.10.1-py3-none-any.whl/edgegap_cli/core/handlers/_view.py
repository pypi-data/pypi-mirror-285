import inspect
import logging
import os
from logging import Logger
from typing import Any, Callable

from edgegap_logging import Color, Format
from pydantic import PostgresDsn, SecretStr

from .. import handlers
from ..models import ViewModel
from ._depends import Depends

clear = 'cls' if os.name == 'nt' else 'clear'


class View:
    __accepted_cls = [str, int, float, bool, SecretStr, PostgresDsn]

    def __init__(
            self,
            name: str,
            description: str,
            func: Callable,
            confirm_message: str = None,
            wait_on_exit: bool = True,
            logger: Logger = None,
    ):
        self.__view = ViewModel(
            name=name,
            description=description,
            func=func,
            confirm_message=confirm_message,
            wait_on_exit=wait_on_exit,
        )
        self.__logger = logger

    @property
    def accepted_cls(self):
        return self.__accepted_cls

    @property
    def name(self) -> str:
        return self.__view.name

    @property
    def description(self) -> str:
        return self.__view.description

    @property
    def confirm(self) -> bool:
        return isinstance(self.__view.confirm_message, str)

    @property
    def wait_on_exit(self) -> bool:
        return self.__view.wait_on_exit

    @property
    def signature(self) -> inspect.Signature:
        return inspect.signature(self.__view.func)

    def __pre_execute(self, no_input: bool, **kwargs) -> tuple[bool, dict]:
        print(f'\nExecuting view {Format.squared(self.name, Color.CYAN)}')
        should_proceed = True

        kwargs = self.__parse_kwargs(no_input, **kwargs)

        if self.confirm:
            print('\nParameters:')

            for key, value in kwargs.items():
                print(f' - {Format.squared(key, Color.CYAN)}: {value}')

            if no_input:
                print('\nNo Input detected, will not confirm...')
            else:
                confirmation = input(
                    f"\n{self.__view.confirm_message}\nProceed? {Format.squared('y/n', Color.GREEN)} ",
                )

                should_proceed = confirmation.lower() == 'y'

        return should_proceed, kwargs

    def exec(self, no_input: bool = False, *args, **kwargs):
        should_proceed, kwargs = self.__pre_execute(no_input, **kwargs)

        if should_proceed:
            self.__view.func(*args, **kwargs)
        else:
            self.__cancel_operation()

        self.__post_execute(no_input)

    def __cancel_operation(self):
        print(f'\nView {Format.squared(self.name, Color.YELLOW)} cancelled')

    def __post_execute(self, no_input: bool = False):
        if self.wait_on_exit and not no_input:
            input('Press Enter to exit...')

    def __parse_kwargs(self, no_input: bool, **kwargs) -> dict[str, Any]:
        cleaned_kwargs = {key: value for key, value in kwargs.items() if value is not None}
        missing_params = [
            param for param in self.signature.parameters.values() if param.name not in cleaned_kwargs.keys()
        ]

        for param in missing_params:
            if isinstance(param.default, Depends) or param.annotation not in self.accepted_cls:
                kwargs[param.name] = self.__parse_value(param)
            else:
                kwargs[param.name] = self.__ask_for_value(param, no_input)

        return kwargs

    @staticmethod
    def __ask_for_value(param: inspect.Parameter, no_input: bool) -> Any:
        message = f'Parameter {Format.squared(param.name, Color.CYAN)} - '

        if param.default is not param.empty:
            message += 'default=' + Format.parentheses(f'{param.default}', Color.GREEN) + ' '

        message += '\nEnter a value or press Enter to use the default: '

        if no_input:
            print('No Input detected, will not ask for parameters values')

        have_default = param.default is not param.empty

        if no_input:
            input_or_default = param.default if have_default else None
        else:
            input_or_default = input(message).strip() or param.default

        return param.annotation(input_or_default) if input_or_default is not None else None

    def __parse_value(self, param) -> Any:
        match param.annotation:
            case logging.Logger:
                return logging.getLogger(f'view.{self.name}')

        match type(param.default):
            case handlers.Depends:
                return param.default.dependency()
            case _:
                raise TypeError(f'Unexpected type {param.annotation}')
