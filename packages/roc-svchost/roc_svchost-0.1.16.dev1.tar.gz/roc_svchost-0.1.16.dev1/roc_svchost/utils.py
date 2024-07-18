from typing import Iterable, TypeVar

T = TypeVar('T')
Item = T | None


def first(iterable: Iterable[T], default: Item = None) -> Item:
    return next(iter(iterable), default)