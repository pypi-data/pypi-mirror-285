import json
import aiohttp
from aiohttp import ClientSession

from credio.config import storage, store
from credio.util.type import Object
from credio.cli.actions.config import (
    DEFAULT_AUTH_TOKEN_KEY,
    DEFAULT_CONFIG_FOLDER,
    DEFAULT_CREDENTIAL_FILE,
    DEFAULT_GATEWAY_BASE_URL,
)


class API:
    @staticmethod
    def get_auth_token():
        try:
            credentials = Object(
                json.loads(
                    storage.retrieve(
                        DEFAULT_CONFIG_FOLDER, name=DEFAULT_CREDENTIAL_FILE
                    )
                )
            )
            return credentials.select(DEFAULT_AUTH_TOKEN_KEY, str)
        except:
            raise Exception("Please log in to continue!")

    @staticmethod
    def store_auth_token(value: str):
        return storage.store(
            DEFAULT_CONFIG_FOLDER, name=DEFAULT_CREDENTIAL_FILE, data=value.encode()
        )

    @property
    def base_url(self):
        return store.get("GATEWAY_BASE_URL") or DEFAULT_GATEWAY_BASE_URL

    @property
    def session(self):
        return ClientSession(base_url=self.base_url)

    @property
    def auth_session(self):
        auth_token = API.get_auth_token()
        return ClientSession(
            base_url=self.base_url,
            headers={f"{aiohttp.hdrs.AUTHORIZATION}": "Bearer %s" % auth_token},
        )
