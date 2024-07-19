from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

from categories.control.alternative import Alternative
from categories.control.applicative import Applicative
from categories.control.monad import Monad
from categories.control.monadfail import MonadFail
from categories.control.monadplus import MonadPlus
from categories.data.functor import Functor
from categories.type import Lambda, forall

__all__ = (
    'Maybe',
    'Nothing',
    'Just',
    'FunctorMaybe',
    'ApplicativeMaybe',
    'AlternativeMaybe',
    'MonadMaybe',
    'MonadFailMaybe',
    'MonadPlusMaybe',
)


a = TypeVar('a')

b = TypeVar('b')


@dataclass(frozen=True)
class Nothing: ...


@dataclass(frozen=True)
class Just(forall[a]):
    x : a


Maybe = Nothing | Just[a]


@dataclass(frozen=True)
class FunctorMaybe(Functor[Maybe]):
    def map(self, f : Lambda[a, b], m : Maybe[a], /) -> Maybe[b]:
        match m:
            case Nothing():
                return Nothing()
            case Just(x):
                return Just(f(x))


@dataclass(frozen=True)
class ApplicativeMaybe(FunctorMaybe, Applicative[Maybe]):
    def pure(self, x : a, /) -> Maybe[a]:
        return Just(x)

    def apply(self, m : Maybe[Lambda[a, b]], m_ : Maybe[a], /) -> Maybe[b]:
        match m:
            case Nothing():
                return Nothing()
            case Just(f):
                return self.map(f, m_)


@dataclass(frozen=True)
class AlternativeMaybe(ApplicativeMaybe, Alternative[Maybe]):
    def empty(self, /) -> Maybe[a]:
        return Nothing()

    def alt(self, m : Maybe[a], m_ : Maybe[a], /) -> Maybe[a]:
        match m:
            case Nothing():
                return m_
            case Just(_):
                return m


@dataclass(frozen=True)
class MonadMaybe(ApplicativeMaybe, Monad[Maybe]):
    def bind(self, m : Maybe[a], k : Lambda[a, Maybe[b]], /) -> Maybe[b]:
        match m:
            case Nothing():
                return Nothing()
            case Just(x):
                return k(x)


@dataclass(frozen=True)
class MonadFailMaybe(MonadMaybe, MonadFail[Maybe]):
    def fail(self, _ : str, /) -> Maybe[a]:
        return Nothing()


@dataclass(frozen=True)
class MonadPlusMaybe(AlternativeMaybe, MonadMaybe, MonadPlus[Maybe]): ...
