"""Decode a stream of consecutive top-level JSON values.

The jq command accepts a sequence of JSON texts, such as several complete
objects separated by whitespace, although json.loads() accepts only one.
Return source character offsets with each decoded value. No files, subprocess
or Tk objects are used here.
"""
import json

_WHITESPACE = " \t\r\n"


def json_values(text):
    """Return [(start, end, value), ...] for a nonempty JSON text stream.

    Raise json.JSONDecodeError with an offset in the *original* source on
    malformed JSON, including data between records. Adjacent JSON objects
    without commas are separate top-level values (as they are for jq).
    """
    decoder = json.JSONDecoder()
    values = []
    position = 0
    length = len(text)
    while True:
        while position < length and text[position] in _WHITESPACE:
            position += 1
        if position == length:
            break
        value, end = decoder.raw_decode(text, position)
        values.append((position, end, value))
        position = end
    if not values:
        raise json.JSONDecodeError("Expecting value", text, 0)
    return values
