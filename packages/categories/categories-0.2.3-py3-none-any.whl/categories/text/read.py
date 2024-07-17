from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

from categories.type import typeclass

__all__ = (
    'Read',
)


a = TypeVar('a')


@dataclass(frozen=True)
class Read(typeclass[a]):
    def read(self, s : str, /) -> list[tuple[a, str]]: ...
