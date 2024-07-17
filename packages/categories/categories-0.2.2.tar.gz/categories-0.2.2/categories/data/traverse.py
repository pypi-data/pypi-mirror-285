from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

from categories.control.applicative import Applicative
from categories.data.fold import Fold
from categories.data.functor import Functor
from categories.type import Lambda, hkt, typeclass

__all__ = (
    'Traverse',
)


a = TypeVar('a')

b = TypeVar('b')

f = TypeVar('f')

t = TypeVar('t')


@dataclass(frozen=True)
class Traverse(Functor[t], Fold[t], typeclass[t]):
    def traverse(self, inst : Applicative[f],
                 f : Lambda[a, hkt[f, b]], xs : hkt[t, a], /) -> hkt[f, hkt[t, b]]:
        return self.sequence(inst, self.map(f, xs))

    def sequence(self, inst : Applicative[f],
                  xs : hkt[t, hkt[f, a]], /) -> hkt[f, hkt[t, a]]:
        return self.traverse(inst, lambda x, /: x, xs)
