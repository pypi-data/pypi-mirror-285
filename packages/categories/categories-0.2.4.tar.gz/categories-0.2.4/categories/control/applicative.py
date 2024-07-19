from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

from categories.data.functor import Functor, FunctorIO, FunctorLambda, FunctorList
from categories.type import IO, Lambda, _, hkt, typeclass

__all__ = (
    'Applicative',
    'ApplicativeIO',
    'ApplicativeLambda',
    'ApplicativeList',
)


a = TypeVar('a')

b = TypeVar('b')

f = TypeVar('f')

r = TypeVar('r')


@dataclass(frozen=True)
class Applicative(Functor[f], typeclass[f]):
    def pure(self, x : a, /) -> hkt[f, a]: ...

    def apply(self, f : hkt[f, Lambda[a, b]], x : hkt[f, a], /) -> hkt[f, b]: ...

    def seq(self, _ : hkt[f, a], x : hkt[f, b], /) -> hkt[f, b]:
        return self.apply(self.const(lambda x, /: x, _), x)


@dataclass(frozen=True)
class ApplicativeIO(FunctorIO, Applicative[IO]):
    async def pure(self, x : a, /) -> a:
        return x

    async def apply(self, m : IO[Lambda[a, b]], m_ : IO[a], /) -> b:
        match await m, await m_:
            case f, x:
                return f(x)

    async def seq(self, m : IO[a], k : IO[b], /) -> b:
        match await m:
            case _:
                return await k


@dataclass(frozen=True)
class ApplicativeLambda(FunctorLambda[r], Applicative[Lambda[r, _]]):
    def pure(self, x : a, /) -> Lambda[r, a]:
        return lambda _, /: x

    def apply(self, f : Lambda[r, Lambda[a, b]], g : Lambda[r, a], /) -> Lambda[r, b]:
        return lambda x, /: f(x)(g(x))


@dataclass(frozen=True)
class ApplicativeList(FunctorList, Applicative[list]):
    def pure(self, x : a, /) -> list[a]:
        return [x]

    def apply(self, fs : list[Lambda[a, b]], xs : list[a], /) -> list[b]:
        return [f(x) for f in fs for x in xs]
