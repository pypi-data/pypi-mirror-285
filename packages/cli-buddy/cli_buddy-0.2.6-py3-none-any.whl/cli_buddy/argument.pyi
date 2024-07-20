import typing
from .cli import CLI as CLI
from argparse import Action, FileType
from cli_buddy.exceptions import InvalidArgumentError as InvalidArgumentError
from easydatamodel._typing import UNASSIGNED, UnassignedType as UnassignedType
from easydatamodel.field import FieldInfo

T = typing.TypeVar('T')

class ArgParseKwargs(typing.TypedDict, typing.Generic[T]):
    action: typing.NotRequired[str | type[Action]]
    nargs: typing.NotRequired[int | typing.Literal['?', '*', '+', '...', 'A...', '==SUPPRESS==']]
    const: typing.NotRequired[typing.Any]
    default: typing.NotRequired[typing.Any]
    type: typing.NotRequired[typing.Callable[[str], T] | FileType]
    choices: typing.NotRequired[typing.Iterable[T]]
    required: typing.NotRequired[bool]
    help: typing.NotRequired[str]
    metavar: typing.NotRequired[str | tuple[str, ...]]
    version: typing.NotRequired[str]

def Argument(*flags: str, **kwargs: typing.Unpack[ArgParseKwargs[T]]) -> typing.Any: ...

class ArgumentInfo(FieldInfo):
    flags: tuple[str, ...]
    argparse_kwargs: ArgParseKwargs[typing.Any]
    def __init__(self, *flags: str, name: str | UnassignedType[str] = ..., field_type: typing.Any | UnassignedType[typing.Any] = ..., **argparse_kwargs: typing.Unpack[ArgParseKwargs[typing.Any]]) -> None: ...
    @classmethod
    def from_annotation(cls, name: str, type: UNASSIGNED) -> typing.Self: ...
    @classmethod
    def from_namespace(cls, name: str, default: typing.Any, type: typing.Any) -> typing.Self: ...
    def __set_name__(self, owner: type['CLI'], name: str) -> None: ...
    def copy(self) -> ArgumentInfo: ...
