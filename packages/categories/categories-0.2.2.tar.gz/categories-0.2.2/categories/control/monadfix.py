from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

from categories.control.monad import Monad, MonadLambda
from categories.type import Lambda, _, hkt, typeclass

__all__ = (
    'MonadFix',
    'MonadFixLambda',
)


a = TypeVar('a')

m = TypeVar('m')

r = TypeVar('r')


@dataclass(frozen=True)
class MonadFix(Monad[m], typeclass[m]):
    def fix(self, f : Lambda[a, hkt[m, a]], /) -> hkt[m, a]: ...


@dataclass(frozen=True)
class MonadFixLambda(MonadLambda[r], MonadFix[Lambda[r, _]]):
    def fix(self, f : Lambda[a, Lambda[r, a]], /) -> Lambda[r, a]:
        return lambda r, /: (x := lambda: f(x)(r))()
