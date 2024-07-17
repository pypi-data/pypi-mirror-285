import os
from typing import Optional

from credio.config.value import DEFAULT_STORAGE_PATH
from credio.config.store import default as store
from credio.util.type import lazy


class File:
    storage_path: str = DEFAULT_STORAGE_PATH

    @staticmethod
    def _mkdir(path: str):
        if not os.path.exists(path):
            os.makedirs(path)
        if not os.path.isdir(path):
            raise Exception("Path '%s' is not a directory" % path)

    def __init__(self):
        storage_path = store.get("STORAGE_PATH")
        if storage_path is not None:
            File._mkdir(storage_path)
            self.storage_path = storage_path

    def path(self, bucket: str, *folders: str, name: Optional[str] = None) -> str:
        folder_path = os.path.join(self.storage_path, bucket, *folders)
        File._mkdir(folder_path)
        return os.path.join(folder_path, name) if name else folder_path

    def store(
        self,
        bucket: str,
        *folders: str,
        name: Optional[str] = None,
        data: bytes = bytes(0)
    ) -> str:
        file_path = self.path(bucket, *folders, name=name)
        with open(file_path, "+wb") as file:
            data = data if isinstance(data, bytes) else str(data).encode()
            file.write(data)
        return file_path

    def remove(self, bucket: str, *folders: str, name: Optional[str] = None) -> str:
        path = self.path(bucket, *folders, name=name)
        if os.path.isdir(path):
            os.rmdir(path)
        else:
            os.remove(path)
        return path

    def retrieve(self, bucket: str, *folders: str, name: str) -> bytes:
        file_path = os.path.join(self.storage_path, bucket, *folders, name)
        with open(file_path, "+rb") as file:
            return file.read()


default = lazy(File)
"""Simple storage."""
