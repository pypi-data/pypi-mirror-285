import asyncio
import json
import rich
import typer

from credio.cli.actions.config import DEFAULT_AUTH_TOKEN_KEY
from credio.cli.actions.gateway import API
from credio.util.type import Object


action = typer.Typer()


class Account(Object):
    email: str
    password: str


def ask(confirm_password: bool = False, max_retries: int = 3):
    email = typer.prompt("Your email")
    password = typer.prompt("Password", hide_input=True)
    if confirm_password:
        for _ in range(max_retries):
            if password == typer.prompt("Confirm password", hide_input=True):
                break
            rich.print("[red]Password not match![/red]")
    return Account(
        {
            "email": email,
            "password": password,
        }
    )


class Auth(API):
    async def logout(self):
        API.store_auth_token("")

    async def register(self, email: str, password: str):
        async with self.session as session:
            async with session.post(
                "/account/register",
                json={
                    "email": email,
                    "password": password,
                },
            ) as res:
                r = Object(await res.json())
                if not res.ok:
                    raise Exception(r.select("message"))
                return "[green]Success.[/green]"

    async def authenticate(self, email: str, password: str):
        async with self.session as session:
            async with session.post(
                "/account/authenticate",
                json={
                    "email": email,
                    "password": password,
                },
            ) as res:
                r = Object(await res.json())
                if not res.ok:
                    raise Exception(r.select("message"))
                auth_token = r.select("token")
                API.store_auth_token(
                    json.dumps(
                        {f"{DEFAULT_AUTH_TOKEN_KEY}": auth_token}, separators=(",", ":")
                    )
                )
                return "[green]Success.[/green]"

    async def info(self):
        async with self.auth_session as session:
            async with session.get("/account") as res:
                r = Object(await res.json())
                if not res.ok:
                    raise Exception(r.select("message"))
                return r.select("email")


@action.command(name="register", help="Register a Credio account.")
def register():
    account = ask(confirm_password=True)
    rich.print(
        asyncio.run(Auth().register(email=account.email, password=account.password))
    )


@action.command(name="login", help="Log in to Credio platform.")
def login():
    account = ask()
    rich.print(
        asyncio.run(Auth().authenticate(email=account.email, password=account.password))
    )


@action.command(name="hello", help="Show your logged-in Credio account.")
def show():
    email = asyncio.run(Auth().info())
    rich.print("Hi, [green]%s[/green]!" % email)


@action.command(name="logout", help="No need to do that.")
def logout():
    confirm = typer.prompt("Sure? (yes/no)", default="no", show_default=True)
    if str(confirm).lower() in ["y", "yes"]:
        asyncio.run(Auth().logout())
        rich.print("Bye!")
