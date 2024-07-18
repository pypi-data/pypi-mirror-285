from typing import Callable


class Depends:
    def __init__(self, dependency: Callable):
        self.dependency = dependency
