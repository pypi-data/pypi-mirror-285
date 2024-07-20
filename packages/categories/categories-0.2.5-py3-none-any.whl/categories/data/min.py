from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

from categories.data.maybe import Maybe, Nothing, Just
from categories.data.monoid import Monoid
from categories.data.ord import Ord
from categories.data.semigroup import Semigroup
from categories.type import forall

__all__ = (
    'Min',
    'SemigroupMin',
    'MonoidMin',
)


a = TypeVar('a')


@dataclass(frozen=True)
class Min(forall[a]):
    min : Maybe[a]


@dataclass(frozen=True)
class SemigroupMin(Semigroup[Min[a]]):
    inst : Ord[a]

    def append(self, x : Min[a], y : Min[a], /) -> Min[a]:
        match self, x, y:
            case SemigroupMin(inst), Min(m), Min(Nothing()):
                return Min(m)
            case SemigroupMin(inst), Min(Nothing()), Min(m):
                return Min(m)
            case SemigroupMin(inst), Min(Just(x)), Min(Just(y)):
                return Min(Just(x if inst.le(x, y) else y))


@dataclass(frozen=True)
class MonoidMin(SemigroupMin[a], Monoid[Min[a]]):
    inst : Ord[a]

    def empty(self, /) -> Min[a]:
        return Min(Nothing())
