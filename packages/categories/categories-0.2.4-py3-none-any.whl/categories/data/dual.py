from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

from categories.data.monoid import Monoid
from categories.data.semigroup import Semigroup
from categories.type import forall

__all__ = (
    'Dual',
    'SemigroupDual',
    'MonoidDual',
)


a = TypeVar('a')


@dataclass(frozen=True)
class Dual(forall[a]):
    dual : a


@dataclass(frozen=True)
class SemigroupDual(Semigroup[Dual[a]]):
    inst : Semigroup[a]

    def append(self, x : Dual[a], y : Dual[a], /) -> Dual[a]:
        match self, x, y:
            case SemigroupDual(inst), Dual(x_), Dual(y_):
                return Dual(inst.append(y_, x_))

    def times(self, n : int, x : Dual[a], /) -> Dual[a]:
        match self, x:
            case SemigroupDual(inst), Dual(x_):
                return Dual(inst.times(n, x_))


@dataclass(frozen=True)
class MonoidDual(SemigroupDual[a], Monoid[Dual[a]]):
    inst : Monoid[a]

    def empty(self, /) -> Dual[a]:
        match self:
            case MonoidDual(inst):
                return Dual(inst.empty())
