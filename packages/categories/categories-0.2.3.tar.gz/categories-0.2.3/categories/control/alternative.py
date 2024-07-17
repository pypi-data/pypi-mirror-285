from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

from categories.control.applicative import Applicative, ApplicativeIO, ApplicativeList
from categories.type import IO, hkt, typeclass

__all__ = (
    'Alternative',
    'AlternativeIO',
    'AlternativeList',
)


a = TypeVar('a')

b = TypeVar('b')

f = TypeVar('f')


@dataclass(frozen=True)
class Alternative(Applicative[f], typeclass[f]):
    def empty(self, /) -> hkt[f, a]: ...

    def alt(self, x : hkt[f, a], y : hkt[f, a], /) -> hkt[f, a]: ...

    def some(self, v : hkt[f, a], /) -> hkt[f, list[a]]:
        return self.apply(self.map(lambda x, /: lambda xs, /: [x, *xs], v), self.many(v))

    def many(self, v : hkt[f, a], /) -> hkt[f, list[a]]:
        return self.alt(self.some(v), self.pure([]))


@dataclass(frozen=True)
class AlternativeIO(ApplicativeIO, Alternative[IO]):
    async def empty(self, /) -> a:
        raise Exception

    async def alt(self, m : IO[a], m_ : IO[a], /) -> a:
        try:
            return await m
        except BaseException:
            return await m_


@dataclass(frozen=True)
class AlternativeList(ApplicativeList, Alternative[list]):
    def empty(self, /) -> list[a]:
        return []

    def alt(self, xs : list[a], ys : list[a], /) -> list[a]:
        return xs + ys
