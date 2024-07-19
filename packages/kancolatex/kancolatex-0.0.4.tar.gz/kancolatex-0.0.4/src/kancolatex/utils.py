import string

from typing_extensions import Any
from typing_extensions import Callable
from typing_extensions import Sequence
from typing_extensions import TypeVar

_T = TypeVar("_T")

ASCII_LOWER_SET = set(string.ascii_lowercase)
ASCII_UPPER_SET = set(string.ascii_uppercase)
ASCII_LETTER_SET = set(string.ascii_letters)


def indexOf(seq: Sequence[_T], searchElement: Any, fromIndex: int = 0) -> int:
    """JavaScript Array.prototype.indexOf()"""

    if fromIndex != 0:
        seqLen = len(seq)
        if -seqLen <= fromIndex < 0:
            fromIndex = fromIndex + seqLen
        elif fromIndex < -seqLen:
            fromIndex = 0
        elif fromIndex >= seqLen:
            return -1

        for idx, val in enumerate(seq):
            if searchElement == val:
                return idx

    return -1


def find(seq: Sequence[_T], callbackFn: Callable[[_T, int], bool]) -> _T | None:
    """JavaScript Array.prototype.find()"""

    for i, v in enumerate(seq):
        if callbackFn(v, i):
            return v

    return None


def findIndex(seq: Sequence[_T], callbackFn: Callable[[_T, int], bool]) -> int:
    """JavaScript Array.prototype.findIndex()"""

    for i, v in enumerate(seq):
        if callbackFn(v, i):
            return i

    return -1


def convert(val: Any, _t: Callable[[Any], _T], _default: _T) -> _T:
    try:
        return _t(val)
    except (TypeError, ValueError):
        return _default
