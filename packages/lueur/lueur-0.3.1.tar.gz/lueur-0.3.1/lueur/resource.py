from typing import Any, Iterable

import jsonpath

__all__ = [
    "iter_resource",
    "match_path",
]


def iter_resource(
    discovery: dict[str, Any], path: str
) -> Iterable[jsonpath.JSONPathMatch]:
    yield from jsonpath.finditer(path, discovery)


def match_path(
    discovery: dict[str, Any], path: str
) -> jsonpath.JSONPathMatch | None:
    return jsonpath.match(path, discovery)
