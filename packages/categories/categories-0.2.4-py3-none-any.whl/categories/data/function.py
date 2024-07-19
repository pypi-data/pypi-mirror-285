from __future__ import annotations

from typing import TypeVar

from categories.type import Expr, Lambda

__all__ = (
    'fix',
    'o',
    'id',
    'const',
    'apply',
    'reverse',
    'flip',
    'on',
    'when',
)


a = TypeVar('a')

b = TypeVar('b')

c = TypeVar('c')


def fix(f : Expr[..., a], /) -> Expr[..., a]:
    return (x := lambda *_: f(x, *_))


def o(f : Lambda[b, c], g : Lambda[a, b], /) -> Lambda[a, c]:
    return lambda x, /: f(g(x))


def id(x : a, /) -> a:
    return x


def const(x : a, /) -> Lambda[b, a]:
    return lambda _, /: x


def apply(f : Lambda[a, b], x : a, /) -> b:
    return f(x)


def reverse(x : a, f : Lambda[a, b], /) -> b:
    return f(x)


def flip(f : Expr[[a, b], c], /) -> Expr[[b, a], c]:
    return lambda x, y, /: f(y, x)


def on(f : Expr[[b, b], c], g : Lambda[a, b], /) -> Expr[[a, a], c]:
    return lambda x, y, /: f(g(x), g(y))


def when(p : bool, f : Lambda[a, a], x : a, /) -> a:
    return f(x) if p else x