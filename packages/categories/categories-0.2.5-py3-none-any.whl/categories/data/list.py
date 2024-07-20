from __future__ import annotations

from typing import TypeVar

from categories.type import Expr, Lambda

__all__ = (
    'cons',
    'head',
    'tail',
    'filter',
    'foldl',
    'foldr',
    'map',
    'scanl',
    'scanr',
    'unfoldr',
)


a = TypeVar('a')

b = TypeVar('b')


def cons(x : a, xs : list[a], /) -> list[a]:
    return [x, *xs]


def head(xs : list[a], /) -> a:
    match xs:
        case []:
            assert None
        case [x, *_]:
            return x


def tail(xs : list[a], /) -> list[a]:
    match xs:
        case []:
            return []
        case [_, *xs]:
            return xs


def filter(f : Lambda[a, bool], xs : list[a], /) -> list[a]:
    return [x for x in xs if f(x)]


def foldl(f : Expr[[b, a], b], z : b, xs : list[a], /) -> b:
    match xs:
        case []:
            return z
        case [x, *xs]:
            return foldl(f, f(z, x), xs)


def foldr(f : Expr[[a, b], b], z : b, xs : list[a], /) -> b:
    match xs:
        case []:
            return z
        case [x, *xs]:
            return f(x, foldr(f, z, xs))


def map(f : Lambda[a, b], xs : list[a], /) -> list[b]:
    return [f(x) for x in xs]


def scanl(f : Expr[[b, a], b], z : b, xs : list[a], /) -> list[b]:
    match xs:
        case []:
            return [z]
        case [x, *xs]:
            return [z, *scanl(f, f(z, x), xs)]


def scanr(f : Expr[[a, b], b], z : b, xs : list[a], /) -> list[b]:
    match xs:
        case []:
            return [z]
        case [x, *xs]:
            match scanr(f, z, xs):
                case [y, *_] as ys:
                    return [f(x, y), *ys]


def unfoldr(f : Lambda[b, None | tuple[a, b]], z : b, /) -> list[a]:
    match f(z):
        case None:
            return []
        case (x, y):
            return [x, *unfoldr(f, y)]
