from __future__ import annotations

from typing import TypeVar

from categories.type import Expr, Lambda

__all__ = (
    'Curry',
    'fst',
    'snd',
    'curry',
    'uncurry',
    'swap',
)


a = TypeVar('a')

b = TypeVar('b')

c = TypeVar('c')


Curry = Lambda[a, Lambda[b, c]]


def fst(z : tuple[a, b], /) -> a:
    match z:
        case (x, _):
            return x


def snd(z : tuple[a, b], /) -> b:
    match z:
        case (_, y):
            return y


def curry(f : Expr[[a, b], c], /) -> Curry[a, b, c]:
    return lambda x, /: lambda y, /: f(x, y)


def uncurry(f : Curry[a, b, c], /) -> Expr[[a, b], c]:
    return lambda x, y, /: f(x)(y)


def swap(z : tuple[a, b], /) -> tuple[b, a]:
    match z:
        case (x, y):
            return (y, x)
