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
from categories.data.monoid import Monoid
from categories.type import IO, Lambda, _, forall, hkt

__all__ = (
    'WriterT',
    'FunctorWriterT',
    'ApplicativeWriterT',
    'AlternativeWriterT',
    'MonadWriterT',
    'MonadPlusWriterT',
    'MonadTransWriterT',
    'LiftIOWriterT',
)


a = TypeVar('a')

b = TypeVar('b')

m = TypeVar('m')

w = TypeVar('w')


@dataclass(frozen=True)
class WriterT(forall[w, m, a]):
    run : hkt[m, tuple[a, w]]


@dataclass(frozen=True)
class FunctorWriterT(Functor[WriterT[w, m, _]]):
    monoid : Monoid[w]
    inst : Functor[m]

    def map(self, f : Lambda[a, b], x : WriterT[w, m, a], /) -> WriterT[w, m, b]:
        match self:
            case FunctorWriterT(monoid, inst):
                def g(_ : tuple[a, w], /) -> tuple[b, w]:
                    match _:
                        case (x, w):
                            return (f(x), w)
                return WriterT(inst.map(g, x.run))


@dataclass(frozen=True)
class ApplicativeWriterT(FunctorWriterT[w, m], Applicative[WriterT[w, m, _]]):
    monoid : Monoid[w]
    inst : Applicative[m]

    def pure(self, x : a, /) -> WriterT[w, m, a]:
        match self:
            case ApplicativeWriterT(monoid, inst):
                return WriterT(inst.pure((x, monoid.empty())))

    def apply(self, f : WriterT[w, m, Lambda[a, b]], x : WriterT[w, m, a], /) -> WriterT[w, m, b]:
        match self:
            case ApplicativeWriterT(monoid, inst):
                def g(_ : tuple[Lambda[a, b], w], /) -> tuple[b, w]:
                    match _:
                        case (f, w):
                            def h(_ : tuple[a, w], /) -> tuple[b, w]:
                                match _:
                                    case (x, w_):
                                        return (f(x), monoid.append(w, w_))
                            return h
                return WriterT(inst.apply(inst.map(g, f.run), x.run))


@dataclass(frozen=True)
class AlternativeWriterT(ApplicativeWriterT[w, m], Alternative[WriterT[w, m, _]]):
    monoid : Monoid[w]
    inst : Alternative[m]

    def empty(self, /) -> WriterT[w, m, a]:
        match self:
            case AlternativeWriterT(monoid, inst):
                return WriterT(inst.empty())

    def alt(self, x : WriterT[w, m, a], y : WriterT[w, m, a], /) -> WriterT[w, m, a]:
        match self:
            case AlternativeWriterT(monoid, inst):
                return WriterT(inst.alt(x.run, y.run))


@dataclass(frozen=True)
class MonadWriterT(ApplicativeWriterT[w, m], Monad[WriterT[w, m, _]]):
    monoid : Monoid[w]
    inst : Monad[m]

    def bind(self, m : WriterT[w, m, a], k : Lambda[a, WriterT[w, m, b]], /) -> WriterT[w, m, b]:
        match self:
            case MonadWriterT(monoid, inst):
                def k_(_ : tuple[a, w], /) -> hkt[m, tuple[b, w]]:
                    match _:
                        case (x, w):
                            def k__(_ : tuple[b, w], /) -> hkt[m, tuple[b, w]]:
                                match _:
                                    case (y, w_):
                                        return inst.pure((y, monoid.append(w, w_)))
                            return inst.bind(k(x).run, k__)
                return WriterT(inst.bind(m.run, k_))


@dataclass(frozen=True)
class MonadPlusWriterT(AlternativeWriterT[w, m], MonadWriterT[w, m], MonadPlus[WriterT[w, m, _]]):
    monoid : Monoid[w]
    inst : MonadPlus[m]


@dataclass(frozen=True)
class MonadTransWriterT(MonadTrans[WriterT[w, _, _]]):
    monoid : Monoid[w]

    def lift(self, inst : Monad[m], m : hkt[m, a], /) -> WriterT[w, m, a]:
        match self:
            case MonadTransWriterT(monoid):
                return WriterT(inst.bind(m, lambda x, /: inst.pure((x, monoid.empty()))))


@dataclass(frozen=True)
class LiftIOWriterT(MonadWriterT[w, m], LiftIO[WriterT[w, m, _]]):
    monoid : Monoid[w]
    inst : LiftIO[m]

    def liftIO(self, m : IO[a], /) -> WriterT[w, m, a]:
        match self:
            case LiftIOWriterT(monoid, inst):
                return WriterT(inst.bind(inst.liftIO(m), lambda x, /: inst.pure((x, monoid.empty()))))
