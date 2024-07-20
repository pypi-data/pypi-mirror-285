from __future__ import annotations

from dataclasses import dataclass
from functools import reduce
from typing import TypeVar

from categories.control.monad import Monad
from categories.data.all import All, MonoidAll
from categories.data.any import Any, MonoidAny
from categories.data.dual import Dual, MonoidDual
from categories.data.endo import Endo, MonoidEndo
from categories.data.eq import Eq
from categories.data.max import Max, MonoidMax
from categories.data.maybe import Maybe, Nothing, Just
from categories.data.min import Min, MonoidMin
from categories.data.monoid import Monoid
from categories.data.num import Num
from categories.data.ord import Ord
from categories.data.product import Product, MonoidProduct
from categories.data.sum import Sum, MonoidSum
from categories.type import Expr, Lambda, hkt, typeclass

__all__ = (
    'Fold',
    'FoldList',
    'foldrM',
    'foldlM',
)


a = TypeVar('a')

b = TypeVar('b')

m = TypeVar('m')

t = TypeVar('t')


@dataclass(frozen=True)
class Fold(typeclass[t]):
    def fold(self, inst : Monoid[m], xs : hkt[t, m], /) -> m:
        return self.foldMap(inst, lambda x, /: x, xs)

    def foldMap(self, inst : Monoid[m], f : Lambda[a, m], xs : hkt[t, a], /) -> m:
        def g(x : a, y : m, /) -> m:
            return inst.append(f(x), y)
        return self.foldr(g, inst.empty(), xs)

    def foldMap_(self, inst : Monoid[m], f : Lambda[a, m], xs : hkt[t, a], /) -> m:
        def g(x : m, y : a, /) -> m:
            return inst.append(x, f(y))
        return self.foldl_(g, inst.empty(), xs)

    def foldr(self, f : Expr[[a, b], b], z : b, xs : hkt[t, a], /) -> b:
        def g(x : a, /) -> Endo[b]:
            return Endo(lambda y, /: f(x, y))
        return self.foldMap(MonoidEndo(), g, xs).endo(z)

    def foldr_(self, f : Expr[[a, b], b], z : b, xs : hkt[t, a], /) -> b:
        def g(k : Lambda[b, b], x : a, /) -> Lambda[b, b]:
            return lambda y, /: k(f(x, y))
        return self.foldl(g, lambda x, /: x, xs)(z)

    def foldl(self, f : Expr[[b, a], b], z : b, xs : hkt[t, a], /) -> b:
        def g(x : a, /) -> Dual[Endo[b]]:
            return Dual(Endo(lambda y, /: f(y, x)))
        return self.foldMap(MonoidDual(MonoidEndo()), g, xs).dual.endo(z)

    def foldl_(self, f : Expr[[b, a], b], z : b, xs : hkt[t, a], /) -> b:
        def g(x : a, k : Lambda[b, b], /) -> Lambda[b, b]:
            return lambda y, /: k(f(y, x))
        return self.foldr(g, lambda x, /: x, xs)(z)

    def foldr1(self, f : Expr[[a, a], a], xs : hkt[t, a], /) -> a:
        def g(x : a, m : Maybe[a], /) -> Maybe[a]:
            match m:
                case Nothing():
                    return Just(x)
                case Just(y):
                    return Just(f(x, y))

        match self.foldr(g, Nothing(), xs):
            case Nothing():
                assert None
            case Just(x):
                return x

    def foldl1(self, f : Expr[[a, a], a], xs : hkt[t, a], /) -> a:
        def g(m : Maybe[a], y : a, /) -> Maybe[a]:
            match m:
                case Nothing():
                    return Just(y)
                case Just(x):
                    return Just(f(x, y))

        match self.foldl(g, Nothing(), xs):
            case Nothing():
                assert None
            case Just(x):
                return x

    def list(self, xs : hkt[t, a], /) -> list[a]:
        return self.foldr(lambda x, xs, /: [x, *xs], [], xs)

    def null(self, xs : hkt[t, a], /) -> bool:
        return self.foldr(lambda _, __, /: False, True, xs)

    def length(self, xs : hkt[t, a], /) -> int:
        return self.foldl_(lambda n, _, /: n + 1, 0, xs)

    def elem(self, inst : Eq[a], x : a, xs : hkt[t, a], /) -> bool:
        return self.any(lambda y, /: inst.eq(x, y), xs)

    def max(self, inst : Ord[a], xs : hkt[t, a], /) -> a:
        match self.foldMap_(MonoidMax(inst), lambda x, /: Max(Just(x)), xs).max:
            case Nothing():
                assert None
            case Just(x):
                return x

    def min(self, inst : Ord[a], xs : hkt[t, a], /) -> a:
        match self.foldMap_(MonoidMin(inst), lambda x, /: Min(Just(x)), xs).min:
            case Nothing():
                assert None
            case Just(x):
                return x

    def sum(self, inst : Num[a], xs : hkt[t, a], /) -> a:
        return self.foldMap_(MonoidSum(inst), Sum, xs).sum

    def product(self, inst : Num[a], xs : hkt[t, a], /) -> a:
        return self.foldMap_(MonoidProduct(inst), Product, xs).product

    def any(self, p : Lambda[a, bool], xs : hkt[t, a], /) -> bool:
        return self.foldMap(MonoidAny(), lambda x, /: Any(p(x)), xs).any

    def all(self, p : Lambda[a, bool], xs : hkt[t, a], /) -> bool:
        return self.foldMap(MonoidAll(), lambda x, /: All(p(x)), xs).all


