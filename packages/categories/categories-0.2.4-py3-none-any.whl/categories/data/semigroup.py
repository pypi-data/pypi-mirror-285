from __future__ import annotations

from dataclasses import dataclass
from functools import reduce
from itertools import repeat
from typing import TypeVar

from categories.type import typeclass

__all__ = (
    'Semigroup',
    'SemigroupStr',
)


a = TypeVar('a')


@dataclass(frozen=True)
class Semigroup(typeclass[a]):
    def append(self, x : a, y : a, /) -> a:
        return self.concat([x, y])

    def concat(self, xs : list[a], /) -> a:
        return reduce(self.append, xs)

    def times(self, n : int, x : a, /) -> a:
        return reduce(self.append, repeat(x, n))


@dataclass(frozen=True)
class SemigroupStr(Semigroup[str]):
    def append(self, x : str, y : str, /) -> str:
        return x + y

    def concat(self, xs : list[str], /) -> str:
        return str().join(xs)

    def times(self, n : int, x : str, /) -> str:
        return str().join(repeat(x, n))
