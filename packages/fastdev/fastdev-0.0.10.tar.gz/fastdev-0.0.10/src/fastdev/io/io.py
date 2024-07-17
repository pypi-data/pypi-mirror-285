from functools import lru_cache
from pathlib import Path
from typing import IO, Any, Dict, Literal, Optional, Type, Union, cast

import fsspec  # type: ignore
from typing_extensions import TypeAlias

from fastdev.io.handlers.base_handler import BaseFileHandler
from fastdev.io.handlers.json_handler import JSONHandler
from fastdev.io.handlers.yaml_handler import YAMLHandler

FILE_HANDLER_CLASSES: Dict[str, Type[BaseFileHandler]] = {
    "json": JSONHandler,
    "yaml": YAMLHandler,
    "yml": YAMLHandler,
}
FILE_EXTENSIONS: TypeAlias = Literal["json", "yaml", "yml"]
FILE_HANDLERS: Dict[str, BaseFileHandler] = {}


@lru_cache()
def get_file_handler(file_format: str) -> BaseFileHandler:
    if file_format not in FILE_HANDLERS:
        if file_format not in FILE_HANDLER_CLASSES:
            raise ValueError(f"Unsupported file format: {file_format}")
        else:
            FILE_HANDLERS[file_format] = FILE_HANDLER_CLASSES[file_format]()
    return FILE_HANDLERS[file_format]


def load(
    file: Union[str, Path, IO],
    file_format: Optional[FILE_EXTENSIONS] = None,
    **kwargs,
) -> Any:
    """Load json/yaml/pickle file from file.

    Args:
        file (Union[str, Path, IO]): file path or io object.
        file_format (Optional[FILE_EXTENSIONS], optional): file extension. Defaults to None.

    Returns:
        Any: The loaded python object.

    Examples:
        >>> load("assets/example.json")
        {'hello': 'world'}
    """
    # Parameters validation
    if isinstance(file, Path):
        file = str(file)
    if file_format is None:
        if isinstance(file, str):
            file_format = cast(FILE_EXTENSIONS, file.split(".")[-1])
        else:
            raise ValueError("file_format is required when file is not a string or path")

    # Get file handler
    file_handler = get_file_handler(file_format)

    # Load file
    if isinstance(file, str):
        mode = "rb" if file_handler.str_or_bytes == "bytes" else "r"
        with fsspec.open(file, mode) as f:
            obj = file_handler.load_from_fileobj(cast(IO, f), **kwargs)
    elif hasattr(file, "read"):
        obj = file_handler.load_from_fileobj(cast(IO, file), **kwargs)
    else:
        raise TypeError("File must be a filepath str or a file object")
    return obj


def dump(
    obj: Any,
    file: Union[str, Path, IO],
    file_format: Optional[FILE_EXTENSIONS] = None,
    **kwargs,
):
    """Dump obj to json/yaml file.

    Args:
        obj (Any): Python object to dump.
        file (Union[str, Path, IO]): File path or IO object.
        file_format (Optional[FILE_EXTENSIONS], optional): File format. Defaults to None.

    Examples:
        >>> import tempfile
        >>> with tempfile.TemporaryDirectory() as tmpdir:
        ...     dump({"hello": "world"}, f"{tmpdir}/example.json")
    """
    # Parameters validation
    if isinstance(file, Path):
        file = str(file)
    if file_format is None:
        if isinstance(file, str):
            file_format = cast(FILE_EXTENSIONS, file.split(".")[-1])
        else:
            raise ValueError("file_format is required when file is not a string or path")

    # Get file handler
    file_handler = get_file_handler(file_format)

    if isinstance(file, str):
        mode = "wb" if file_handler.str_or_bytes == "bytes" else "r"
        with fsspec.open(file, mode) as f:
            file_handler.dump_to_fileobj(obj, cast(IO, f), **kwargs)
    elif hasattr(file, "write"):
        file_handler.dump_to_fileobj(obj, cast(IO, file), **kwargs)
    else:
        raise TypeError("File must be a filepath str or a file object")


__all__ = ["FILE_EXTENSIONS", "load", "dump"]
