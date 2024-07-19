from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

from categories.data.eq import Eq
from categories.type import typeclass

__all__ = (
    'Ord',
    'Ordering',
    'LT',
    'EQ',
    'GT',
)


a = TypeVar('a')


@dataclass(frozen=True)
class LT: ...


@dataclass(frozen=True)
class EQ: ...


@dataclass(frozen=True)
class GT: ...


Ordering = LT | EQ | GT


@dataclass(frozen=True)
class Ord(Eq[a], typeclass[a]):
    def cmp(self, x : a, y : a, /) -> Ordering:
        return EQ() if self.eq(x, y) \
          else LT() if self.le(x, y) \
          else GT()

    def le(self, x : a, y : a, /) -> bool:
        match self.cmp(x, y):
            case GT():
                return False
            case _:
                return True

    def ge(self, x : a, y : a, /) -> bool:
        return self.le(y, x)

    def gt(self, x : a, y : a, /) -> bool:
        return not self.le(x, y)

    def lt(self, x : a, y : a, /) -> bool:
        return not self.le(y, x)

    def max(self, x : a, y : a, /) -> a:
        return y if self.le(x, y) else x

    def min(self, x : a, y : a, /) -> a:
        return x if self.le(x, y) else y
