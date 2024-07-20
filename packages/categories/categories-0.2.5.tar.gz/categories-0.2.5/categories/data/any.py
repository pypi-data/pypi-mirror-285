from __future__ import annotations

from dataclasses import dataclass

from categories.data.monoid import Monoid
from categories.data.semigroup import Semigroup

__all__ = (
    'Any',
    'SemigroupAny',
    'MonoidAny',
)


@dataclass(frozen=True)
class Any:
    any : bool


@dataclass(frozen=True)
class SemigroupAny(Semigroup[Any]):
    def append(self, x : Any, y : Any, /) -> Any:
        match x, y:
            case Any(p), Any(q):
                return Any(p | q)


@dataclass(frozen=True)
class MonoidAny(SemigroupAny, Monoid[Any]):
    def empty(self, /) -> Any:
        return Any(False)
