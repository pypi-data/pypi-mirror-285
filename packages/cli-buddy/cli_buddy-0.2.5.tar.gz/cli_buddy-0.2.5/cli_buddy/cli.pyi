from .argument import ArgumentInfo as ArgumentInfo
from easydatamodel.model import _GenericModel
from typing import Any

class CLI(_GenericModel[ArgumentInfo]):
    __field_class__ = ArgumentInfo
    def __init__(self) -> None: ...
    def __call__(self) -> Any: ...
