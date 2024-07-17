# mypy: disable-error-code="call-arg"
import msgspec
from kubernetes import client

from lueur.make_id import make_id
from lueur.models import Meta, Resource
from lueur.platform.k8s.client import AsyncClient, Client

__all__ = ["explore_ingress"]


async def explore_ingress() -> list[Resource]:
    resources = []

    async with Client(client.NetworkingV1Api) as c:
        ingresses = await explore_ingresses(c)
        resources.extend(ingresses)

    return resources


###############################################################################
# Private functions
###############################################################################
async def explore_ingresses(c: AsyncClient) -> list[Resource]:
    response = await c.execute("list_ingress_for_all_namespaces")

    ingresses = msgspec.json.decode(response.data)

    results = []
    for ingress in ingresses["items"]:
        meta = ingress["metadata"]
        results.append(
            Resource(
                id=make_id(meta["uid"]),
                meta=Meta(
                    name=meta["name"], display=meta["name"], kind="k8s/ingress"
                ),
                struct=ingress,
            )
        )

    return results
