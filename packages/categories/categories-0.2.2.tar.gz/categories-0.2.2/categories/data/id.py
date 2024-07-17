from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

from categories.control.applicative import Applicative
from categories.control.monad import Monad
from categories.data.functor import Functor
from categories.type import Lambda, forall

__all__ = (
    'Id',
    'FunctorId',
    'ApplicativeId',
    'MonadId',
)


a = TypeVar('a')

b = TypeVar('b')


@dataclass(frozen=True)
class Id(forall[a]):
    id : a


@dataclass(frozen=True)
class FunctorId(Functor[Id]):
    def map(self, f : Lambda[a, b], x : Id[a], /) -> Id[b]:
        match x:
            case Id(x):
                return Id(f(x))


@dataclass(frozen=True)
class ApplicativeId(FunctorId, Applicative[Id]):
    def pure(self, x : a, /) -> Id[a]:
        return Id(x)

    def apply(self, f : Id[Lambda[a, b]], x : Id[a], /) -> Id[b]:
        match f, x:
            case Id(f), Id(x):
                return Id(f(x))


@dataclass(frozen=True)
class MonadId(ApplicativeId, Monad[Id]):
    def bind(self, m : Id[a], k : Lambda[a, Id[b]], /) -> Id[b]:
        match m:
            case Id(x):
                return k(x)
