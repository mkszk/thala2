import regex


OFFSET = regex.compile(r"^\s*(\+|-)?\s*(\d+)(\.\d+)?(h|min|s|ms)?\s*$")
GAIN = regex.compile(r"^\s*(\+|-)?\s*(\d+)(\.\d+)?\s*dB$")
ALL_ELEMENTS = (
    "audio",
    "movie",
    "image",
    "speak",
    "media",
    "crop",
    "margin",
    "scale",
    "seq",
    "par",
)


def _decode_num(sign, integer, fractional):
    val = float(integer)
    if fractional:
        val += float(fractional)
    if sign == "-":
        val *= -1
    return val


def _decode_time(sign, integer, fractional, unit):
    val = _decode_num(sign, integer, fractional)
    if unit == "h":
        val *= 60. * 60.
    elif unit == "min":
        val *= 60.
    elif unit == "s":
        pass
    elif unit == "ms":
        val *= 1e-3
    else:
        assert False
    return val


def parse_time(query):
    if mat := OFFSET.match(query):
        val = _decode_time(
            mat.group(1), mat.group(2), mat.group(3), mat.group(4))
        return val

    else:
        assert False


def parse_gain(query):
    if mat := GAIN.match(query):
        return _decode_num(
            mat.group(1), mat.group(2), mat.group(3))
    else:
        assert False


assert parse_time("10ms") == 10 * 1e-3
assert parse_time("+1s") == 1
assert parse_time("-10min") == -10 * 60
assert parse_time("1h") == 1 * 60 * 60
assert parse_gain("10dB") == 10
assert parse_gain("-10dB") == -10
