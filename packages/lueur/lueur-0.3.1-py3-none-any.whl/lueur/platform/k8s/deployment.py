# mypy: disable-error-code="call-arg,index"
import msgspec
from kubernetes import client

from lueur.make_id import make_id
from lueur.models import Meta, Resource
from lueur.platform.k8s.client import AsyncClient, Client

__all__ = ["explore_deployment"]


async def explore_deployment() -> list[Resource]:
    resources = []

    async with Client(client.AppsV1Api) as c:
        pods = await explore_deployments(c)
        resources.extend(pods)

    return resources


###############################################################################
# Private functions
###############################################################################
async def explore_deployments(c: AsyncClient) -> list[Resource]:
    response = await c.execute("list_deployment_for_all_namespaces")

    deployments = msgspec.json.decode(response.data)

    results = []
    for deployment in deployments["items"]:
        meta = deployment["metadata"]
        results.append(
            Resource(
                id=make_id(meta["uid"]),
                meta=Meta(
                    name=meta["name"],
                    display=meta["name"],
                    kind="k8s/deployment",
                ),
                struct=deployment,
            )
        )

    return results
