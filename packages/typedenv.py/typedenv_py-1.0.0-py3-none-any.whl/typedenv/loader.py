import os
import typing
from collections.abc import Sequence

from typedenv._internals import _MISSING
from typedenv.annotations import get_annotated_args, get_unioned_with_none
from typedenv.converters import Converter, ConverterDict, cast_to_bool

_T = typing.TypeVar("_T", bound="EnvLoader")
_SINGLETONS: dict[type, typing.Any] = {}


class EnvLoader:
    __frozen: typing.ClassVar[bool]
    __singleton: typing.ClassVar[bool]
    __converters: typing.ClassVar[ConverterDict]
    _env_keys: set[str]

    def __init_subclass__(
        cls,
        frozen: bool = True,
        singleton: bool = False,
        converters: Sequence[Converter] | None = None,
        **kwargs,
    ) -> None:
        cls.__frozen = frozen
        cls.__singleton = singleton
        cls.__converters = ConverterDict()

        cls.__converters[str] = str
        cls.__converters[int] = int
        cls.__converters[float] = float
        cls.__converters[bool] = cast_to_bool

        if converters is not None:
            for converter in converters:
                cls.__converters[converter.type_] = converter.convert

        return super().__init_subclass__(**kwargs)

    def __new__(cls: type[_T], *args, **kwargs) -> _T:
        global _SINGLETONS
        if cls.__singleton and cls in _SINGLETONS:
            return _SINGLETONS[cls]

        instance = super().__new__(cls, *args, **kwargs)
        instance._env_keys = set()
        instance.__load_env__()

        if cls.__singleton:
            _SINGLETONS[cls] = instance

        return instance

    def __load_env__(self) -> None:
        for env_name, cast_type in typing.get_type_hints(
            type(self), include_extras=True
        ).items():
            if not env_name.isupper():
                continue

            default: typing.Literal[_MISSING] | str | typing.Any | None = _MISSING
            bespoke_cvtr: Converter | None = None

            annotated_args = get_annotated_args(cast_type)
            if annotated_args is not None:
                cast_type, *metadata_args = annotated_args
                for metadata in metadata_args:
                    if isinstance(metadata, Converter):
                        bespoke_cvtr = metadata
                        break

            unioned_type = get_unioned_with_none(cast_type)
            if is_nullable := unioned_type is not None:
                default = None
                cast_type = unioned_type

            if bespoke_cvtr and cast_type != bespoke_cvtr.type_:
                raise TypeError(
                    f"expected Converter for {env_name} to return {cast_type}; got {bespoke_cvtr.type_} instead"
                )

            if bespoke_cvtr is None and cast_type not in self.__converters:
                raise TypeError(f"Unsupported type: {cast_type}")

            convert = (
                bespoke_cvtr.convert if bespoke_cvtr else self.__converters[cast_type]
            )
            default = getattr(self, env_name, default)
            value = os.getenv(env_name, default)

            if value is _MISSING:
                raise ValueError(f"Missing environment variable: {env_name}")
            elif isinstance(value, str) and value != default:
                value = convert(value)
            elif value is None and not is_nullable:
                raise ValueError(f"Cannot set {env_name} to None")

            setattr(self, env_name, value)
            self._env_keys.add(env_name)

    def __setattr__(self, name: str, value: typing.Any) -> None:
        if name == f"_env_keys" and getattr(self, "_env_keys", None) is None:
            return object.__setattr__(self, name, value)

        if self.__frozen and name in self._env_keys:
            raise AttributeError(f"{name} is frozen and cannot be modified")

        return super().__setattr__(name, value)
