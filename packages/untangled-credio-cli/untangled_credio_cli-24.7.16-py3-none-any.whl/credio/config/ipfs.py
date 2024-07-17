import os
from typing import Optional
import ipfshttpclient
import ipfshttpclient.requests_wrapper

from credio.config.value import DEFAULT_IPFS_GATEWAY
from credio.config.store import default as store
from credio.util.type import lazyclass


@lazyclass
class IPFSClient:
    _client: ipfshttpclient.Client

    def __init__(self):
        self._client = ipfshttpclient.Client(
            addr=(store.get("IPFS_GATEWAY") or DEFAULT_IPFS_GATEWAY),
            session=True,
        )

    def add(self, path: Optional[str]) -> Optional[str]:
        if path is None:
            return
        if os.path.isdir(path):
            return self._client.add(path, pin=True, recursive=True)[-1]["Hash"]  # type: ignore
        return self._client.add(path, pin=True)["Hash"]  # type: ignore

    def cat(self, content_id: str) -> bytes:
        return self._client.cat(content_id)


client = IPFSClient()
