from __future__ import annotations

from dataclasses import dataclass

from categories.data.monoid import Monoid
from categories.data.semigroup import Semigroup

__all__ = (
    'All',
    'SemigroupAll',
    'MonoidAll',
)


@dataclass(frozen=True)
class All:
    all : bool


@dataclass(frozen=True)
class SemigroupAll(Semigroup[All]):
    def append(self, x : All, y : All, /) -> All:
        match x, y:
            case All(p), All(q):
                return All(p & q)


@dataclass(frozen=True)
class MonoidAll(SemigroupAll, Monoid[All]):
    def empty(self, /) -> All:
        return All(True)
