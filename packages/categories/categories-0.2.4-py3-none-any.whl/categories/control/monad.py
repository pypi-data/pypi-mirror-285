from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

from categories.control.applicative import Applicative, ApplicativeIO, ApplicativeLambda, ApplicativeList
from categories.type import IO, Lambda, _, hkt, typeclass

__all__ = (
    'Monad',
    'MonadIO',
    'MonadLambda',
    'MonadList',
)


a = TypeVar('a')

b = TypeVar('b')

m = TypeVar('m')

r = TypeVar('r')


@dataclass(frozen=True)
class Monad(Applicative[m], typeclass[m]):
    def bind(self, m : hkt[m, a], k : Lambda[a, hkt[m, b]], /) -> hkt[m, b]:
        return self.join(self.map(k, m))

    def join(self, m : hkt[m, hkt[m, a]], /) -> hkt[m, a]:
        return self.bind(m, lambda x, /: x)

    def seq(self, m : hkt[m, a], k : hkt[m, b], /) -> hkt[m, b]:
        return self.bind(m, lambda _, /: k)


@dataclass(frozen=True)
class MonadIO(ApplicativeIO, Monad[IO]):
    async def bind(self, m : IO[a], k : Lambda[a, IO[b]], /) -> b:
        match await m:
            case x:
                return await k(x)

    async def join(self, m : IO[IO[a]], /) -> a:
        match await m:
            case x:
                return await x


@dataclass(frozen=True)
class MonadLambda(ApplicativeLambda[r], Monad[Lambda[r, _]]):
    def bind(self, f : Lambda[r, a], k : Lambda[a, Lambda[r, b]], /) -> Lambda[r, b]:
        return lambda r, /: k(f(r))(r)


@dataclass(frozen=True)
class MonadList(ApplicativeList, Monad[list]):
    def bind(self, xs : list[a], f : Lambda[a, list[b]], /) -> list[b]:
        return [y for x in xs for y in f(x)]

    def join(self, xss : list[list[a]], /) -> list[a]:
        return [x for xs in xss for x in xs]
