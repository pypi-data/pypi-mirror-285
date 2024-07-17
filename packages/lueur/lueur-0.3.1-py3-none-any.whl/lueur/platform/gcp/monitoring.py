# mypy: disable-error-code="attr-defined,operator,union-attr"
import asyncio
from typing import Any

import msgspec
from google.oauth2._service_account_async import Credentials

from lueur.links import add_link
from lueur.make_id import make_id
from lueur.models import Discovery, GCPMeta, Link, Resource
from lueur.platform.gcp.client import AuthorizedSession, Client
from lueur.rules import iter_resource

__all__ = ["explore_monitoring"]


async def explore_monitoring(
    project: str, creds: Credentials | None = None
) -> list[Resource]:
    resources = []

    async with Client("https://monitoring.googleapis.com", creds) as c:
        services = await explore_services(c, project)
        resources.extend(services)

        tasks: list[asyncio.Task] = []

        async with asyncio.TaskGroup() as tg:
            tasks.append(tg.create_task(explore_alert_policies(c, project)))
            tasks.append(tg.create_task(explore_groups(c, project)))
            tasks.append(
                tg.create_task(explore_notification_channels(c, project))
            )

            # uncomment once API is publicly available
            # tasks.append(tg.create_task(explore_incidents(c, project)))

            for svc in services:
                tasks.append(
                    tg.create_task(explore_slos(c, project, svc.meta.name))
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
async def explore_services(
    c: AuthorizedSession, project: str
) -> list[Resource]:
    response = await c.get(f"/v3/projects/{project}/services")

    services = msgspec.json.decode(response.content)

    results = []
    for svc in services["services"]:
        name = svc["name"]
        display = svc["displayName"]
        results.append(
            Resource(
                id=make_id(name),
                meta=GCPMeta(
                    name=name, display=display, kind="service", project=project
                ),
                struct=svc,
            )
        )

    return results


async def explore_slos(
    c: AuthorizedSession, project: str, service_name: str
) -> list[Resource]:
    response = await c.get(
        f"/v3/{service_name}/serviceLevelObjectives",
        params={"view": "EXPLICIT"},
    )

    slos = msgspec.json.decode(response.content)

    if not slos:
        return []

    results = []
    for slo in slos["serviceLevelObjectives"]:
        name = slo["name"]
        display = slo["displayName"]
        results.append(
            Resource(
                id=make_id(slo["name"]),
                meta=GCPMeta(
                    name=name, display=display, kind="slo", project=project
                ),
                struct=slo,
            )
        )

    return results


async def explore_alert_policies(
    c: AuthorizedSession, project: str
) -> list[Resource]:
    response = await c.get(f"/v3/projects/{project}/alertPolicies")

    policies = msgspec.json.decode(response.content)

    results = []
    for nc in policies["alertPolicies"]:
        name = nc["name"]
        display = nc["displayName"]
        results.append(
            Resource(
                id=make_id(name),
                meta=GCPMeta(
                    name=name,
                    display=display,
                    kind="alert-policy",
                    project=project,
                ),
                struct=nc,
            )
        )

    return results


async def explore_notification_channels(
    c: AuthorizedSession, project: str
) -> list[Resource]:
    response = await c.get(f"/v3/projects/{project}/notificationChannels")

    channels = msgspec.json.decode(response.content)

    results = []
    for nc in channels["notificationChannels"]:
        name = nc["name"]
        display = nc["displayName"]
        results.append(
            Resource(
                id=make_id(name),
                meta=GCPMeta(
                    name=name,
                    display=display,
                    kind="notification-channel",
                    project=project,
                ),
                struct=nc,
            )
        )

    return results


async def explore_groups(c: AuthorizedSession, project: str) -> list[Resource]:
    response = await c.get(f"/v3/projects/{project}/groups")

    groups = msgspec.json.decode(response.content)

    results = []
    for g in groups.get("group", []):
        name = g["name"]
        display = g["displayName"]
        results.append(
            Resource(
                id=make_id(name),
                meta=GCPMeta(
                    name=name,
                    display=display,
                    kind="group",
                    project=project,
                ),
                struct=g,
            )
        )

    return results


async def explore_incidents(
    c: AuthorizedSession, project: str
) -> list[Resource]:
    response = await c.get(f"/v3/projects/{project}/incidents")

    incidents = msgspec.json.decode(response.content)

    results = []
    for g in incidents.get("incidents", []):
        name = g["name"]
        display = g["name"]
        results.append(
            Resource(
                id=make_id(name),
                meta=GCPMeta(
                    name=name,
                    display=display,
                    kind="incident",
                    project=project,
                ),
                struct=g,
            )
        )

    return results


def expand_links(d: Discovery, serialized: dict[str, Any]) -> None:
    for s in iter_resource(
        serialized, "$.resources[?@.meta.kind=='service'].meta.name"
    ):
        r_id = s.parent.parent.obj["id"]  # type: ignore
        name = s.value
        p = f"$.resources[?@.meta.kind=='slo' && match(@.meta.name, '{name}/serviceLevelObjectives/.*')]"  # noqa E501
        for slo in iter_resource(serialized, p):
            add_link(
                d,
                r_id,
                Link(
                    direction="out",
                    kind="slo",
                    path=slo.path,
                    pointer=str(slo.pointer()),
                ),
            )

    for slo in iter_resource(
        serialized,
        "$.resources[?@.meta.kind=='slo'].meta.name",
    ):
        r_id = slo.parent.parent.obj["id"]  # type: ignore
        segments = slo.value.split("/")
        name = "/".join(segments[:-2])  # service name

        p = f"$.resources[?@.meta.kind=='service' && @.meta.name=='{name}']"
        for svc in iter_resource(serialized, p):
            add_link(
                d,
                r_id,
                Link(
                    direction="out",
                    kind="service",
                    path=svc.path,
                    pointer=str(svc.pointer()),
                ),
            )

    for alertnc in iter_resource(
        serialized,
        "$.resources[?@.meta.kind=='alert-policy'].struct.notificationChannels.*",  # noqa E501
    ):
        r_id = alertnc.parent.parent.parent.obj["id"]  # type: ignore
        name = alertnc.value
        p = f"$.resources[?@.meta.kind=='notification-channel' && @.meta.name=='{name}']"  # noqa E501
        for nc in iter_resource(serialized, p):
            add_link(
                d,
                r_id,
                Link(
                    direction="out",
                    kind="notification-channel",
                    path=nc.path,
                    pointer=str(nc.pointer()),
                ),
            )

    slos = {}
    for slo in iter_resource(
        serialized, "$.resources[?@.meta.kind=='slo'].meta.name"
    ):
        r_id = slo.parent.parent.obj["id"]  # type: ignore
        slos[slo.value] = r_id

    for condition_filter in iter_resource(
        serialized,
        "$.resources[?@.meta.kind=='alert-policy'].struct.conditions.*.conditionThreshold.filter",  # noqa E501
    ):
        cf = condition_filter.value
        for slo in slos:  # type: ignore
            if slo in cf:
                add_link(
                    d,
                    slos[slo],
                    Link(
                        direction="out",
                        kind="alert-policy",
                        path=condition_filter.path,
                        pointer=str(condition_filter.pointer()),
                    ),
                )
                break

    for s in iter_resource(
        serialized,
        "$.resources[?@.meta.kind=='service' && @.struct.basicService.serviceType=='CLOUD_RUN'].struct.basicService.serviceLabels.service_name",  # noqa E501
    ):
        r_id = s.parent.parent.parent.parent.obj["id"]  # type: ignore
        name = s.value
        p = f"$.resources[?@.meta.kind=='global-backend-service' && @.meta.name=='{name}']"  # noqa E501
        for slo in iter_resource(serialized, p):
            add_link(
                d,
                r_id,
                Link(
                    direction="out",
                    kind="global-backend-service",
                    path=slo.path,
                    pointer=str(slo.pointer()),
                ),
            )
