# mypy: disable-error-code="union-attr"
import asyncio
from typing import Any

import msgspec
from google.oauth2._service_account_async import Credentials

from lueur.links import add_link
from lueur.make_id import make_id
from lueur.models import Discovery, Link, Meta, Resource
from lueur.platform.gcp.client import AuthorizedSession, Client
from lueur.rules import iter_resource

__all__ = ["explore_gke"]


async def explore_gke(
    project: str, location: str, creds: Credentials | None = None
) -> list[Resource]:
    resources = []

    async with Client("https://container.googleapis.com", creds) as c:
        clusters = await explore_clusters(c, project, location)
        resources.extend(clusters)

        tasks: list[asyncio.Task] = []

        async with asyncio.TaskGroup() as tg:
            for cl in clusters:
                tasks.append(
                    tg.create_task(
                        explore_nodepools(c, project, location, cl.meta.name)
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
async def explore_clusters(
    c: AuthorizedSession, project: str, location: str
) -> list[Resource]:
    response = await c.get(
        f"/v1/projects/{project}/locations/{location}/clusters"
    )

    clusters = msgspec.json.decode(response.content)

    results = []
    for cl in clusters["clusters"]:
        results.append(
            Resource(
                id=make_id(cl["id"]),
                meta=Meta(name=cl["name"], display=cl["name"], kind="cluster"),
                struct=cl,
            )
        )

    return results


async def explore_nodepools(
    c: AuthorizedSession, project: str, location: str, cluster_name: str
) -> list[Resource]:
    response = await c.get(
        f"/v1/projects/{project}/locations/{location}/clusters/{cluster_name}/nodePools"  # noqa E501
    )

    node_pools = msgspec.json.decode(response.content)

    results = []
    for np in node_pools["nodePools"]:
        results.append(
            Resource(
                id=make_id(np["selfLink"]),
                meta=Meta(name=np["name"], display=np["name"], kind="nodepool"),
                struct=np,
            )
        )

    return results


def expand_links(d: Discovery, serialized: dict[str, Any]) -> None:
    for np in iter_resource(
        serialized, "$.resources[?@.meta.kind=='cluster'].struct.network"
    ):
        r_id = np.parent.parent.obj["id"]  # type: ignore
        name = np.value
        p = f"$.resources[?@.meta.kind=='k8s/node' && @.struct.metadata.labels.['cloud.google.com/gke-nodepool']=='{name}']"  # noqa E501
        for k8snode in iter_resource(serialized, p):
            add_link(
                d,
                r_id,
                Link(
                    direction="out",
                    kind="k8s/node",
                    path=k8snode.path,
                    pointer=str(k8snode.pointer()),
                ),
            )

        p = f"$.resources[?@.meta.kind=='network' && @.meta.name=='{name}']"
        for k8snode in iter_resource(serialized, p):
            add_link(
                d,
                r_id,
                Link(
                    direction="out",
                    kind="network",
                    path=k8snode.path,
                    pointer=str(k8snode.pointer()),
                ),
            )

    for np in iter_resource(
        serialized, "$.resources[?@.meta.kind=='cluster'].struct.subnetwork"
    ):
        p = f"$.resources[?@.meta.kind=='subnet' && @.meta.name=='{name}']"
        for k8snode in iter_resource(serialized, p):
            add_link(
                d,
                r_id,
                Link(
                    direction="out",
                    kind="subnet",
                    path=k8snode.path,
                    pointer=str(k8snode.pointer()),
                ),
            )

    for np in iter_resource(
        serialized,
        "$.resources[?@.meta.kind=='cluster'].struct.nodePools.*.name",
    ):
        r_id = np.parent.parent.parent.parent.obj["id"]  # type: ignore
        np_name = np.value
        p = f"$.resources[?@.meta.kind=='nodepool' && @.meta.name=='{np_name}']"
        for svc in iter_resource(serialized, p):
            add_link(
                d,
                r_id,
                Link(
                    direction="out",
                    kind="nodepool",
                    path=svc.path,
                    pointer=str(svc.pointer()),
                ),
            )

    for s in iter_resource(
        serialized, "$.resources[?@.meta.kind=='cluster'].meta.name"
    ):
        r_id = s.parent.parent.obj["id"]  # type: ignore
        name = s.value
        p = f"$.resources[?@.meta.kind=='service' && @.struct.gkeWorkload.clusterName=='{name}']"  # noqa E501
        for service in iter_resource(serialized, p):
            add_link(
                d,
                r_id,
                Link(
                    direction="out",
                    kind="service",
                    path=service.path,
                    pointer=str(service.pointer()),
                ),
            )
