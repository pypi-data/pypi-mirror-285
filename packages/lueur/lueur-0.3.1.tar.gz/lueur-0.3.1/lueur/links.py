from typing import Any, cast

import jsonpath

from lueur.models import Discovery, Link

__all__ = ["add_link", "get_linked_resource"]


def add_link(d: Discovery, resource_id: str, link: Link) -> None:
    for r in d.resources:
        if r.id == resource_id:
            r.links.append(link)
            break


def get_linked_resource(
    discovery: dict[str, Any], pointer: str
) -> dict[str, str]:
    return cast(
        dict[str, str], jsonpath.JSONPointer(pointer).resolve(discovery)
    )
