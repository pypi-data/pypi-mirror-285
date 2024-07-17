import datetime
from typing import Any

import yaml
from msgspec import convert, to_builtins

from fastdev.io.handlers.base_handler import BaseFileHandler

# from msgspec.yaml import decode as msgspec_yaml_decode
# from msgspec.yaml import encode as msgspec_yaml_encode


# ref: https://github.com/jcrist/msgspec/blob/13a06dd88bcf553bb0497da3b3f0a2a628627ed6/msgspec/yaml.py#L31
def msgspec_yaml_encode(obj: Any) -> bytes:
    Dumper = getattr(yaml, "CDumper", yaml.Dumper)
    return yaml.dump_all(
        [to_builtins(obj, builtin_types=(datetime.datetime, datetime.date))],
        encoding="utf-8",
        Dumper=Dumper,
        allow_unicode=True,
        sort_keys=False,
    )


# ref: https://github.com/jcrist/msgspec/blob/13a06dd88bcf553bb0497da3b3f0a2a628627ed6/msgspec/yaml.py#L129
def msgspec_yaml_decode(buf, *, type=Any):
    Loader = getattr(yaml, "CFullLoader", yaml.FullLoader)
    if not isinstance(buf, (str, bytes)):
        # call `memoryview` first, since `bytes(1)` is actually valid
        buf = bytes(memoryview(buf))

    obj = yaml.load(buf, Loader)

    if type is Any:
        return obj
    return convert(
        obj,
        type,
        builtin_types=(datetime.datetime, datetime.date),
    )


class YAMLHandler(BaseFileHandler):
    str_or_bytes = "bytes"

    def load_from_fileobj(self, file, **kwargs):
        return msgspec_yaml_decode(file.read())

    def dump_to_fileobj(self, obj, file, **kwargs):
        file.write(msgspec_yaml_encode(obj))

    def dump_to_str(self, obj, **kwargs):
        # https://github.com/jcrist/msgspec/issues/514
        return msgspec_yaml_encode(obj).decode("utf-8")

    def load_from_str(self, s: str, **kwargs):
        return msgspec_yaml_decode(s)


__all__ = ["YAMLHandler"]
