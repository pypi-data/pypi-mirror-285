import json
import os
from typing import Optional, Type, TypeVar

from credio.util.log import log
from credio.util.type import Object


V = TypeVar("V")


class Store(dict):
    def __init__(self):
        pass

    def get(self, key: str, type: Type[V] = str) -> Optional[V]:
        if key in self.keys():
            return self[key]

    def load(self, *keys: str):
        for key in keys:
            self[key] = os.environ[key]
        return self

    def load_json(self, obj: dict):
        for key in obj:
            self[key] = str(obj[key])
        return self

    def load_all(self):
        self.load(*os.environ.keys())
        log(
            "Loaded %s configuration%s from environment variables"
            % (len(os.environ.keys()), "s" if len(os.environ.keys()) > 1 else "")
        )
        return self

    def load_file(self, path: Optional[str]):
        log("Loading configurations from file: %s" % path)
        if path is None or not os.path.isfile(path):
            raise Exception("Configuration file not found: %s" % path)
        with open(path, "rb") as file:
            json_obj = Object(json.loads(file.read().decode()))
            self.load_json(json_obj)
            log(
                "Loaded %s configuration%s from file: %s"
                % (len(json_obj.keys()), "s" if len(json_obj.keys()) > 1 else "", path)
            )
        return self


default = Store().load_all()
"""Default Configuration Store."""
