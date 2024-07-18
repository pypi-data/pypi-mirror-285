import dataclasses
import functools
import typing

T = typing.TypeVar("T")
_ConvertFunc = typing.Callable[[str], T]


@dataclasses.dataclass(frozen=True)
class Converter(typing.Generic[T]):
    convert: _ConvertFunc[T]

    def __post_init__(self):
        if not callable(self.convert):
            raise ValueError(f"{self.convert} must be a callable function")

        # This is to force `type_` to immediately be evaluated
        if not self.type_:
            raise RuntimeError(f"self.type_ should already have been verified")

    @functools.cached_property
    def type_(self) -> type[T]:
        return_val = typing.get_type_hints(self.convert).get("return")

        if return_val is None:
            raise ValueError(f"{self.convert} must have a return type hint.")

        return return_val


class ConverterDict(dict[type, _ConvertFunc]):
    def __setitem__(self, key: type[T], value: _ConvertFunc[T]) -> None:
        super().__setitem__(key, value)

    def __getitem__(self, key: type[T]) -> _ConvertFunc[T]:
        return super().__getitem__(key)

    def __missing__(self, key: type[T]) -> _ConvertFunc[T]:
        raise KeyError(key)


def cast_to_bool(value: str) -> bool:
    if value.lower() in ("true", "1"):
        return True
    if value.lower() in ("false", "0"):
        return False
    raise ValueError(f"Unsupported boolean value: {value}")
