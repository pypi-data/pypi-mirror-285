import shutil
import subprocess
import click
import rich
from rich.traceback import install
import typer

from credio.cli import actions
from credio.cli.actions.config import DEFAULT_STORAGE_PATH
from credio.config import store


install(suppress=[click])

app = typer.Typer(
    rich_markup_mode="markdown",
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
    help="A command-line tool to build everything.",
)
app.add_typer(
    actions.config, name="config", help="All command-line tool configurations."
)
app.add_typer(
    actions.zkml,
    name="model",
    help="Use ZKML functionalities (compile/serve/register).",
)
app.add_typer(
    actions.auth,
    name="me",
    help="You on Credio platform (normally show your registered email).",
)
app.add_typer(
    actions.artifact,
    name="artifact",
    help="Interact with artifacts (datasets, model submission, etc.)",
)
app.add_typer(
    actions.competition,
    name="competition",
    help="Credio ML competitions with valuable rewards.",
)


@app.command(
    name="version", help="Show current version of Credio CLI (installed via pip)."
)
def version():
    if shutil.which("pip") is None:
        rich.print("[yellow]Unknown.[/yellow]")
        return
    subprocess.run(["pip", "show", "untangled-credio-cli"])


def main():
    store.load_json({"STORAGE_PATH": DEFAULT_STORAGE_PATH})
    debug = store.get("DEBUG")
    try:
        if debug:
            rich.print("[yellow]DEBUG enabled.[/yellow]")
        app()
    except Exception as ex:
        if debug:
            raise ex
        rich.print("[red]%s[/red]" % ex)
