_C64_CHARMAP = ["."] * 128

_C64_CHARMAP[0] = "@"
for _ in range(26):
    _C64_CHARMAP[1 + _] = chr(ord("a") + _)
_C64_CHARMAP[27] = "["
_C64_CHARMAP[29] = "]"
_C64_CHARMAP[32] = " "
for _ in range(15):
    _C64_CHARMAP[33 + _] = chr(ord("!") + _)
for _ in range(10):
    _C64_CHARMAP[48 + _] = chr(ord("0") + _)
_C64_CHARMAP[58] = ":"
_C64_CHARMAP[59] = ";"
_C64_CHARMAP[60] = "<"
_C64_CHARMAP[61] = "="
_C64_CHARMAP[62] = ">"
_C64_CHARMAP[63] = "?"
_C64_CHARMAP[64] = "@"
for _ in range(26):
    _C64_CHARMAP[65 + _] = chr(ord("A") + _)


def c64_video_codes_to_unicode(data: bytes) -> str:
    return "".join(_C64_CHARMAP[b & 0x7F] for b in data)


def int_from_c64_bytes(value: bytes) -> int:
    return int.from_bytes(value, byteorder="little")


def validated_update(model, data):
    return model.__class__.model_validate({**model.model_dump(), **data})
