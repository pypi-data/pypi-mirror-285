from __future__ import annotations

from dataclasses import dataclass
from itertools import count
from typing import TypeVar

from categories.type import Stream, typeclass

__all__ = (
    'Bounded',
    'Enum',
    'boundedEnumFrom',
    'boundedEnumFromThen',
)


a = TypeVar('a')


@dataclass(frozen=True)
class Bounded(typeclass[a]):
    def min(self, /) -> a: ...

    def max(self, /) -> a: ...


@dataclass(frozen=True)
class Enum(typeclass[a]):
    def succ(self, x : a, /) -> a:
        return self.toEnum(self.fromEnum(x) + 1)

    def pred(self, x : a, /) -> a:
        return self.toEnum(self.fromEnum(x) - 1)

    def toEnum(self, x : int, /) -> a: ...

    def fromEnum(self, x : a, /) -> int: ...

    def enumFrom(self, x : a, /) -> Stream[a]:
        return map(self.toEnum, count(self.fromEnum(x)))

    def enumFromThen(self, x : a, y : a, /) -> Stream[a]:
        return map(self.toEnum, count(self.fromEnum(x), self.fromEnum(y) - self.fromEnum(x)))

    def enumFromTo(self, x : a, y : a, /) -> Stream[a]:
        return map(self.toEnum, range(self.fromEnum(x), self.fromEnum(y) + 1))

    def enumFromThenTo(self, x : a, y : a, z : a, /) -> Stream[a]:
        return map(self.toEnum, range(self.fromEnum(x), self.fromEnum(z) + 1, self.fromEnum(y) - self.fromEnum(x)))


def boundedEnumFrom(enum : Enum[a], bounded : Bounded[a], x : a, /) -> Stream[a]:
    return map(enum.toEnum, range(enum.fromEnum(x), enum.fromEnum(bounded.max()) + 1))


def boundedEnumFromThen(enum : Enum[a], bounded : Bounded[a], x : a, y : a, /) -> Stream[a]:
    match enum.fromEnum(x), enum.fromEnum(y):
        case x_, y_ if y_ >= x_:
            return map(enum.toEnum, range(x_, enum.fromEnum(bounded.max()) + 1, y_ - x_))
        case x_, y_:
            return map(enum.toEnum, range(x_, enum.fromEnum(bounded.min()) - 1, y_ - x_))
