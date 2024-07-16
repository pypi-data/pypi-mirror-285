from typing import Generator

from airfold_common.format import ChFormat, Format
from airfold_common.project import ProjectFile
from cachetools import TTLCache, cached

from airfold_cli.api import AirfoldApi


@cached(cache=TTLCache(maxsize=10000, ttl=5))
def get_source_names() -> list[str]:
    api = AirfoldApi.from_config()
    files = api.pull()
    formatter: Format = ChFormat()
    sources: list[ProjectFile] = list(filter(lambda f: formatter.is_source(f.data), files))
    return [source.name for source in sources]


def source_name_completion(cur: str) -> Generator[str, None, None]:
    """Pipe name completion."""
    try:
        source_names: list[str] = get_source_names()
        yield from filter(lambda name: name.startswith(cur), source_names) if cur else source_names
    except Exception as e:
        pass