@dataclass(frozen=True)
class FoldList(Fold[list]):
    def fold(self, inst : Monoid[m], xs : list[m], /) -> m:
        return inst.concat(xs)

    def foldMap(self, inst : Monoid[m], f : Lambda[a, m], xs : list[a], /) -> m:
        return inst.concat([f(x) for x in xs])

    def foldMap_(self, inst : Monoid[m], f : Lambda[a, m], xs : list[a], /) -> m:
        return inst.concat([f(x) for x in xs])

    def foldr(self, f : Expr[[a, b], b], z : b, xs : list[a], /) -> b:
        match xs:
            case []:
                return z
            case [x, *xs]:
                return f(x, self.foldr(f, z, xs))

    def foldr_(self, f : Expr[[a, b], b], z : b, xs : list[a], /) -> b:
        return reduce(lambda x, y, /: f(y, x), reversed(xs), z)

    def foldl(self, f : Expr[[b, a], b], z : b, xs : list[a], /) -> b:
        match xs:
            case []:
                return z
            case [x, *xs]:
                return self.foldl(f, f(z, x), xs)

    def foldl_(self, f : Expr[[b, a], b], z : b, xs : list[a], /) -> b:
        return reduce(f, xs, z)

    def list(self, xs : list[a], /) -> list[a]:
        return xs

    def null(self, xs : list[a], /) -> bool:
        match xs:
            case []:
                return True
            case [_, *_]:
                return False

    def length(self, xs : list[a], /) -> int:
        return len(xs)

    def elem(self, inst : Eq[a], x : a, xs : list[a], /) -> bool:
        return any(map(lambda y, /: inst.eq(x, y), xs))

    def max(self, inst : Ord[a], xs : list[a], /) -> a:
        return reduce(lambda x, y, /: x if inst.ge(x, y) else y, xs)

    def min(self, inst : Ord[a], xs : list[a], /) -> a:
        return reduce(lambda x, y, /: x if inst.le(x, y) else y, xs)

    def sum(self, inst : Num[a], xs : list[a], /) -> a:
        return reduce(inst.add, xs, inst.int(0))

    def product(self, inst : Num[a], xs : list[a], /) -> a:
        return reduce(inst.mul, xs, inst.int(1))

    def any(self, p : Lambda[a, bool], xs : list[a], /) -> bool:
        return any(map(p, xs))

    def all(self, p : Lambda[a, bool], xs : list[a], /) -> bool:
        return all(map(p, xs))


def foldrM(fold : Fold[t], monad : Monad[m],
           f : Expr[[a, b], hkt[m, b]], z : b, xs : hkt[t, a], /) -> hkt[m, b]:
    def g(k : Lambda[b, hkt[m, b]], x : a, /) -> Lambda[b, hkt[m, b]]:
        return lambda y, /: monad.bind(f(x, y), k)
    return fold.foldl(g, monad.pure, xs)(z)


def foldlM(fold : Fold[t], monad : Monad[m],
           f : Expr[[b, a], hkt[m, b]], z : b, xs : hkt[t, a], /) -> hkt[m, b]:
    def g(x : a, k : Lambda[b, hkt[m, b]], /) -> Lambda[b, hkt[m, b]]:
        return lambda y, /: monad.bind(f(y, x), k)
    return fold.foldr(g, monad.pure, xs)(z)
