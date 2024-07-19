from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

from categories.control.monad import Monad
from categories.type import hkt, typeclass

__all__ = (
    'MonadTrans',
)


a = TypeVar('a')

m = TypeVar('m')

t = TypeVar('t')


@dataclass(frozen=True)
class MonadTrans(typeclass[t]):
    def lift(self, inst : Monad[m], m : hkt[m, a], /) -> hkt[t, m, a]: ...
