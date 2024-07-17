import asyncio
from datetime import datetime
import json
from typing import List
from uuid import UUID

import rich
import typer
from credio.cli.actions.gateway import API
from credio.util.type import Object


action = typer.Typer()


class ChallengeObj(Object):
    id: int
    manifesto_id: UUID
    created_by: UUID
    started_at: datetime
    closed_at: datetime


class Competition(API):
    async def all(self):
        async with self.auth_session as session:
            async with session.get("/competition/all") as res:
                r = Object(await res.json())
                if not res.ok:
                    raise Exception(r.select("message"))
                challenges: List[ChallengeObj] = []
                for i in r:
                    challenges.append(ChallengeObj(Object(r[i])))
                return challenges


@action.command(name="list", help="List all available challenges.")
def all():
    all = asyncio.run(Competition().all())
    total = len(all)
    rich.print(
        "[green]%s[/green] challenge%s available." % (total, "s" if total > 1 else "")
    )
    rich.print_json(json=json.dumps(all))
