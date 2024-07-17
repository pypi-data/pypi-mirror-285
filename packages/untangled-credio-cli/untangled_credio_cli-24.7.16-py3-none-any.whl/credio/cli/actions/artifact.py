import asyncio
import json
from multiprocessing.pool import ThreadPool
import os
import re
from typing import List, Optional
from uuid import uuid4
import aiohttp
import requests
import rich
import typer

from credio.cli.actions.config import DEFAULT_IPFS_SERVER_HOST, DEFAULT_IPFS_SERVER_PORT
from credio.config import storage, store
from credio.cli.actions.gateway import API
from credio.util.type import Object


action = typer.Typer()


def get_file_name(res: aiohttp.ClientResponse):
    return [
        *re.findall("filename=(.+)", res.headers[aiohttp.hdrs.CONTENT_DISPOSITION]),
        None,
    ][0]


class FileObj(Object):
    file_name: str
    content_id: str
    folder: str


class Artifact(API):
    @property
    def ipfs_server_host(self):
        return store.get("IPFS_SERVER_HOST", str) or DEFAULT_IPFS_SERVER_HOST

    @property
    def ipfs_server_port(self):
        return store.get("IPFS_SERVER_PORT", str) or DEFAULT_IPFS_SERVER_PORT

    async def upload(
        self, *files: str, type: Optional[str] = None, challenge: Optional[int] = None
    ):
        with aiohttp.MultipartWriter("form-data") as writer:
            for file in files:
                if not os.path.isfile(file):
                    raise Exception(
                        "Not a file path: %s" % file
                    )  # TODO: Support uploading a directory
                part = writer.append(open(file, "rb"))
                part.set_content_disposition(
                    "form-data", name=str(uuid4()), filename=os.path.basename(file)
                )
            if type is not None:
                part = writer.append(type, {"Content-Type": "text/plain"})
                part.set_content_disposition("form-data", name="type")
            if challenge is not None:
                part = writer.append(str(challenge), {"Content-Type": "text/plain"})
                part.set_content_disposition("form-data", name="challenge")
            async with self.auth_session as session:
                async with session.post("/storage/upload", data=writer) as res:
                    r = Object(await res.json())
                    if not res.ok:
                        raise Exception(r.select("message"))
                    return r

    async def metadata(self, artifact_id: str):
        async with self.session as session:
            async with session.get("/storage/metadata/%s" % artifact_id) as res:
                r = Object(await res.json())
                if not res.ok:
                    raise Exception(r.select("message"))
                files: List[FileObj] = []
                for i in r:
                    content = Object(r[i])
                    content_id = content.select("content_id", type=str)
                    file_name = content.select("file_name", type=str)
                    if content_id is not None:
                        files.append(
                            FileObj(
                                {
                                    "file_name": file_name,
                                    "content_id": content_id,
                                }
                            )
                        )
                return files

    def download(self, file: FileObj):
        if file.file_name in ["", None]:
            raise NotImplementedError(
                "Please open this link to download the artifact: http://%s:%s/ipfs/%s"
                % (self.ipfs_server_host, self.ipfs_server_port, file.content_id)
            )
        res = requests.get(
            "%s/storage/download/%s" % (self.base_url, file.content_id), stream=True
        )
        if not res.ok:
            raise Exception("Failed when downloading content '%s'" % file.content_id)
        storage._mkdir(file.folder)
        file_path = os.path.join(file.folder, file.file_name)
        with open(file_path, "wb") as f:
            for data in res:
                rich.print(
                    "[bright_black]Downloading %s...[/bright_black]" % file.file_name
                )
                f.write(data)
        rich.print("[bright_black]%s downloaded.[/bright_black]" % file.file_name)
        return file.file_name

    def download_artifact(self, folder: str, artifact_id: str):
        files = ThreadPool(5).imap_unordered(
            self.download,
            [
                FileObj(
                    {
                        **file,
                        "folder": folder,
                    }
                )
                for file in asyncio.run(self.metadata(artifact_id=artifact_id))
            ],
        )
        return [file for file in files]


@action.command(name="info", help="Show information of a Credio artifact.")
def info(artifact_id: str):
    res = asyncio.run(Artifact().metadata(artifact_id))
    rich.print_json(json=json.dumps(res))


@action.command(
    name="upload", help="Upload specific files as a Credio artifact (stored in IPFS)."
)
def upload(files: List[str]):
    res = asyncio.run(Artifact().upload(*files))
    rich.print("[green]Uploaded.[/green]")
    rich.print_json(json=json.dumps(res))


@action.command(
    name="download", help="Download a specific Credio artifact (from IPFS)."
)
def download(artifact_id: str):
    cwd = os.getcwd()
    folder = str(typer.prompt("Download to", default=cwd, show_default=True))
    files = Artifact().download_artifact(folder, artifact_id)
    total = len(files)
    rich.print(
        "[green]%s[/green] file%s downloaded to %s."
        % (total, "s" if total > 1 else "", folder)
    )
    rich.print_json(json=json.dumps(files))
