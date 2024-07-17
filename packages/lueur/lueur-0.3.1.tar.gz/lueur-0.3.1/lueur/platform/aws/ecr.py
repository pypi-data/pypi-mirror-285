from concurrent.futures import ThreadPoolExecutor

from lueur.make_id import make_id
from lueur.models import Meta, Resource
from lueur.platform.aws.client import Client

__all__ = ["explore_ecr"]


def explore_ecr(region: str) -> list[Resource]:
    resources = []

    repositories = explore_repositories(region)
    resources.extend(repositories)

    if not repositories:
        return resources

    futures = []
    with ThreadPoolExecutor(max_workers=len(repositories)) as executor:
        for c in repositories:
            registry_id = c.struct["registryId"]
            repository_name = c.struct["repositoryName"]

            futures.append(
                executor.submit(
                    explore_images, region, registry_id, repository_name
                )
            )

    for future in futures:
        resources.extend(future.result())

    return resources


###############################################################################
# Private functions
###############################################################################
def explore_repositories(region: str) -> list[Resource]:
    results = []

    with Client("ecr", region) as c:
        repositories = c.describe_repositories()

        for repository in repositories["repositories"]:
            results.append(
                Resource(
                    id=make_id(repository["repositoryArn"]),
                    meta=Meta(
                        name=repository["repositoryName"],
                        display=repository["repositoryName"],
                        kind="repository",
                    ),
                    struct=repository,
                )
            )

    return results


def explore_images(
    region: str, registry_id: str, repository_name: str
) -> list[Resource]:
    with Client("ecr", region) as c:
        images = c.describe_images(
            registryId=registry_id, repositoryName=repository_name
        )

    results = []
    for image in images["imageDetails"]:
        name = f"{image['registryId']}/{image['repositoryName']}"
        results.append(
            Resource(
                id=make_id(image["imageDigest"]),
                meta=Meta(name=name, display=name, kind="image"),
                struct=image,
            )
        )

    return results
