# mypy: disable-error-code="call-arg"
import msgspec
from kubernetes import client

from lueur.make_id import make_id
from lueur.models import Meta, Resource
from lueur.platform.k8s.client import AsyncClient, Client

__all__ = ["explore_pod"]


async def explore_pod() -> list[Resource]:
    resources = []

    async with Client(client.CoreV1Api) as c:
        pods = await explore_pods(c)
        resources.extend(pods)

    return resources


###############################################################################
# Private functions
###############################################################################
async def explore_pods(c: AsyncClient) -> list[Resource]:
    response = await c.execute("list_pod_for_all_namespaces")

    pods = msgspec.json.decode(response.data)

    results = []
    for pod in pods["items"]:
        meta = pod["metadata"]
        results.append(
            Resource(
                id=make_id(meta["uid"]),
                meta=Meta(
                    name=meta["name"], display=meta["name"], kind="k8s/pod"
                ),
                struct=pod,
            )
        )

    return results
