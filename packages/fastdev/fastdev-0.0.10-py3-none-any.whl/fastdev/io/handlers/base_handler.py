from abc import ABCMeta, abstractmethod
from typing import Any, IO, Literal


class BaseFileHandler(metaclass=ABCMeta):
    str_or_bytes: Literal["str", "bytes"] = "bytes"

    @abstractmethod
    def load_from_fileobj(self, file: IO, **kwargs) -> Any: ...

    @abstractmethod
    def dump_to_fileobj(self, obj: Any, file: IO, **kwargs): ...

    @abstractmethod
    def load_from_str(self, s: str, **kwargs) -> Any: ...

    @abstractmethod
    def dump_to_str(self, obj: Any, **kwargs) -> str: ...
