import dataclasses
import threading
from aiohttp import web
import jmespath
from typing import Any, Awaitable, Callable, List, Optional, Tuple, Type, TypeVar, Union

from credio.util.log import log


V = TypeVar("V")

Guard = Callable[
    [Callable[..., Awaitable[web.Response]]], Callable[..., Awaitable[web.Response]]
]
"""Type of guards."""

Matcher = Callable[[str], bool]
"""Type of path matchers."""


class Object(dict):
    """A wrapper class for type `dict`."""

    def __init__(self, obj: Optional[Any] = {}, *args, **kwargs):
        super().__init__()
        if isinstance(obj, dict):
            for key, value in obj.items():
                self.set(str(key), value)
        elif isinstance(obj, list) or isinstance(obj, set) or isinstance(obj, tuple):
            for i in range(len(obj)):
                self.set(str(i), None)
            self.assign(*obj)
        elif hasattr(obj, "__dict__"):
            for key in obj.__dict__:
                self.set(str(key), getattr(obj, key))
        else:
            raise Exception(f"Incompatible object: {obj}")

    def get(self, key: str, type: Type[V] = object) -> Optional[V]:
        if key in self.keys():
            return self[key]

    def set(self, key: str, value: Any):
        if key is not None and not key.startswith("__"):  # ignore private attributes
            setattr(self, key, value)
            self[key] = value
        return self

    def remove(self, key: str):
        if key in self.keys():
            del self[key]

    def attrs(self, ignore: List[str] = []) -> Tuple[str]:
        attrs: List[str] = []
        for key in self.keys():
            attr = str(key)
            if attr.startswith("__"):
                continue  # ignore private attributes
            if attr not in ignore:
                attrs.append(attr)
        return tuple(attrs)  # type: ignore

    def values(
        self,
        attrs: Optional[Tuple[str]] = None,
        ignore: List[str] = [],
    ):
        vals = []
        if attrs is None:
            attrs = self.attrs(ignore=ignore)
        for attr in attrs:
            val = None
            if attr in self.keys():
                val = self[attr]
            vals.append(val)
        return tuple(vals)

    def assign(self, *args):
        attrs = self.attrs()
        for i in range(len(attrs)):
            if i >= len(args):
                break
            self[attrs[i]] = args[i]
        return self

    def __str__(self):
        this = {}
        for attr in self.attrs():
            this[attr] = self[attr]
        return str(this)

    def __hash__(self):
        return hash(str(self))

    def select(
        self,
        key: Optional[str] = "",
        type: Type[V] = object,
        default_value: Optional[V] = None,
        strict: bool = False,
    ) -> Optional[V]:
        """Recursively obtains value for a specific composite key using JMESPath expression."""
        value = default_value
        try:
            if key in ["", None]:
                key = ""
                value = self  # type: ignore
            else:
                value: Optional[V] = jmespath.search(str(key), self) or default_value
        except:
            pass
        if strict and not isinstance(value, type):
            error_params = (
                __class__.__name__ + (key if key == "" else f".{key}"),
                type.__name__ if type is not None else "None",
                value.__class__.__name__ if value is not None else None,
            )
            raise TypeError("'%s' must be '%s' but actually '%s'" % error_params)
        return value


def lazyclass(init: Union[Type[V], Callable[..., V]], *args, **kwargs) -> Type[V]:
    """
    Returns a lazy type for a specific type.

    Parameters:
    - init (class/function): type or function to create the instance.
    """

    if init is None or not callable(init):
        raise TypeError("Type must not be 'None' or uncallable")

    @dataclasses.dataclass
    class _Holder:
        """Closure instance for holding actual object."""

        initialized: bool
        lock: threading.Lock
        obj: Optional[V]
        """Actual object."""

    _holder = _Holder(False, threading.Lock(), None)

    def _init_obj(proxy: object):
        """Actually initializes holding object."""
        if not _holder.initialized:
            with _holder.lock:
                if not _holder.initialized:
                    for k, v in init.__dict__.items():
                        if isinstance(v, staticmethod):
                            setattr(
                                proxy, k, v
                            )  # ensure in-constructor static method invocation not failed
                    _holder.obj = init(*args, **kwargs)
                    for k, v in _holder.obj.__dict__.items():
                        setattr(proxy, k, v)  # update proxy attributes
                    _holder.initialized = True
                    setattr(proxy, "__class__", _holder.obj.__class__)

    class _Object:
        def __getattribute__(self, name: str) -> Any:
            _init_obj(self)
            return getattr(_holder.obj, name)

        def __str__(self):
            _init_obj(self)
            return str(_holder.obj)

    log("Marked object '%s' as Lazy" % init.__name__)
    return _Object  # type: ignore


def lazy(init: Union[Type[V], Callable[..., V]], *args, **kwargs) -> V:
    """
    Returns a lazy instance for a specific type.

    Parameters:
    - init (class/function): type or function to create the instance.
    """
    return lazyclass(init, *args, *kwargs)()
