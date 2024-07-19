from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

from categories.type import IO, Lambda, _, hkt, typeclass

__all__ = (
    'Functor',
    'FunctorIO',
    'FunctorLambda',
    'FunctorList',
)


a = TypeVar('a')

b = TypeVar('b')

f = TypeVar('f')

r = TypeVar('r')


@dataclass(frozen=True)
class Functor(typeclass[f]):
    def map(self, f : Lambda[a, b], x : hkt[f, a], /) -> hkt[f, b]: ...

    def const(self, x : a, _ : hkt[f, b], /) -> hkt[f, a]:
        return self.map(lambda _, /: x, _)


@dataclass(frozen=True)
class FunctorIO(Functor[IO]):
    async def map(self, f : Lambda[a, b], m : IO[a], /) -> b:
        match await m:
            case x:
                return f(x)

    async def const(self, x : a, _ : IO[b], /) -> a:
        match await _:
            case _:
                return x


@dataclass(frozen=True)
class FunctorLambda(Functor[Lambda[r, _]]):
    def map(self, f : Lambda[a, b], g : Lambda[r, a], /) -> Lambda[r, b]:
        return lambda x, /: f(g(x))


@dataclass(frozen=True)
class FunctorList(Functor[list]):
    def map(self, f : Lambda[a, b], xs : list[a], /) -> list[b]:
        return [f(x) for x in xs]
