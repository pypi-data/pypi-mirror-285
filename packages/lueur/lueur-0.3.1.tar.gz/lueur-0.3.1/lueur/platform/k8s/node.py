# mypy: disable-error-code="index,call-arg,union-attr"
from typing import Any

import msgspec
from kubernetes import client

from lueur.links import add_link
from lueur.make_id import make_id
from lueur.models import Discovery, Link, Meta, Resource
from lueur.platform.k8s.client import AsyncClient, Client
from lueur.rules import iter_resource

__all__ = ["explore_node"]


async def explore_node() -> list[Resource]:
    resources = []

    async with Client(client.CoreV1Api) as c:
        nodes = await explore_nodes(c)
        resources.extend(nodes)

    return resources


###############################################################################
# Private functions
###############################################################################
async def explore_nodes(c: AsyncClient) -> list[Resource]:
    response = await c.execute("list_node")

    nodes = msgspec.json.decode(response.data)

    results = []
    for node in nodes["items"]:
        meta = node["metadata"]
        results.append(
            Resource(
                id=make_id(meta["uid"]),
                meta=Meta(
                    name=meta["name"], display=meta["name"], kind="k8s/node"
                ),
                struct=node,
            )
        )

    return results


def expand_links(d: Discovery, serialized: dict[str, Any]) -> None:
    for np in iter_resource(
        serialized, "$.resources[?@.meta.kind=='nodepool'].meta.name"
    ):
        r_id = np.parent.parent.obj["id"]
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
