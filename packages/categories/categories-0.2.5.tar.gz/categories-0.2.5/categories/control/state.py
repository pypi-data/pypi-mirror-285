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
    'StateT',
    'FunctorStateT',
    'ApplicativeStateT',
    'AlternativeStateT',
    'MonadStateT',
    'MonadPlusStateT',
    'MonadTransStateT',
    'LiftIOStateT',
)


a = TypeVar('a')

b = TypeVar('b')

m = TypeVar('m')

s = TypeVar('s')


@dataclass(frozen=True)
class StateT(forall[s, m, a]):
    run : Lambda[s, hkt[m, tuple[a, s]]]


@dataclass(frozen=True)
class FunctorStateT(Functor[StateT[s, m, _]]):
    inst : Functor[m]

    def map(self, f : Lambda[a, b], x : StateT[s, m, a], /) -> StateT[s, m, b]:
        match self:
            case FunctorStateT(inst):
                def g(_ : tuple[a, s], /) -> tuple[b, s]:
                    match _:
                        case (x, s_):
                            return (f(x), s_)
                return StateT(lambda s, /: inst.map(g, x.run(s)))


@dataclass(frozen=True)
class ApplicativeStateT(FunctorStateT[s, m], Applicative[StateT[s, m, _]]):
    inst : Monad[m]

    def pure(self, x : a, /) -> StateT[s, m, a]:
        match self:
            case ApplicativeStateT(inst):
                return StateT(lambda s, /: inst.pure((x, s)))

    def apply(self, f : StateT[s, m, Lambda[a, b]], x : StateT[s, m, a], /) -> StateT[s, m, b]:
        match self:
            case ApplicativeStateT(inst):
                def k(_ : tuple[Lambda[a, b], s], /) -> hkt[m, tuple[b, s]]:
                    match _:
                        case (f, s_):
                            def k_(_ : tuple[a, s], /) -> hkt[m, tuple[b, s]]:
                                match _:
                                    case (x, s__):
                                        return inst.pure((f(x), s__))
                            return inst.bind(x.run(s_), k_)
                return StateT(lambda s, /: inst.bind(f.run(s), k))


@dataclass(frozen=True)
class AlternativeStateT(ApplicativeStateT[s, m], Alternative[StateT[s, m, _]]):
    inst : Alternative[m]

    def empty(self, /) -> StateT[s, m, a]:
        match self:
            case AlternativeStateT(inst):
                return StateT(lambda _, /: inst.empty())

    def alt(self, x : StateT[s, m, a], y : StateT[s, m, a], /) -> StateT[s, m, a]:
        match self:
            case AlternativeStateT(inst):
                return StateT(lambda s, /: inst.alt(x.run(s), y.run(s)))


@dataclass(frozen=True)
class MonadStateT(ApplicativeStateT[s, m], Monad[StateT[s, m, _]]):
    inst : Monad[m]

    def bind(self, m : StateT[s, m, a], k : Lambda[a, StateT[s, m, b]], /) -> StateT[s, m, b]:
        match self:
            case MonadStateT(inst):
                def k_(_ : tuple[a, s], /) -> hkt[m, tuple[b, s]]:
                    match _:
                        case (x, s_):
                            return k(x).run(s_)
                return StateT(lambda s, /: inst.bind(m.run(s), k_))


@dataclass(frozen=True)
class MonadPlusStateT(AlternativeStateT[s, m], MonadStateT[s, m], MonadPlus[StateT[s, m, _]]):
    inst : MonadPlus[m]


@dataclass(frozen=True)
class MonadTransStateT(MonadTrans[StateT[s, _, _]]):
    def lift(self, inst : Monad[m], m : hkt[m, a], /) -> StateT[s, m, a]:
        return StateT(lambda s, /: inst.bind(m, lambda x, /: inst.pure((x, s))))


@dataclass(frozen=True)
class LiftIOStateT(MonadStateT[s, m], LiftIO[StateT[s, m, _]]):
    inst : LiftIO[m]

    def liftIO(self, m : IO[a], /) -> StateT[s, m, a]:
        match self:
            case LiftIOStateT(inst):
                return StateT(lambda s, /: inst.bind(inst.liftIO(m), lambda x, /: inst.pure((x, s))))
