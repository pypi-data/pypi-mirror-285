from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

from categories.control.applicative import Applicative
from categories.control.monad import Monad
from categories.data.functor import Functor
from categories.type import Lambda, forall

__all__ = (
    'Node',
    'FunctorNode',
    'ApplicativeNode',
    'MonadNode',
)


a = TypeVar('a')

b = TypeVar('b')


@dataclass(frozen=True)
class Node(forall[a]):
    x  : a
    xs : list[Node[a]]


@dataclass(frozen=True)
class FunctorNode(Functor[Node]):
    def map(self, f : Lambda[a, b], n : Node[a], /) -> Node[b]:
        match n:
            case Node(x, xs):
                return Node(f(x), [self.map(f, x) for x in xs])

    def const(self, x : a, _ : Node[b], /) -> Node[a]:
        match _:
            case Node(_, xs):
                return Node(x, [self.const(x, _) for _ in xs])


@dataclass(frozen=True)
class ApplicativeNode(FunctorNode, Applicative[Node]):
    def pure(self, x : a, /) -> Node[a]:
        return Node(x, [])

    def apply(self, n : Node[Lambda[a, b]], n_ : Node[a], /) -> Node[b]:
        match n, n_:
            case Node(f, fs), Node(x, xs):
                return Node(f(x), [self.map(f, x) for x in xs] + [self.apply(f, n_) for f in fs])

    def seq(self, _ : Node[a], n : Node[b], /) -> Node[b]:
        match _, n:
            case Node(_, xs), Node(y, ys):
                return Node(y, ys + [self.seq(x, n) for x in xs])


@dataclass(frozen=True)
class MonadNode(ApplicativeNode, Monad[Node]):
    def bind(self, n : Node[a], k : Lambda[a, Node[b]], /) -> Node[b]:
        match n:
            case Node(x, xs):
                match k(x):
                    case Node(y, ys):
                        return Node(y, ys + [self.bind(x, k) for x in xs])
