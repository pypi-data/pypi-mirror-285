from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

from categories.type import typeclass

__all__ = (
    'Eq',
)


a = TypeVar('a')


@dataclass(frozen=True)
class Eq(typeclass[a]):
    def eq(self, x : a, y : a, /) -> bool:
        return not self.ne(x, y)

    def ne(self, x : a, y : a, /) -> bool:
        return not self.eq(x, y)
