# Copyright (C) 2024 Nice Zombies
"""JSON decoder."""
from __future__ import annotations

__all__: list[str] = ["DuplicateKey", "JSONSyntaxError", "make_scanner"]

import re
from math import inf, isinf, nan
from re import DOTALL, MULTILINE, VERBOSE, Match, RegexFlag
from shutil import get_terminal_size
from typing import TYPE_CHECKING

from typing_extensions import Any  # type: ignore

if TYPE_CHECKING:
    from collections.abc import Callable

_FLAGS: RegexFlag = VERBOSE | MULTILINE | DOTALL
_UNESCAPE: dict[str, str] = {
    '"': '"',
    "\\": "\\",
    "/": "/",
    "b": "\b",
    "f": "\f",
    "n": "\n",
    "r": "\r",
    "t": "\t",
}

_match_chunk: Callable[[str, int], Match[str] | None] = re.compile(
    r'[^"\\\x00-\x1f]+', _FLAGS,
).match
_match_number: Callable[[str, int], Match[str] | None] = re.compile(
    r"(-?(?:0|[1-9]\d*))(\.\d+)?([eE][-+]?\d+)?", _FLAGS,
).match
_match_whitespace: Callable[[str, int], Match[str] | None] = re.compile(
    r"[ \t\n\r]+", _FLAGS,
).match


