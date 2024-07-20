from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

from categories.data.monoid import Monoid
from categories.data.num import Num
from categories.data.semigroup import Semigroup
from categories.type import forall

__all__ = (
    'Product',
    'SemigroupProduct',
    'MonoidProduct',
)


a = TypeVar('a')


@dataclass(frozen=True)
class Product(forall[a]):
    product : a


@dataclass(frozen=True)
class SemigroupProduct(Semigroup[Product[a]]):
    inst : Num[a]

    def append(self, x : Product[a], y : Product[a], /) -> Product[a]:
        match self, x, y:
            case SemigroupProduct(inst), Product(x), Product(y):
                return Product(inst.mul(x, y))


@dataclass(frozen=True)
class MonoidProduct(SemigroupProduct[a], Monoid[Product[a]]):
    inst : Num[a]

    def empty(self, /) -> Product[a]:
        match self:
            case MonoidProduct(inst):
                return Product(inst.int(1))
