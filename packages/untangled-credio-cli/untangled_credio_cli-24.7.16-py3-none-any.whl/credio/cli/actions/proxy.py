import asyncio
import select
import socket
import threading
import traceback
from typing import Optional
import paramiko
import rich
import rich.progress

from credio.cli.actions.config import (
    DEFAULT_SSH_CLIENT_PRIVATE_KEY_PATH,
    DEFAULT_SSH_SERVER_HOST,
    DEFAULT_SSH_SERVER_PORT,
)
from credio.cli.actions.gateway import API
from credio.config import store
from credio.util.type import Object


def _pipe(chan: paramiko.Channel, host: str, port: int):
    sock = socket.socket()
    sock.connect((host, port))
    while True:
        r, _, _ = select.select([sock, chan], [], [])
        if sock in r:
            data = sock.recv(1024)
            if len(data) == 0:
                break
            chan.send(data)
        if chan in r:
            data = chan.recv(1024)
            if len(data) == 0:
                break
            sock.send(data)
    chan.close()
    sock.close()


def _forward(
    remote_host: str,
    remote_port: int,
    local_host: str,
    local_port: int,
    transport: paramiko.Transport,
):
    transport.request_port_forward("", remote_port)
    rich.print("Proxying from %s to %s:%s..." % (remote_host, local_host, local_port))
    rich.print("[bright_black]Press Ctrl + C to stop proxying.[/bright_black]")
    while True:
        if not transport.active:
            break
        chan = transport.accept(1000)
        if chan is None:
            continue
        thread = threading.Thread(target=_pipe, args=(chan, local_host, local_port))
        thread.setDaemon(True)
        thread.start()
    rich.print("[red]Proxy from %s stopped.[/red]" % remote_host)


class Endpoint(API):
    @property
    def ssh_host(self):
        return store.get("SSH_SERVER_HOST", str) or DEFAULT_SSH_SERVER_HOST

    @property
    def ssh_port(self):
        return int(store.get("SSH_SERVER_PORT", str) or DEFAULT_SSH_SERVER_PORT)

    @property
    def ssh_private_key_path(self):
        return (
            store.get("SSH_CLIENT_PRIVATE_KEY_PATH", str)
            or DEFAULT_SSH_CLIENT_PRIVATE_KEY_PATH
        )

    async def list_all(self):
        async with self.auth_session as session:
            async with session.get("/usage/endpoints") as res:
                r = Object(await res.json())
                if not res.ok:
                    raise Exception(r.select("message"))
                return r

    async def register(self, model_id: int, public_key_path: str):
        authorized_key = None
        with open(public_key_path, "rb") as file:
            authorized_key = file.read().decode()
        async with self.auth_session as session:
            async with session.post(
                "/usage/register",
                json={"model_id": model_id, "authorized_key": authorized_key},
            ) as res:
                r = Object(await res.json())
                if not res.ok:
                    raise Exception(r.select("message"))
                return "[green]Endpoint registered.[/green]"

    async def get_assigned_port(self, model_id: int):
        async with self.auth_session as session:
            async with session.get("/usage/endpoint/%s" % model_id) as res:
                r = Object(await res.json())
                if not res.ok:
                    raise Exception(r.select("message"))
                assigned_port = r.select("endpoint.assigned_port", int)
                if assigned_port is None:
                    raise Exception(
                        "No assigned port available for model %s" % model_id
                    )
                return assigned_port

    def start_proxy(
        self,
        username: str,
        remote_port: int,
        local_port: int = 8080,
        local_host: str = "localhost",
        private_key_path: Optional[str] = None,
    ):
        if private_key_path is None:
            private_key_path = self.ssh_private_key_path
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        rich.print("Connecting to %s..." % self.ssh_host)
        client.connect(
            username=username,
            hostname=self.ssh_host,
            port=self.ssh_port,
            pkey=paramiko.PKey.from_path(private_key_path),
        )
        rich.print("Connected.")
        transport = client.get_transport()
        if transport is None:
            raise Exception("No transport available for paramiko SSHClient")
        _forward(
            remote_host=self.ssh_host,
            remote_port=remote_port,
            local_host=local_host,
            local_port=local_port,
            transport=transport,
        )


def start_proxy(
    model_id: int,
    remote_port: int,
    local_port: int,
    private_key_path: str,
):
    def start():
        Endpoint().start_proxy(
            username=str(model_id),
            remote_port=remote_port,
            local_port=local_port,
            private_key_path=private_key_path,
        )

    debug = store.get("DEBUG")
    try:
        start()
    except:
        rich.print("[red]Connection failed.[/red]")
        if debug:
            print(traceback.format_exc())
