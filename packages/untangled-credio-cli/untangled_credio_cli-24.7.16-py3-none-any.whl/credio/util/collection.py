from typing import Any, Callable, List, Optional, Type, TypeVar

from .type import Object


T = TypeVar("T")


def first(
    collection: List[Any], cast: Optional[Callable[..., T]] = None
) -> Optional[T]:
    """Returns first element of given collection."""
    found = (collection or [None])[0]
    if found is not None and cast is not None:
        return cast(found)
    return found


def notnone(collection: List[Any], cast: Optional[Callable[..., T]] = None) -> List[T]:
    found: List[T] = []
    for e in collection:
        if e is not None:
            found.append(e if cast is None else cast(e))
    return found
