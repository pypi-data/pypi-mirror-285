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
from categories.type import IO, Lambda, _, forall, hkt

__all__ = (
    'ReaderT',
    'FunctorReaderT',
    'ApplicativeReaderT',
    'AlternativeReaderT',
    'MonadReaderT',
    'MonadPlusReaderT',
    'MonadTransReaderT',
    'LiftIOReaderT',
)


a = TypeVar('a')

b = TypeVar('b')

m = TypeVar('m')

r = TypeVar('r')


@dataclass(frozen=True)
class ReaderT(forall[r, m, a]):
    run : Lambda[r, hkt[m, a]]


@dataclass(frozen=True)
class FunctorReaderT(Functor[ReaderT[r, m, _]]):
    inst : Functor[m]

    def map(self, f : Lambda[a, b], x : ReaderT[r, m, a], /) -> ReaderT[r, m, b]:
        match self:
            case FunctorReaderT(inst):
                return ReaderT(lambda r, /: inst.map(f, x.run(r)))

    def const(self, x : a, _ : ReaderT[r, m, b], /) -> ReaderT[r, m, a]:
        match self:
            case FunctorReaderT(inst):
                return ReaderT(lambda r, /: inst.const(x, _.run(r)))


@dataclass(frozen=True)
class ApplicativeReaderT(FunctorReaderT[r, m], Applicative[ReaderT[r, m, _]]):
    inst : Applicative[m]

    def pure(self, x : a, /) -> ReaderT[r, m, a]:
        match self:
            case ApplicativeReaderT(inst):
                return ReaderT(lambda _, /: inst.pure(x))

    def apply(self, f : ReaderT[r, m, Lambda[a, b]], x : ReaderT[r, m, a], /) -> ReaderT[r, m, b]:
        match self:
            case ApplicativeReaderT(inst):
                return ReaderT(lambda r, /: inst.apply(f.run(r), x.run(r)))

    def seq(self, _ : ReaderT[r, m, a], x : ReaderT[r, m, b], /) -> ReaderT[r, m, b]:
        match self:
            case ApplicativeReaderT(inst):
                return ReaderT(lambda r, /: inst.seq(_.run(r), x.run(r)))


@dataclass(frozen=True)
class AlternativeReaderT(ApplicativeReaderT[r, m], Alternative[ReaderT[r, m, _]]):
    inst : Alternative[m]

    def empty(self, /) -> ReaderT[r, m, a]:
        match self:
            case AlternativeReaderT(inst):
                return ReaderT(lambda _, /: inst.empty())

    def alt(self, x : ReaderT[r, m, a], y : ReaderT[r, m, a], /) -> ReaderT[r, m, a]:
        match self:
            case AlternativeReaderT(inst):
                return ReaderT(lambda r, /: inst.alt(x.run(r), y.run(r)))


@dataclass(frozen=True)
class MonadReaderT(ApplicativeReaderT[r, m], Monad[ReaderT[r, m, _]]):
    inst : Monad[m]

    def bind(self, m : ReaderT[r, m, a], k : Lambda[a, ReaderT[r, m, b]], /) -> ReaderT[r, m, b]:
        match self:
            case MonadReaderT(inst):
                return ReaderT(lambda r, /: inst.bind(m.run(r), lambda x, /: k(x).run(r)))


@dataclass(frozen=True)
class MonadPlusReaderT(AlternativeReaderT[r, m], MonadReaderT[r, m], MonadPlus[ReaderT[r, m, _]]):
    inst : MonadPlus[m]


@dataclass(frozen=True)
class MonadTransReaderT(MonadTrans[ReaderT[r, _, _]]):
    def lift(self, inst : Monad[m], m : hkt[m, a], /) -> ReaderT[r, m, a]:
        return ReaderT(lambda _, /: m)


@dataclass(frozen=True)
class LiftIOReaderT(MonadReaderT[r, m], LiftIO[ReaderT[r, m, _]]):
    inst : LiftIO[m]

    def liftIO(self, m : IO[a], /) -> ReaderT[r, m, a]:
        match self:
            case LiftIOReaderT(inst):
                return ReaderT(lambda _, /: inst.liftIO(m))
