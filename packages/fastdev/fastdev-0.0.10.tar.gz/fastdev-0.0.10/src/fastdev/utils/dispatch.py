from __future__ import annotations

from typing import Any, Callable, TypeVar, cast, get_type_hints


class SingleDispatch:
    def __init__(self, func_name: str):
        self._func_name = func_name
        self._impls: dict[type, Callable] = {}
        self._dispatch_cache: dict[type, Callable] = {}

    def register_impl(self, func: Callable):
        first_arg_type = list(get_type_hints(func).values())[0]
        self._impls[first_arg_type] = func
        self._dispatch_cache[first_arg_type] = func

    def __call__(self, *args: Any, **kwarg: Any) -> Any:
        if len(args) > 0:
            first_arg_type = type(args[0])
        elif len(kwarg) > 0:
            first_arg_type = type(list(kwarg.values())[0])
        else:
            first_arg_type = type(None)

        try:
            impl = self._dispatch_cache[first_arg_type]
        except KeyError:
            found_impl = False
            for typ in self._impls:
                if issubclass(first_arg_type, typ):
                    impl = self._impls[typ]
                    self._dispatch_cache[first_arg_type] = self._impls[typ]
                    found_impl = True
                    break
            if not found_impl:
                raise TypeError(f"No implementation found for {self._func_name} with type {first_arg_type}")

        return impl(*args, **kwarg)


_DISPATCH_REGISTRY: dict[str, SingleDispatch] = {}

T = TypeVar("T", bound=Callable)


def singledispatch(is_impl: bool = True) -> Callable[[T], T]:
    def _inner(func: T) -> T:
        func_name = func.__name__
        if func_name not in _DISPATCH_REGISTRY:
            _DISPATCH_REGISTRY[func_name] = SingleDispatch(func_name)
        if is_impl:
            _DISPATCH_REGISTRY[func_name].register_impl(func)
        return cast(T, _DISPATCH_REGISTRY[func_name])

    return _inner


__all__ = ["singledispatch"]
