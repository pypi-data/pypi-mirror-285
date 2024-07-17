# mypy: disable-error-code="index,union-attr"
import asyncio
from typing import Any

import msgspec
from google.oauth2._service_account_async import Credentials

from lueur.links import add_link
from lueur.make_id import make_id
from lueur.models import Discovery, Link, Meta, Resource
from lueur.platform.gcp.client import AuthorizedSession, Client
from lueur.rules import iter_resource

__all__ = ["explore_sql", "expand_links"]


async def explore_sql(
    project: str, creds: Credentials | None = None
) -> list[Resource]:
    resources = []

    async with Client("https://sqladmin.googleapis.com", creds) as c:
        instances = await explore_instances(c, project)
        resources.extend(instances)

        tasks: list[asyncio.Task] = []

        async with asyncio.TaskGroup() as tg:
            for inst in instances:
                tasks.append(
                    tg.create_task(explore_users(c, project, inst.meta.name))
                )
                tasks.append(
                    tg.create_task(
                        explore_databases(c, project, inst.meta.name)
                    )
                )

        for task in tasks:
            result = task.result()
            if result is None:
                continue
            resources.extend(result)

    return resources


###############################################################################
# Private functions
###############################################################################
async def explore_instances(
    c: AuthorizedSession, project: str
) -> list[Resource]:
    response = await c.get(f"/v1/projects/{project}/instances")

    instances = msgspec.json.decode(response.content)

    results = []
    for inst in instances["items"]:
        results.append(
            Resource(
                id=make_id(inst["selfLink"]),
                meta=Meta(
                    name=inst["name"], display=inst["name"], kind="instance"
                ),
                struct=inst,
            )
        )

    return results


async def explore_users(
    c: AuthorizedSession, project: str, instance: str
) -> list[Resource]:
    response = await c.get(f"/v1/projects/{project}/instances/{instance}/users")

    users = msgspec.json.decode(response.content)

    results = []
    for user in users["items"]:
        results.append(
            Resource(
                id=make_id(f"{user['instance']}-{user['name']}"),
                meta=Meta(name=user["name"], display=user["name"], kind="user"),
                struct=user,
            )
        )

    return results


async def explore_databases(
    c: AuthorizedSession, project: str, instance: str
) -> list[Resource]:
    response = await c.get(
        f"/v1/projects/{project}/instances/{instance}/databases"
    )

    databases = msgspec.json.decode(response.content)

    results = []
    for database in databases["items"]:
        results.append(
            Resource(
                id=make_id(f"{database['instance']}-{database['name']}"),
                meta=Meta(
                    name=database["name"],
                    display=database["name"],
                    kind="database",
                ),
                struct=database,
            )
        )

    return results


def expand_links(d: Discovery, serialized: dict[str, Any]) -> None:
    for i in iter_resource(
        serialized, "$.resources[?@.meta.kind=='instance'].meta.name"
    ):
        r_id = i.parent.parent.obj["id"]
        name = i.value

        p = f"$.resources[?@.meta.kind=='user' && @.struct.instance=='{name}']"
        for user in iter_resource(serialized, p):
            add_link(
                d,
                r_id,
                Link(
                    direction="out",
                    kind="user",
                    path=user.path,
                    pointer=str(user.pointer()),
                ),
            )

        p = f"$.resources[?@.meta.kind=='database' && @.struct.instance=='{name}']"  # noqa E501
        for db in iter_resource(serialized, p):
            add_link(
                d,
                r_id,
                Link(
                    direction="out",
                    kind="database",
                    path=db.path,
                    pointer=str(db.pointer()),
                ),
            )

    for s in iter_resource(
        serialized,
        "$.resources[?@.meta.kind=='instance'].struct.settings.ipConfiguration.privateNetwork",  # noqa E501
    ):
        r_id = s.parent.parent.parent.parent.obj["id"]  # type: ignore
        network = s.value.rsplit("/", 1)[-1]  # type: ignore
        p = f"$.resources[?@.meta.kind=='network' && @.meta.name=='{network}']"
        for svc in iter_resource(serialized, p):
            add_link(
                d,
                r_id,
                Link(
                    direction="out",
                    kind="network",
                    path=svc.path,
                    pointer=str(svc.pointer()),
                ),
            )
