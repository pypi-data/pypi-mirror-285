from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

from categories.type import typeclass

__all__ = (
    'Num',
    'NumInt',
)


a = TypeVar('a')


@dataclass(frozen=True)
class Num(typeclass[a]):
    def add(self, x : a, y : a, /) -> a: ...

    def sub(self, x : a, y : a, /) -> a:
        return self.add(x, self.neg(y))

    def mul(self, x : a, y : a, /) -> a: ...

    def neg(self, x : a, /) -> a:
        return self.sub(self.int(0), x)

    def abs(self, x : a, /) -> a: ...

    def sign(self, x : a, /) -> a: ...

    def int(self, x : int, /) -> a: ...


@dataclass(frozen=True)
class NumInt(Num[int]):
    def add(self, x : int, y : int, /) -> int:
        return x + y

    def sub(self, x : int, y : int, /) -> int:
        return x - y

    def mul(self, x : int, y : int, /) -> int:
        return x * y

    def neg(self, x : int, /) -> int:
        return -x

    def abs(self, x : int, /) -> int:
        return abs(x)

    def sign(self, x : int, /) -> int:
        match x:
            case x if x < 0:
                return -1
            case 0:
                return 0
            case x if x > 0:
                return 1

    def int(self, x : int, /) -> int:
        return x
