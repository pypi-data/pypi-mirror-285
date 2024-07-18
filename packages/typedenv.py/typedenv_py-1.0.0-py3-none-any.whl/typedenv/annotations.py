import types
import typing


def get_unioned_with_none(t: typing.Any) -> typing.Any:
    """Parses an annotation that Unions a type with None and returns that type.
    If multiple types are Unioned with None, they are combined into a single Union.

    Example:
    - typing.Union[int, None] -> int
    - typing.Optional[int] -> int
    - int | None -> int
    - typing.Union[int, str, None] -> typing.Union[int, str]
    - typing.Optional[int | str] -> typing.Union[int, str]
    - int | str | None -> int | str

    If the given type is not a Union with None, the function returns None instead.
    """
    origin_type = typing.get_origin(t)

    if origin_type is not typing.Union and origin_type is not types.UnionType:
        return None

    args = typing.get_args(t)
    args_without_none = tuple(arg for arg in args if arg is not types.NoneType)

    if len(args_without_none) == len(args) or len(args_without_none) == 0:
        return None

    if origin_type is typing.Union:
        return typing.Union[args_without_none]

    repacked_union = args_without_none[0]
    for arg in args_without_none[1:]:
        repacked_union = repacked_union | arg

    return repacked_union


def get_annotated_args(t: typing.Any) -> tuple[typing.Any, ...] | None:
    """Parses a typing.Annotated type and returns the inner type and its args.

    If the given type is not an Annotated type, None is returned instead.
    """
    origin_type = typing.get_origin(t)
    if origin_type is not typing.Annotated:
        return None

    return typing.get_args(t)