def _get_err_context(doc: str, pos: int) -> tuple[int, str]:
    line_start: int = doc.rfind("\n", 0, pos) + 1
    if (line_end := doc.find("\n", pos)) == -1:
        line_end = len(doc)

    max_chars: int = get_terminal_size().columns - 4  # leading spaces
    min_start: int = min(line_end - max_chars, pos - max_chars // 2)
    max_end: int = max(line_start + max_chars, pos + max_chars // 2)
    text_start: int = max(min_start, line_start)
    text_end: int = min(line_end, max_end)
    text: str = doc[text_start:text_end].expandtabs(1)
    if text_start > line_start:
        text = "..." + text[3:]

    if text_end < line_end:
        text = text[:-3] + "..."

    return pos - text_start + 1, text


def _unescape_unicode(filename: str, s: str, pos: int) -> int:
    esc: str = s[pos:pos + 4]
    if len(esc) == 4 and esc[1] not in "xX":
        try:
            return int(esc, 16)
        except ValueError:
            pass

    msg: str = "Expecting 4 hex digits"
    raise JSONSyntaxError(msg, filename, s, pos)


# pylint: disable-next=R0912
def _scan_string(filename: str, s: str, end: int) -> (  # noqa: C901, PLR0912
    tuple[str, int]
):
    chunks: list[str] = []
    append_chunk: Callable[[str], None] = chunks.append
    str_idx: int = end - 1
    while True:
        # Match one or more unescaped string characters
        if match := _match_chunk(s, end):
            end = match.end()
            append_chunk(match.group())

        # Terminator is the end of string, a literal control character,
        # or a backslash denoting that an escape sequence follows
        try:
            terminator: str = s[end]
        except IndexError:
            msg: str = "Unterminated string"
            raise JSONSyntaxError(msg, filename, s, str_idx) from None

        if terminator == '"':
            return "".join(chunks), end + 1

        if terminator != "\\":
            if terminator == "\n":
                msg = "Unterminated string"
                raise JSONSyntaxError(msg, filename, s, str_idx)

            msg = "Unescaped control character"
            raise JSONSyntaxError(msg, filename, s, end)

        end += 1
        try:
            esc = s[end]
        except IndexError:
            msg = "Expecting escaped character"
            raise JSONSyntaxError(msg, filename, s, end) from None

        # If not a unicode escape sequence, must be in the lookup table
        if esc != "u":
            try:
                char = _UNESCAPE[esc]
            except KeyError:
                if esc == "\n":
                    msg = "Expecting escaped character"
                    raise JSONSyntaxError(msg, filename, s, end) from None

                msg = "Invalid backslash escape"
                raise JSONSyntaxError(msg, filename, s, end) from None

            end += 1
        else:
            uni: int = _unescape_unicode(filename, s, end + 1)
            end += 5
            if 0xd800 <= uni <= 0xdbff and s[end:end + 2] == r"\u":
                uni2: int = _unescape_unicode(filename, s, end + 2)
                if 0xdc00 <= uni2 <= 0xdfff:
                    uni = ((uni - 0xd800) << 10) | (uni2 - 0xdc00)
                    uni += 0x10000
                    end += 6

            char = chr(uni)

        append_chunk(char)


try:
    from jsonyx._accelerator import DuplicateKey  # type: ignore
except ImportError:
    class DuplicateKey(str):
        """Duplicate key."""

        __slots__: tuple[()] = ()

        def __hash__(self) -> int:
            """Return hash."""
            return id(self)


class JSONSyntaxError(SyntaxError):
    """JSON syntax error."""

    def __init__(self, msg: str, filename: str, doc: str, pos: int) -> None:
        """Create new JSON syntax error."""
        lineno: int = doc.count("\n", 0, pos) + 1
        self.colno: int = pos - doc.rfind("\n", 0, pos)
        offset, text = _get_err_context(doc, pos)
        super().__init__(msg, (filename, lineno, offset, text))

    def __str__(self) -> str:
        """Convert to string."""
        return (
            f"{self.msg} (file {self.filename}, line {self.lineno:d}, column "
            f"{self.colno:d})"
        )


try:
    from jsonyx._accelerator import make_scanner
except ImportError:
    # pylint: disable-next=R0915
    def make_scanner(  # noqa: C901, PLR0915
        allow_comments: bool,  # noqa: FBT001
        allow_duplicate_keys: bool,  # noqa: FBT001
        allow_nan: bool,  # noqa: FBT001
        allow_trailing_comma: bool,  # noqa: FBT001
    ) -> Callable[[str, str], Any]:
        """Make JSON scanner."""
        memo: dict[str, str] = {}
        memoize: Callable[[str, str], str] = memo.setdefault

        def skip_comments(filename: str, s: str, end: int) -> int:
            find: Callable[[str, int], int] = s.find
            while True:
                if match := _match_whitespace(s, end):
                    end = match.end()

                if (comment_prefix := s[end:end + 2]) == "//":
                    if not allow_comments:
                        msg: str = "Comments are not allowed"
                        raise JSONSyntaxError(msg, filename, s, end)

                    if (end := find("\n", end + 2)) == -1:
                        return len(s)

                    end += 1
                elif comment_prefix == "/*":
                    if not allow_comments:
                        msg = "Comments are not allowed"
                        raise JSONSyntaxError(msg, filename, s, end)

                    comment_idx: int = end
                    if (end := find("*/", end + 2)) == -1:
                        msg = "Unterminated comment"
                        raise JSONSyntaxError(msg, filename, s, comment_idx)

                    end += 2
                else:
                    return end

        # pylint: disable-next=R0913, R0912
        def scan_object(  # noqa: C901, PLR0912
            filename: str, s: str, end: int,
        ) -> tuple[dict[str, Any], int]:
            end = skip_comments(filename, s, end)
            if (nextchar := s[end:end + 1]) != '"':
                if nextchar != "}":
                    msg: str = "Expecting string"
                    raise JSONSyntaxError(msg, filename, s, end)

                return {}, end + 1

            result: dict[str, Any] = {}
            while True:
                key_idx: int = end
                key, end = _scan_string(filename, s, end + 1)
                if key not in result:
                    # Reduce memory consumption
                    key = memoize(key, key)
                elif not allow_duplicate_keys:
                    msg = "Duplicate keys are not allowed"
                    raise JSONSyntaxError(msg, filename, s, key_idx)
                else:
                    key = DuplicateKey(key)

                if s[end:end + 1] != ":":
                    colon_idx: int = end
                    end = skip_comments(filename, s, end)
                    if s[end:end + 1] != ":":
                        msg = "Expecting ':' delimiter"
                        raise JSONSyntaxError(msg, filename, s, colon_idx)

                end = skip_comments(filename, s, end + 1)
                result[key], end = scan_value(filename, s, end)
                if s[end:end + 1] != ",":
                    comma_idx: int = end
                    end = skip_comments(filename, s, end)
                    if (nextchar := s[end:end + 1]) != ",":
                        if nextchar != "}":
                            msg = "Expecting ',' delimiter"
                            raise JSONSyntaxError(msg, filename, s, comma_idx)

                        return result, end + 1

                comma_idx = end
                end = skip_comments(filename, s, end + 1)
                if (nextchar := s[end:end + 1]) != '"':
                    if nextchar != "}":
                        msg = "Expecting string"
                        raise JSONSyntaxError(msg, filename, s, end)

                    if not allow_trailing_comma:
                        msg = "Trailing comma is not allowed"
                        raise JSONSyntaxError(msg, filename, s, comma_idx)

                    return result, end + 1

        def scan_array(filename: str, s: str, end: int) -> (
            tuple[list[Any], int]
        ):
            end = skip_comments(filename, s, end)
            if (nextchar := s[end:end + 1]) == "]":
                return [], end + 1

            values: list[Any] = []
            append_value: Callable[[Any], None] = values.append
            while True:
                value, end = scan_value(filename, s, end)
                append_value(value)
                if s[end:end + 1] != ",":
                    comma_idx: int = end
                    end = skip_comments(filename, s, end)
                    if (nextchar := s[end:end + 1]) != ",":
                        if nextchar == "]":
                            return values, end + 1

                        msg: str = "Expecting ',' delimiter"
                        raise JSONSyntaxError(msg, filename, s, comma_idx)

                comma_idx = end
                end = skip_comments(filename, s, end + 1)
                if s[end:end + 1] == "]":
                    if allow_trailing_comma:
                        return values, end + 1

                    msg = "Trailing comma is not allowed"
                    raise JSONSyntaxError(msg, filename, s, comma_idx)

        # pylint: disable-next=R0912
        def scan_value(  # noqa: C901, PLR0912
            filename: str, s: str, idx: int,
        ) -> tuple[Any, int]:
            try:
                nextchar = s[idx]
            except IndexError:
                msg: str = "Expecting value"
                raise JSONSyntaxError(msg, filename, s, idx) from None

            result: Any
            if nextchar == '"':
                result, end = _scan_string(filename, s, idx + 1)
            elif nextchar == "{":
                result, end = scan_object(filename, s, idx + 1)
            elif nextchar == "[":
                result, end = scan_array(filename, s, idx + 1)
            elif nextchar == "n" and s[idx:idx + 4] == "null":
                result, end = None, idx + 4
            elif nextchar == "t" and s[idx:idx + 4] == "true":
                result, end = True, idx + 4
            elif nextchar == "f" and s[idx:idx + 5] == "false":
                result, end = False, idx + 5
            elif number := _match_number(s, idx):
                integer, frac, exp = number.groups()
                end = number.end()
                if frac or exp:
                    result = float(integer + (frac or "") + (exp or ""))
                    if isinf(result):
                        msg = "Number is too large"
                        raise JSONSyntaxError(msg, filename, s, idx)
                else:
                    result = int(integer)
            elif nextchar == "N" and s[idx:idx + 3] == "NaN":
                if not allow_nan:
                    msg: str = "NaN is not allowed"
                    raise JSONSyntaxError(msg, filename, s, idx)

                result, end = nan, idx + 3
            elif nextchar == "I" and s[idx:idx + 8] == "Infinity":
                if not allow_nan:
                    msg = "Infinity is not allowed"
                    raise JSONSyntaxError(msg, filename, s, idx)

                result, end = inf, idx + 8
            elif nextchar == "-" and s[idx:idx + 9] == "-Infinity":
                if not allow_nan:
                    msg = "-Infinity is not allowed"
                    raise JSONSyntaxError(msg, filename, s, idx)

                result, end = -inf, idx + 9
            else:
                msg = "Expecting value"
                raise JSONSyntaxError(msg, filename, s, idx)

            return result, end

        def scanner(filename: str, s: str) -> Any:
            end: int = skip_comments(filename, s, 0)
            try:
                obj, end = scan_value(filename, s, end)
            except JSONSyntaxError as exc:
                raise exc.with_traceback(None) from None
            finally:
                memo.clear()

            if (end := skip_comments(filename, s, end)) < len(s):
                msg: str = "Unexpected value"
                raise JSONSyntaxError(msg, filename, s, end)

            return obj

        return scanner
