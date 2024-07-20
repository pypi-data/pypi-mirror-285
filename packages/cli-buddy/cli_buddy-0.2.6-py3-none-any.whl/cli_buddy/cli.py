from __future__ import annotations

from argparse import ArgumentParser
from typing import Any

from easydatamodel.model import _GenericModel  # type: ignore

from .argument import ArgumentInfo


class CLI(_GenericModel[ArgumentInfo]):
    """Base class for cli_buddy CLIs."""

    __field_class__ = ArgumentInfo

    def __init__(self):
        parser = ArgumentParser(description=self.__doc__)
        for field in self.__fields_map__.values():
            if not field.classfield:
                parser.add_argument(*field.flags, **field.argparse_kwargs, dest=field.name)
        super().__init__(**vars(parser.parse_args()))
        self()

    def __call__(self) -> Any:
        pass
