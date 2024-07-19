from .argument import ArgumentInfo as ArgumentInfo
from easydatamodel.model import Model
from typing import Any

class CLI(Model[ArgumentInfo]):
    __field_class__ = ArgumentInfo
    def __init__(self) -> None: ...
    def __call__(self) -> Any: ...
