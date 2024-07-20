from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

from categories.control.alternative import Alternative
from categories.control.applicative import Applicative
from categories.control.liftio import LiftIO
from categories.control.monad import Monad
from categories.control.monadplus import MonadPlus
from categories.control.monadtrans import MonadTrans
from categories.data.functor import Functor
from categories.data.maybe import Maybe, Nothing, Just
from categories.type import IO, Lambda, _, forall, hkt

__all__ = (
    'MaybeT',
    'FunctorMaybeT',
    'ApplicativeMaybeT',
    'AlternativeMaybeT',
    'MonadMaybeT',
    'MonadPlusMaybeT',
    'MonadTransMaybeT',
    'LiftIOMaybeT',
)


a = TypeVar('a')

b = TypeVar('b')

m = TypeVar('m')


@dataclass(frozen=True)
class MaybeT(forall[m, a]):
    run : hkt[m, Maybe[a]]


@dataclass(frozen=True)
class FunctorMaybeT(Functor[MaybeT[m, _]]):
    inst : Functor[m]

    def map(self, f : Lambda[a, b], x : MaybeT[m, a], /) -> MaybeT[m, b]:
        match self:
            case FunctorMaybeT(inst):
                def g(m : Maybe[a], /) -> Maybe[b]:
                    match m:
                        case Nothing():
                            return Nothing()
                        case Just(x):
                            return Just(f(x))
                return MaybeT(inst.map(g, x.run))


@dataclass(frozen=True)
class ApplicativeMaybeT(FunctorMaybeT[m], Applicative[MaybeT[m, _]]):
    inst : Monad[m]

    def pure(self, x : a, /) -> MaybeT[m, a]:
        match self:
            case ApplicativeMaybeT(inst):
                return MaybeT(inst.pure(Just(x)))

    def apply(self, f : MaybeT[m, Lambda[a, b]], x : MaybeT[m, a], /) -> MaybeT[m, b]:
        match self:
            case ApplicativeMaybeT(inst):
                def k(m : Maybe[Lambda[a, b]], /) -> hkt[m, Maybe[b]]:
                    match m:
                        case Nothing():
                            return inst.pure(Nothing())
                        case Just(f):
                            def k_(m_ : Maybe[a], /) -> hkt[m, Maybe[b]]:
                                match m_:
                                    case Nothing():
                                        return inst.pure(Nothing())
                                    case Just(x):
                                        return inst.pure(Just(f(x)))
                            return inst.bind(x.run, k_)
                return MaybeT(inst.bind(f.run, k))


@dataclass(frozen=True)
class AlternativeMaybeT(ApplicativeMaybeT[m], Alternative[MaybeT[m, _]]):
    inst : Monad[m]

    def empty(self, /) -> MaybeT[m, a]:
        match self:
            case AlternativeMaybeT(inst):
                return MaybeT(inst.pure(Nothing()))

    def alt(self, x : MaybeT[m, a], y : MaybeT[m, a], /) -> MaybeT[m, a]:
        match self:
            case AlternativeMaybeT(inst):
                def k(m : Maybe[a], /) -> hkt[m, Maybe[a]]:
                    match m:
                        case Nothing():
                            return y.run
                        case Just(_):
                            return inst.pure(m)
                return MaybeT(inst.bind(x.run, k))


@dataclass(frozen=True)
class MonadMaybeT(ApplicativeMaybeT[m], Monad[MaybeT[m, _]]):
    inst : Monad[m]

    def bind(self, m : MaybeT[m, a], k : Lambda[a, MaybeT[m, b]], /) -> MaybeT[m, b]:
        match self:
            case MonadMaybeT(inst):
                def k_(m_ : Maybe[a], /) -> hkt[m, Maybe[b]]:
                    match m_:
                        case Nothing():
                            return inst.pure(Nothing())
                        case Just(x):
                            return k(x).run
                return MaybeT(inst.bind(m.run, k_))


@dataclass(frozen=True)
class MonadPlusMaybeT(AlternativeMaybeT[m], MonadMaybeT[m], MonadPlus[MaybeT[m, _]]):
    inst : Monad[m]


@dataclass(frozen=True)
class MonadTransMaybeT(MonadTrans[MaybeT]):
    def lift(self, inst : Monad[m], m : hkt[m, a], /) -> MaybeT[m, a]:
        return MaybeT(inst.map(Just, m))


@dataclass(frozen=True)
class LiftIOMaybeT(MonadMaybeT[m], LiftIO[MaybeT[m, _]]):
    inst : LiftIO[m]

    def liftIO(self, m : IO[a], /) -> MaybeT[m, a]:
        match self:
            case LiftIOMaybeT(inst):
                return MaybeT(inst.map(Just, inst.liftIO(m)))
