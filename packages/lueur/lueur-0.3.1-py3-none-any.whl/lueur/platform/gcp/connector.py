import asyncio

import msgspec
from google.oauth2._service_account_async import Credentials

from lueur.make_id import make_id
from lueur.models import GCPMeta, Resource
from lueur.platform.gcp.client import AuthorizedSession, Client

__all__ = ["explore_connector"]


async def explore_connector(
    project: str, location: str, creds: Credentials | None = None
) -> list[Resource]:
    resources = []

    async with Client("https://connectors.googleapis.com", creds) as c:
        providers = await explore_connector_providers(c, project, location)
        resources.extend(providers)

        connections = await explore_connections(c, project, location)
        resources.extend(connections)

        tasks: list[asyncio.Task] = []

        async with asyncio.TaskGroup() as tg:
            for p in providers:
                tasks.append(
                    tg.create_task(
                        explore_connectors(c, project, location, p.meta.name)
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
async def explore_connector_providers(
    c: AuthorizedSession, project: str, location: str
) -> list[Resource]:
    response = await c.get(
        f"/v1/projects/{project}/locations/{location}/providers"
    )

    providers = msgspec.json.decode(response.content)

    results = []
    for provider in providers.get("providers", []):
        name = provider["name"]
        display = provider["displayName"]

        results.append(
            Resource(
                id=make_id(provider["name"]),
                meta=GCPMeta(
                    name=name,
                    display=display,
                    kind="connector-provider",
                    project=project,
                    region=location,
                ),
                struct=provider,
            )
        )

    return results


async def explore_connectors(
    c: AuthorizedSession, project: str, location: str, name: str
) -> list[Resource]:
    response = await c.get(
        f"/v1/projects/{project}/locations/{location}/providers/{name}/connectors"
    )

    connectors = msgspec.json.decode(response.content)

    results = []
    for connector in connectors.get("connectors", []):
        name = connector["name"]
        display = connector["displayName"]

        results.append(
            Resource(
                id=make_id(connector["name"]),
                meta=GCPMeta(
                    name=name,
                    display=display,
                    kind="connector",
                    project=project,
                    region=location,
                ),
                struct=connector,
            )
        )

    return results


async def explore_connections(
    c: AuthorizedSession, project: str, location: str
) -> list[Resource]:
    response = await c.get(
        f"/v1/projects/{project}/locations/{location}/connections"
    )

    connections = msgspec.json.decode(response.content)

    results = []
    for connection in connections.get("connections", []):
        name = connection["name"]
        display = connection["name"]

        results.append(
            Resource(
                id=make_id(connection["name"]),
                meta=GCPMeta(
                    name=name,
                    display=display,
                    kind="connector-connection",
                    project=project,
                    region=location,
                ),
                struct=connection,
            )
        )

    return results
