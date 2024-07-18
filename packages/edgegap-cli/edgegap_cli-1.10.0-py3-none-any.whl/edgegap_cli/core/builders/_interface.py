from abc import ABC, abstractmethod
from typing import Callable

from ..handlers import CLI


class BuilderInterface(ABC):
    def __init__(self, cli: CLI):
        self._cli = cli

    @abstractmethod
    def _build(self) -> Callable:
        """Build the instance"""

    def run(self):
        func = self._build()
        func()
