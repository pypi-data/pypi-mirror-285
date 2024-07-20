from __future__ import annotations

from builtins import frozenset as Set
from collections.abc import Callable as Expr
from collections.abc import Coroutine as Action
from collections.abc import Iterator as Stream
from types import MappingProxyType as Map
from typing import Annotated as hkt
from typing import Any as _
from typing import Generic as forall
from typing import NoReturn as Void
from typing import Protocol as typeclass
from typing import TypeVar

__all__ = (
    'Delay',
    'Action',
    'Expr',
    'IO',
    'Lambda',
    'Map',
    'Set',
    'Stream',
    'Void',
    '_',
    'forall',
    'hkt',
    'typeclass',
)


a = TypeVar('a')

b = TypeVar('b')


Delay = Expr[[], a]

IO = Action[_, _, a]

Lambda = Expr[[a], b]
