from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

from categories.control.applicative import Applicative
from categories.control.monad import Monad
from categories.data.functor import Functor
from categories.type import Lambda, _, forall

__all__ = (
    'Either',
    'Left',
    'Right',
    'FunctorEither',
    'ApplicativeEither',
    'MonadEither',
)


a = TypeVar('a')

b = TypeVar('b')

e = TypeVar('e')


@dataclass(frozen=True)
class Left(forall[a]):
    x : a


@dataclass(frozen=True)
class Right(forall[b]):
    y : b


Either = Left[a] | Right[b]


@dataclass(frozen=True)
class FunctorEither(Functor[Either[e, _]]):
    def map(self, f : Lambda[a, b], e : Either[e, a], /) -> Either[e, b]:
        match e:
            case Left(x):
                return Left(x)
            case Right(y):
                return Right(f(y))


@dataclass(frozen=True)
class ApplicativeEither(FunctorEither, Applicative[Either[e, _]]):
    def pure(self, x : a, /) -> Either[e, a]:
        return Right(x)

    def apply(self, e : Either[e, Lambda[a, b]], e_ : Either[e, a], /) -> Either[e, b]:
        match e:
            case Left(x):
                return Left(x)
            case Right(f):
                return self.map(f, e_)


@dataclass(frozen=True)
class MonadEither(ApplicativeEither, Monad[Either[e, _]]):
    def bind(self, e : Either[e, a], k : Lambda[a, Either[e, b]], /) -> Either[e, b]:
        match e:
            case Left(x):
                return Left(x)
            case Right(y):
                return k(y)
