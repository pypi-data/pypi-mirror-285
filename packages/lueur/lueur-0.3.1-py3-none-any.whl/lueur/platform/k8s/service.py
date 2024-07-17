# mypy: disable-error-code="call-arg,index"
import msgspec
from kubernetes import client

from lueur.make_id import make_id
from lueur.models import Meta, Resource
from lueur.platform.k8s.client import AsyncClient, Client

__all__ = ["explore_service"]


async def explore_service() -> list[Resource]:
    resources = []

    async with Client(client.CoreV1Api) as c:
        services = await explore_services(c)
        resources.extend(services)

    return resources


###############################################################################
# Private functions
###############################################################################
async def explore_services(c: AsyncClient) -> list[Resource]:
    response = await c.execute("list_service_for_all_namespaces")

    services = msgspec.json.decode(response.data)

    results = []
    for service in services["items"]:
        meta = service["metadata"]
        results.append(
            Resource(
                id=make_id(meta["uid"]),
                meta=Meta(
                    name=meta["name"], display=meta["name"], kind="k8s/service"
                ),
                struct=service,
            )
        )

    return results
