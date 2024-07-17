import json
import os
import rich
import typer

from credio.config import store
from credio.util.type import Object


DEFAULT_STORAGE_PATH = os.path.expanduser("~")
DEFAULT_CONFIG_FOLDER = ".credio"
DEFAULT_CREDENTIAL_FILE = "credentials"
DEFAULT_AUTH_TOKEN_KEY = "auth_token"
DEFAULT_GATEWAY_BASE_URL = "https://api.credio.network"
DEFAULT_IPFS_GATEWAY = "/dns/ipfs.credio.network/tcp/5001/http"
DEFAULT_SSH_SERVER_HOST = "ssh.credio.network"
DEFAULT_SSH_SERVER_PORT = 32222
DEFAULT_SSH_CLIENT_PRIVATE_KEY_PATH = os.path.join(
    os.path.expanduser("~"), ".ssh", "id_rsa"
)
DEFAULT_SSH_CLIENT_PUBLIC_KEY_PATH = os.path.join(
    os.path.expanduser("~"), ".ssh", "id_rsa.pub"
)
DEFAULT_IPFS_SERVER_HOST = "ipfs.credio.network"
DEFAULT_IPFS_SERVER_PORT = 8080


action = typer.Typer()


@action.command(name="show", help="Show this command-line tool configurations.")
def show():
    gateway_base_url = store.get("GATEWAY_BASE_URL") or DEFAULT_GATEWAY_BASE_URL
    ipfs_gateway = store.get("IPFS_GATEWAY") or DEFAULT_IPFS_GATEWAY
    ssh_server = "%s:%s" % (
        store.get("SSH_SERVER_HOST") or DEFAULT_SSH_SERVER_HOST,
        store.get("SSH_SERVER_PORT") or DEFAULT_SSH_SERVER_PORT,
    )
    storage_path = store.get("STORAGE_PATH") or DEFAULT_STORAGE_PATH
    credentials_path = os.path.join(
        storage_path, DEFAULT_CONFIG_FOLDER, DEFAULT_CREDENTIAL_FILE
    )
    rich.print_json(
        json=json.dumps(
            Object(
                {
                    "GATEWAY_BASE_URL": gateway_base_url,
                    "IPFS_GATEWAY": ipfs_gateway,
                    "SSH_SERVER": ssh_server,
                    "STORAGE_PATH": storage_path,
                    "CREDENTIALS_PATH": credentials_path,
                }
            )
        )
    )
