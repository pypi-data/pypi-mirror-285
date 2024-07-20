from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

from categories.data.maybe import Maybe, Nothing, Just
from categories.data.monoid import Monoid
from categories.data.ord import Ord
from categories.data.semigroup import Semigroup
from categories.type import forall

__all__ = (
    'Max',
    'SemigroupMax',
    'MonoidMax',
)


a = TypeVar('a')


@dataclass(frozen=True)
class Max(forall[a]):
    max : Maybe[a]


@dataclass(frozen=True)
class SemigroupMax(Semigroup[Max[a]]):
    inst : Ord[a]

    def append(self, x : Max[a], y : Max[a], /) -> Max[a]:
        match self, x, y:
            case SemigroupMax(inst), Max(m), Max(Nothing()):
                return Max(m)
            case SemigroupMax(inst), Max(Nothing()), Max(m):
                return Max(m)
            case SemigroupMax(inst), Max(Just(x)), Max(Just(y)):
                return Max(Just(x if inst.ge(x, y) else y))


@dataclass(frozen=True)
class MonoidMax(SemigroupMax[a], Monoid[Max[a]]):
    inst : Ord[a]

    def empty(self, /) -> Max[a]:
        return Max(Nothing())
