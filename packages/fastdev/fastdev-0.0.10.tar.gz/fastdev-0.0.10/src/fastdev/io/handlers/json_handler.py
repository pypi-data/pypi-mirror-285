import msgspec

from fastdev.io.handlers.base_handler import BaseFileHandler


class JSONHandler(BaseFileHandler):
    str_or_bytes = "bytes"

    def __init__(self):
        self.encoder = msgspec.json.Encoder()
        self.decoder = msgspec.json.Decoder()

    def load_from_fileobj(self, file, **kwargs):
        return self.decoder.decode(file.read())

    def dump_to_fileobj(self, obj, file, **kwargs):
        file.write(self.encoder.encode(obj))

    def dump_to_str(self, obj, **kwargs):
        # https://github.com/jcrist/msgspec/issues/514
        return self.encoder.encode(obj).decode("utf-8")

    def load_from_str(self, s: str, **kwargs):
        return self.decoder.decode(s)


__all__ = ["JSONHandler"]
