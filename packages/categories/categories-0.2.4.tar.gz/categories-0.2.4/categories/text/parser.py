from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

from categories.control.alternative import Alternative
from categories.control.applicative import Applicative
from categories.control.monad import Monad
from categories.control.monadplus import MonadPlus
from categories.data.functor import Functor
from categories.type import Lambda

__all__ = (
    'Parser',
    'FunctorParser',
    'ApplicativeParser',
    'AlternativeParser',
    'MonadParser',
    'MonadPlusParser',
)


a = TypeVar('a')

b = TypeVar('b')


Parser = Lambda[str, list[tuple[a, str]]]


@dataclass(frozen=True)
class FunctorParser(Functor[Parser]):
    def map(self, f : Lambda[a, b], p : Parser[a], /) -> Parser[b]:
        return lambda s, /: [(f(x), s) for (x, s) in p(s)]


@dataclass(frozen=True)
class ApplicativeParser(FunctorParser, Applicative[Parser]):
    def pure(self, x : a, /) -> Parser[a]:
        return lambda s, /: [(x, s)]

    def apply(self, p : Parser[Lambda[a, b]], q : Parser[a], /) -> Parser[b]:
        return lambda s, /: [(f(x), s) for (f, s) in p(s) for (x, s) in q(s)]


@dataclass(frozen=True)
class AlternativeParser(ApplicativeParser, Alternative[Parser]):
    def empty(self, /) -> Parser[a]:
        return lambda _, /: []

    def alt(self, p : Parser[a], q : Parser[a], /) -> Parser[a]:
        return lambda s, /: p(s) or q(s)

    def some(self, p : Parser[a], /) -> Parser[list[a]]:
        return lambda s, /: [([x, *xs], s) for (x, s) in p(s) for (xs, s) in self.many(p)(s)]

    def many(self, p : Parser[a], /) -> Parser[list[a]]:
        return self.alt(self.some(p), self.pure([]))


@dataclass(frozen=True)
class MonadParser(ApplicativeParser, Monad[Parser]):
    def bind(self, p : Parser[a], k : Lambda[a, Parser[b]], /) -> Parser[b]:
        return lambda s, /: [(y, s) for (x, s) in p(s) for (y, s) in k(x)(s)]


@dataclass(frozen=True)
class MonadPlusParser(AlternativeParser, MonadParser, MonadPlus[Parser]): ...
