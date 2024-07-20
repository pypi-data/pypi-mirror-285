from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

from categories.data.monoid import Monoid
from categories.data.num import Num
from categories.data.semigroup import Semigroup
from categories.type import forall

__all__ = (
    'Sum',
    'SemigroupSum',
    'MonoidSum',
)


a = TypeVar('a')


@dataclass(frozen=True)
class Sum(forall[a]):
    sum : a


@dataclass(frozen=True)
class SemigroupSum(Semigroup[Sum[a]]):
    inst : Num[a]

    def append(self, x : Sum[a], y : Sum[a], /) -> Sum[a]:
        match self, x, y:
            case SemigroupSum(inst), Sum(x), Sum(y):
                return Sum(inst.add(x, y))


@dataclass(frozen=True)
class MonoidSum(SemigroupSum[a], Monoid[Sum[a]]):
    inst : Num[a]

    def empty(self, /) -> Sum[a]:
        match self:
            case MonoidSum(inst):
                return Sum(inst.int(0))
