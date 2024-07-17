from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

from categories.type import typeclass

__all__ = (
    'Show',
)


a = TypeVar('a')


@dataclass(frozen=True)
class Show(typeclass[a]):
    def show(self, x : a, /) -> str: ...
