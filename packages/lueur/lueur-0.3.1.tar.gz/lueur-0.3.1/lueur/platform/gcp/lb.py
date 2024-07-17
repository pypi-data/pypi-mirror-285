# mypy: disable-error-code="arg-type,attr-defined,index,union-attr"
import asyncio
from typing import Any, cast

import msgspec
from google.oauth2._service_account_async import Credentials

from lueur.links import add_link
from lueur.make_id import make_id
from lueur.models import Discovery, GCPMeta, Link, Resource
from lueur.platform.gcp.client import AuthorizedSession, Client
from lueur.platform.gcp.zone import list_project_zones
from lueur.rules import iter_resource

__all__ = ["explore_lb"]


async def explore_lb(
    project: str, location: str | None = None, creds: Credentials | None = None
) -> list[Resource]:
    resources = []

    async with Client("https://compute.googleapis.com", creds) as c:
        tasks: list[asyncio.Task] = []

        async with asyncio.TaskGroup() as tg:
            if not location:
                tasks.append(tg.create_task(explore_global_urlmaps(c, project)))
                tasks.append(
                    tg.create_task(explore_global_backend_services(c, project))
                )
                tasks.append(
                    tg.create_task(explore_global_backend_groups(c, project))
                )
                tasks.append(
                    tg.create_task(explore_zonal_backend_groups(c, project))
                )
            else:
                tasks.append(
                    tg.create_task(
                        explore_regional_urlmaps(c, project, location)
                    )
                )
                tasks.append(
                    tg.create_task(
                        explore_regional_backend_services(c, project, location)
                    )
                )
                tasks.append(
                    tg.create_task(
                        explore_regional_backend_groups(c, project, location)
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
async def explore_global_urlmaps(
    c: AuthorizedSession, project: str
) -> list[Resource]:
    response = await c.get(
        f"/compute/v1/projects/{project}/global/urlMaps",
        params={"returnPartialSuccess": True},
    )

    urlmaps = msgspec.json.decode(response.content)

    results = []
    for urlmap in urlmaps.get("items", []):
        results.append(
            Resource(
                id=make_id(urlmap["id"]),
                meta=GCPMeta(
                    name=urlmap["name"],
                    display=urlmap["name"],
                    kind="global-urlmap",
                    project=project,
                ),
                struct=urlmap,
            )
        )

    return results


async def explore_global_backend_services(
    c: AuthorizedSession, project: str
) -> list[Resource]:
    response = await c.get(
        f"/compute/v1/projects/{project}/global/backendServices",
        params={"returnPartialSuccess": True},
    )

    backend_services = msgspec.json.decode(response.content)

    results = []
    for backend_service in backend_services.get("items", []):
        name = backend_service["name"]
        display = name

        results.append(
            Resource(
                id=make_id(backend_service["id"]),
                meta=GCPMeta(
                    name=name,
                    display=display,
                    kind="global-backend-service",
                    project=project,
                ),
                struct=backend_service,
            )
        )

    return results


async def explore_global_backend_groups(
    c: AuthorizedSession, project: str
) -> list[Resource]:
    response = await c.get(
        f"/compute/v1/projects/{project}/global/networkEndpointGroups",
        params={"returnPartialSuccess": True},
    )

    backend_groups = msgspec.json.decode(response.content)

    results = []
    for backend_group in backend_groups.get("items", []):
        name = backend_group["name"]
        display = name
        region = backend_group.get("region")
        zone = backend_group.get("zone")
        if zone:
            _, zone = zone.rsplit("/", 1)

        results.append(
            Resource(
                id=make_id(backend_group["id"]),
                meta=GCPMeta(
                    name=name,
                    display=display,
                    kind="global-neg",
                    project=project,
                    region=region,
                    zone=zone,
                ),
                struct=backend_group,
            )
        )

    return results


async def explore_regional_urlmaps(
    c: AuthorizedSession, project: str, location: str
) -> list[Resource]:
    response = await c.get(
        f"/compute/v1/projects/{project}/regions/{location}/urlMaps",
        params={"returnPartialSuccess": True},
    )

    urlmaps = msgspec.json.decode(response.content)

    results = []
    for urlmap in urlmaps.get("items", []):
        results.append(
            Resource(
                id=make_id(urlmap["id"]),
                meta=GCPMeta(
                    name=urlmap["name"],
                    display=urlmap["name"],
                    kind="regional-urlmap",
                    project=project,
                    region=location,
                ),
                struct=urlmap,
            )
        )

    return results


async def explore_regional_backend_services(
    c: AuthorizedSession, project: str, location: str
) -> list[Resource]:
    response = await c.get(
        f"/compute/v1/projects/{project}/regions/{location}/backendServices",
        params={"returnPartialSuccess": True},
    )

    backend_services = msgspec.json.decode(response.content)

    results = []
    for backend_service in backend_services.get("items", []):
        name = backend_service["name"]
        region = backend_service["region"]
        display = name

        results.append(
            Resource(
                id=make_id(backend_service["id"]),
                meta=GCPMeta(
                    name=name,
                    display=display,
                    kind="regional-backend-service",
                    project=project,
                    region=region,
                ),
                struct=backend_service,
            )
        )

    return results


async def explore_regional_backend_groups(
    c: AuthorizedSession, project: str, location: str
) -> list[Resource]:
    response = await c.get(
        f"/compute/v1/projects/{project}/regions/{location}/networkEndpointGroups",
        params={"returnPartialSuccess": True},
    )

    backend_groups = msgspec.json.decode(response.content)

    results = []

    for backend_group in backend_groups.get("items", []):
        name = backend_group["name"]
        display = name
        zone = backend_group.get("zone")
        if zone:
            _, zone = zone.rsplit("/", 1)

        results.append(
            Resource(
                id=make_id(backend_group["id"]),
                meta=GCPMeta(
                    name=name,
                    display=display,
                    kind="regional-neg",
                    project=project,
                    region=location,
                    zone=zone,
                ),
                struct=backend_group,
            )
        )

    return results


async def explore_zonal_backend_groups(
    c: AuthorizedSession, project: str
) -> list[Resource]:
    zones = await list_project_zones(project)

    results = []
    tasks: list[asyncio.Task] = []

    async with asyncio.TaskGroup() as tg:
        for zone in zones:
            tasks.append(
                tg.create_task(
                    c.get(
                        f"/compute/v1/projects/{project}/zones/{zone}/networkEndpointGroups",
                        params={"returnPartialSuccess": True},
                    )
                )
            )

    for task in tasks:
        response = task.result()
        if response is None:
            response

        backend_groups = msgspec.json.decode(response.content)

        for backend_group in backend_groups.get("items", []):
            name = backend_group["name"]
            display = name
            region = backend_group.get("region")
            if region:
                _, region = region.rsplit("/", 1)

            results.append(
                Resource(
                    id=make_id(backend_group["id"]),
                    meta=GCPMeta(
                        name=name,
                        display=display,
                        kind="zonal-neg",
                        project=project,
                        region=region,
                        zone=zone,
                    ),
                    struct=backend_group,
                )
            )

    return results


def expand_links(d: Discovery, serialized: dict[str, Any]) -> None:
    for backend_service in iter_resource(
        serialized,
        "$.resources[?@.meta.kind=='global-backend-service'].meta.name",
    ):
        struct = backend_service.parent.parent.obj["struct"]  # type: ignore
        for used_by in struct.get("usedBy", []):
            ref = used_by.get("reference")
            p = f"$.resources[?@.meta.kind=='global-urlmap' && @.struct.selfLink=='{ref}'].id"  # noqa E501
            for urlmap_id in iter_resource(serialized, p):
                add_link(
                    d,
                    urlmap_id.value,
                    Link(
                        direction="out",
                        kind="global-backend-service",
                        path=backend_service.parent.parent.path,  # type: ignore
                        pointer=str(backend_service.parent.parent.pointer()),  # type: ignore
                    ),
                )

    for s in iter_resource(
        serialized, "$.resources[?@.meta.kind=='global-neg'].struct.subnetwork"
    ):
        r_id = s.parent.parent.obj["id"]  # type: ignore
        subnet = s.value
        p = f"$.resources[?@.meta.kind=='subnet' && @.meta.self_link=='{subnet}']"  # noqa E501
        for subnet in iter_resource(serialized, p):
            add_link(
                d,
                r_id,
                Link(
                    direction="out",
                    kind="subnet",
                    path=subnet.path,
                    pointer=str(subnet.pointer()),
                ),
            )

    for s in iter_resource(
        serialized, "$.resources[?@.meta.kind=='zonal-neg'].struct.network"
    ):
        r_id = s.parent.parent.obj["id"]  # type: ignore
        network = s.value
        p = f"$.resources[?@.meta.kind=='network' && @.meta.self_link=='{network}']"  # noqa E501
        for subnet in iter_resource(serialized, p):
            add_link(
                d,
                r_id,
                Link(
                    direction="out",
                    kind="network",
                    path=subnet.path,
                    pointer=str(subnet.pointer()),
                ),
            )

    for s in iter_resource(
        serialized, "$.resources[?@.meta.kind=='zonal-neg'].struct.subnetwork"
    ):
        r_id = s.parent.parent.obj["id"]  # type: ignore
        subnet = s.value
        p = f"$.resources[?@.meta.kind=='subnet' && @.meta.self_link=='{subnet}']"  # noqa E501
        for subnet in iter_resource(serialized, p):
            add_link(
                d,
                r_id,
                Link(
                    direction="out",
                    kind="subnet",
                    path=subnet.path,
                    pointer=str(subnet.pointer()),
                ),
            )

    for s in iter_resource(
        serialized,
        "$.resources[?@.meta.kind=='global-backend-service'].struct.backends.*.group",  # noqa E501
    ):
        r_id = s.parent.parent.parent.parent.obj["id"]  # type: ignore
        group = s.value
        p = f"$.resources[?@.meta.kind=='regional-neg' && @.struct.selfLink=='{group}'].struct.cloudRun.service"  # noqa E501
        for service in iter_resource(serialized, p):
            neg = service.parent.parent.parent.obj["meta"]  # type: ignore
            project = neg["project"]
            location = neg["region"]

            cloudrun_name = f"projects/{project}/locations/{location}/services/{service.obj}"  # noqa E501
            p = f"$.resources[?@.meta.kind=='cloudrun' && @.meta.name=='{cloudrun_name}']"  # noqa E501
            for subnet in iter_resource(serialized, p):
                add_link(
                    d,
                    r_id,
                    Link(
                        direction="out",
                        kind="subnet",
                        path=subnet.path,
                        pointer=str(subnet.pointer()),
                    ),
                )

        p = f"$.resources[?@.meta.kind=='zonal-neg' && @.struct.selfLink=='{group}']"  # noqa E501
        for zonal_neg in iter_resource(serialized, p):
            add_link(
                d,
                r_id,
                Link(
                    direction="out",
                    kind="zonal-neg",
                    path=zonal_neg.path,
                    pointer=str(zonal_neg.pointer()),
                ),
            )

    for s in iter_resource(
        serialized,
        "$.resources[?@.meta.kind=='global-backend-service'].struct.securityPolicy",  # noqa E501
    ):
        r_id = s.parent.parent.obj["id"]  # type: ignore
        secpolicy = s.value
        p = f"$.resources[?@.meta.kind=='global-securities' && @.meta.self_link=='{secpolicy}']"  # noqa E501
        for service in iter_resource(serialized, p):
            add_link(
                d,
                r_id,
                Link(
                    direction="out",
                    kind="global-securities",
                    path=service.path,
                    pointer=str(service.pointer()),
                ),
            )

        p = f"$.resources[?@.meta.kind=='regional-securities' && @.meta.self_link=='{secpolicy}']"  # noqa E501
        for service in iter_resource(serialized, p):
            add_link(
                d,
                r_id,
                Link(
                    direction="out",
                    kind="regional-securities",
                    path=service.path,
                    pointer=str(service.pointer()),
                ),
            )

    for s in iter_resource(
        serialized,
        "$.resources[?@.meta.kind=='regional-backend-service'].struct.securityPolicy",  # noqa E501
    ):
        r_id = cast(str, s.parent.parent.obj["id"])  # type: ignore
        secpolicy = s.value
        p = f"$.resources[?@.meta.kind=='regional-securities' && @.meta.self_link=='{secpolicy}']"  # noqa E501
        for service in iter_resource(serialized, p):
            add_link(
                d,
                r_id,
                Link(
                    direction="out",
                    kind="regional-securities",
                    path=service.path,
                    pointer=str(service.pointer()),
                ),
            )

    for s in iter_resource(
        serialized, "$.resources[?@.meta.kind=='regional-neg'].struct.network"
    ):
        r_id = cast(str, s.parent.parent.obj["id"])  # type: ignore
        network = s.value
        p = f"$.resources[?@.meta.kind=='network' && @.meta.self_link=='{network}']"  # noqa E501
        for subnet in iter_resource(serialized, p):
            add_link(
                d,
                r_id,
                Link(
                    direction="out",
                    kind="network",
                    path=subnet.path,
                    pointer=str(subnet.pointer()),
                ),
            )

    for svcneg in iter_resource(
        serialized,
        "$.resources[?@.meta.kind=='global-backend-service'].struct.backends.*.group",
    ):
        r_id = svcneg.parent.parent.parent.parent.obj["id"]  # type: ignore
        neg = svcneg.value
        p = f"$.resources[?@.meta.kind=='regional-neg' && @.struct.selfLink=='{neg}'].struct.cloudRun.service"  # noqa E501
        for cloudrun_name in iter_resource(serialized, p):  # type: ignore
            svc_name = cloudrun_name.value
            p = f"$.resources[?@.meta.kind=='cloudrun' && @.meta.name contains '{svc_name}']"  # noqa E501
            for cloudrun in iter_resource(serialized, p):
                add_link(
                    d,
                    r_id,
                    Link(
                        direction="out",
                        kind="cloudrun",
                        path=cloudrun.path,
                        pointer=str(cloudrun.pointer()),
                    ),
                )

                p = f"$.resources[?@.meta.kind=='service' && @.struct.cloudRun.serviceName=='{svc_name}']"  # noqa E501
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

                    full_svc_name = svc.obj["meta"]["name"]  # type: ignore

                    p = f"$.resources[?@.meta.kind=='slo' && match(@.meta.name, '{full_svc_name}/serviceLevelObjectives/.*')]"  # noqa E501
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
