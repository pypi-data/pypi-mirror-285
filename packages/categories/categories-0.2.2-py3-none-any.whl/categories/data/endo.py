from __future__ import annotations

from dataclasses import dataclass
from functools import reduce
from itertools import repeat
from typing import TypeVar

from categories.data.monoid import Monoid
from categories.data.semigroup import Semigroup
from categories.type import Lambda, forall

__all__ = (
    'Endo',
    'SemigroupEndo',
    'MonoidEndo',
)


a = TypeVar('a')


@dataclass(frozen=True)
class Endo(forall[a]):
    endo : Lambda[a, a]


@dataclass(frozen=True)
class SemigroupEndo(Semigroup[Endo[a]]):
    def append(self, x : Endo[a], y : Endo[a], /) -> Endo[a]:
        match x, y:
            case Endo(f), Endo(g):
                return Endo(lambda x, /: f(g(x)))

    def times(self, n : int, x : Endo[a], /) -> Endo[a]:
        match x:
            case Endo(f):
                return Endo(lambda x, /: reduce(lambda x, f, /: f(x), repeat(f, n), x))


@dataclass(frozen=True)
class MonoidEndo(SemigroupEndo[a], Monoid[Endo[a]]):
    def empty(self, /) -> Endo[a]:
        return Endo(lambda x, /: x)
