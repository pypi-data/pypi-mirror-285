import dataclasses
import re
import threading
from typing import Callable, Dict, Optional, Type, TypeVar, Union

from credio.util.log import log
from credio.util.type import lazyclass


T = TypeVar("T")


def _bean_name(text: str = ""):
    patterns = ["(.)([A-Z][a-z0-9]+)", "([a-z0-9])([A-Z])"]
    for pattern in patterns:
        text = re.sub(pattern, r"\1_\2", text)
    return text.lower()


class Container(dict):
    """A simple IoC container implementation."""

    def __init__(self):
        self._lock = threading.Lock()

    def get(self, bean_name: str, type: Type[T] = dict) -> Optional[T]:
        if bean_name in self.keys():
            return self[bean_name]

    def by_type(self, bean_type: Type[T]) -> T:
        for bean_name in self.keys():
            bean = self[bean_name]
            if isinstance(bean, bean_type):
                return bean
        raise Exception("Bean with type '%s' not found or invalid" % bean_type)

    def inject(self, ref_map: Dict[str, str] = {}):
        """
        Marks a class to be automatically injected with its desired attributes.

        Parameters:
        - ref_map (dict): a mapping that specifies the reference name of each attribute.
        """

        def new_cls(cls: type):
            old_init = cls.__init__

            def new_init(this, *args, **kwargs):
                for field in dataclasses.fields(this):
                    if field.name.startswith("_"):  # ignore private fields
                        continue
                    ref_name = ref_map.get(field.name) or field.name
                    ref_value = self.get(ref_name)
                    if not isinstance(ref_value, field.type):
                        raise Exception("Bean '%s' not found or invalid" % ref_name)
                    setattr(this, field.name, ref_value)
                old_init(this, *args, **kwargs)

            cls.__init__ = new_init

            return dataclasses.dataclass(cls)

        return new_cls

    def singleton(self, name: Optional[str] = None, lazy: bool = True):
        """
        Marks a class/function to be a bean creator.

        Parameters:
        - name (str): the bean name (default: name of the class/function).
        """

        def creator(cls_or_func: Union[type, Callable]):
            bean_name = _bean_name(name or cls_or_func.__name__)
            if isinstance(cls_or_func, type):
                cls = cls_or_func
                if self.get(bean_name) is not None:
                    raise Exception("Bean '%s' exists" % bean_name)
                old_init = cls.__init__

                def new_new(_):
                    bean = self.get(bean_name)
                    if bean is not None:
                        return bean
                    raise Exception("Bean '%s' not found or invalid" % bean_name)

                def new_init(this, *args, **kwargs):
                    if self.get(bean_name) is not None:
                        return
                    with self._lock:
                        if self.get(bean_name) is None:
                            old_init(this, *args, **kwargs)
                            self[bean_name] = this
                            cls.__new__ = new_new  # type: ignore
                            log("Bean '%s' initialized" % bean_name)

                cls.__init__ = new_init

                return dataclasses.dataclass(lazyclass(cls) if lazy else cls)
            else:
                func = cls_or_func
                if self.get(bean_name) is not None:
                    raise Exception("Bean '%s' exists" % bean_name)

                def create(*args, **kwargs):
                    with self._lock:
                        instance = self.get(bean_name)
                        if instance is None:
                            instance = func(*args, **kwargs)
                        self[bean_name] = instance
                        return instance

                return create  # TODO: Support lazy for function!

        return creator

    def bean(
        self,
        name: Optional[str] = None,
        ref_map: Dict[str, str] = {},
        lazy: bool = True,
    ):
        """
        Marks a class to be a bean and automatically injects its desired attributes on creation.

        Parameters:
        - name (str): the bean name (default: name of the class).
        - ref_map (dict): a mapping that specifies the reference name of each attribute.
        - lazy (bool): to specify whether or not to create the bean lazily (default: True).
        """

        def injectable_bean(cls_or_func: Union[type, Callable]):
            if isinstance(cls_or_func, type):
                cls_or_func = self.singleton(name=name, lazy=lazy)(
                    self.inject(ref_map=ref_map)(cls=cls_or_func)
                )
            else:
                cls_or_func = self.singleton(name=name, lazy=lazy)(
                    cls_or_func=cls_or_func
                )
            if not lazy:
                cls_or_func()  # TODO: build dependency tree and pass desired beans to bean function
            return cls_or_func

        return injectable_bean

    def __call__(
        self,
        name: Optional[str] = None,
        ref_map: Dict[str, str] = {},
        lazy: bool = True,
    ):
        return self.bean(name=name, ref_map=ref_map, lazy=lazy)


default = Container()
"""Default IoC container, can be used as a decorator to mark a class/function as a bean."""
