from __future__ import annotations

import typing
from argparse import Action, FileType

from easydatamodel._typing import UNASSIGNED, UnassignedType, is_optional_type
from easydatamodel.field import FieldInfo

from cli_buddy.exceptions import InvalidArgumentError

T = typing.TypeVar("T")

if typing.TYPE_CHECKING:
    from .cli import CLI


class ArgParseKwargs(typing.Generic[T], typing.TypedDict):
    action: typing.NotRequired[str | type[Action]]
    nargs: typing.NotRequired[int | typing.Literal["?", "*", "+", "...", "A...", "==SUPPRESS=="]]
    const: typing.NotRequired[typing.Any]
    default: typing.NotRequired[typing.Any]
    type: typing.NotRequired[typing.Callable[[str], T] | FileType]
    choices: typing.NotRequired[typing.Iterable[T]]
    required: typing.NotRequired[bool]
    help: typing.NotRequired[str]
    metavar: typing.NotRequired[str | tuple[str, ...]]
    version: typing.NotRequired[str]


def Argument(*flags: str, **kwargs: typing.Unpack[ArgParseKwargs[T]]) -> typing.Any:
    """Provide specific configuration information for an easydatamodel column.

    Attributes:
        default: default column value.
        default_factory: 0-argument function called to initialize a column's value.
        type: the type of the column. If not provided, the type will be inferred from the type hints.
        choices: If provided, allowed values for the column.

    Returns:
        A `FieldInfo` object. Return type is `Any` so it plays nicely with your type checker.

    Raises:
        InvalidFieldError:
            - if default and default_factory are both set.
            - if init is False and default or default_factory is not set.
            - if a column's type cannot be determined.
    """
    return ArgumentInfo(*flags, **kwargs)


class ArgumentInfo(FieldInfo):
    """Represents a column in a cli-buddy model.

    Attributes:
        default: default column value.
        default_factory: 0-argument function called to initialize a column's value.
        type: the type of the column. If not provided, the type will be inferred from the type hints.
        choices: If provided, allowed values for the column.
        name: the name of the column. This will usually be set by the metaclass unless you know what you're doing.

    Raises:
        InvalidFieldError:
            - if default and default_factory are both set.
            - if init is False and default or default_factory is not set.
            - if a column's type cannot be determined.
    """

    flags: tuple[str, ...]
    argparse_kwargs: ArgParseKwargs[typing.Any]

    def __init__(
        self,
        *flags: str,
        name: str | UnassignedType[str] = UNASSIGNED,
        field_type: typing.Any | UnassignedType[typing.Any] = UNASSIGNED,
        **argparse_kwargs: typing.Unpack[ArgParseKwargs[typing.Any]],
    ) -> None:
        for flag in flags:
            if not flag.startswith("-"):
                raise InvalidArgumentError(f"Flags must start with a '-' or '--'. Got: {flag}")
        if "required" in argparse_kwargs:
            if len(flags) == 0:
                raise InvalidArgumentError("'required' argument is prohibited for positional arguments.")
            required = argparse_kwargs["required"]
            if required is True and "default" in argparse_kwargs:
                raise InvalidArgumentError("Cannot have a required argument with a default value.")
        default = argparse_kwargs.get("default", UNASSIGNED)
        if default is not UNASSIGNED and "default: " not in argparse_kwargs.get("help", ""):
            argparse_kwargs["help"] = f"{argparse_kwargs.get('help', '')} (default: {default})"
        default_factory = UNASSIGNED
        argparse_type = argparse_kwargs.get("type", UNASSIGNED)
        if isinstance(default, str) and argparse_type is not UNASSIGNED:
            default_factory = lambda: argparse_type(default)  # noqa: E731
            default = UNASSIGNED
        super().__init__(
            name=name,
            default=default,
            default_factory=default_factory,
            type=field_type,
            const=True,
            choices=argparse_kwargs.get("choices"),
        )
        self.flags = flags
        self.argparse_kwargs = argparse_kwargs

    @classmethod
    def from_annotation(cls, name: str, type: UNASSIGNED) -> typing.Self:
        return cls(name=name, field_type=type, type=type)

    @classmethod
    def from_namespace(cls, name: str, default: typing.Any, type: typing.Any) -> typing.Self:
        return cls(name=name, default=default, field_type=type)

    def __repr__(self) -> str:
        argparse_args = ", ".join(
            [f"flags={self.flags}", ", ".join(f"{k}={v!r}" for k, v in self.argparse_kwargs.items())]
        )
        return super().__repr__()[:-1] + f" argparse_args={{{argparse_args}}}>"

    def __set_name__(self, owner: type["CLI"], name: str) -> None:  # type: ignore
        super().__set_name__(owner, name)  # type: ignore
        is_flag = False
        if len(self.flags) > 0:
            is_flag = True
        elif "required" in self.argparse_kwargs:
            is_flag = True
        elif "default" in self.argparse_kwargs:
            is_flag = True
        elif self.type is bool:
            is_flag = True
        else:
            is_flag = False
        if is_flag:
            main_flag = f"--{name}" if len(name) > 1 else f"-{name}"
            if main_flag not in self.flags:
                self.flags += (main_flag,)
        if self.type is bool and "action" not in self.argparse_kwargs:
            action = "store_true" if self.argparse_kwargs.get("default") is not True else "store_false"
            self.argparse_kwargs["action"] = action
            self.argparse_kwargs.pop("type", None)

        elif not is_optional_type(self.type) and is_flag and "default" not in self.argparse_kwargs:
            self.argparse_kwargs["required"] = True

    def copy(self) -> ArgumentInfo:
        """Return a copy of the field without its owner and name values set so it can be used in another class."""
        return self.__class__(*self.flags, name=self.name, **self.argparse_kwargs)
