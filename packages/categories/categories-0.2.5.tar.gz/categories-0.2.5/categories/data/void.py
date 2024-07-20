from __future__ import annotations

from typing import TypeVar

from categories.data.functor import Functor
from categories.type import Void, hkt

__all__ = (
    'Void',
    'absurd',
    'vacuous',
)


a = TypeVar('a')

f = TypeVar('f')


def absurd(_ : Void, /) -> a: ...


def vacuous(inst : Functor[f], _ : hkt[f, Void], /) -> hkt[f, a]:
    return inst.map(absurd, _)
