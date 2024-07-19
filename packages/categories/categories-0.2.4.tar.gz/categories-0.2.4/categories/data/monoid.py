from __future__ import annotations

from dataclasses import dataclass
from functools import reduce
from typing import TypeVar

from categories.data.semigroup import Semigroup, SemigroupStr
from categories.type import typeclass

__all__ = (
    'Monoid',
    'MonoidStr',
)


a = TypeVar('a')


@dataclass(frozen=True)
class Monoid(Semigroup[a], typeclass[a]):
    def empty(self, /) -> a:
        return self.concat([])

    def concat(self, xs : list[a], /) -> a:
        return reduce(self.append, xs, self.empty())


@dataclass(frozen=True)
class MonoidStr(SemigroupStr, Monoid[str]):
    def empty(self, /) -> str:
        return str()

    def concat(self, xs : list[str], /) -> str:
        return str().join(xs)
