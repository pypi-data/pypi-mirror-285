import json
import os
from pathlib import Path
from typing import Any, Iterator, Optional
from urllib.parse import urlparse

import duckdb
import requests
import yaml
from airfold_common.config import merge_dicts
from airfold_common.error import AirfoldError
from airfold_common.utils import dict_from_env, model_hierarchy
from shortuuid import ShortUUID

from airfold_cli.models import Config, UserPermissions, UserProfile

CONFIG_PATH = Path().cwd() / ".airfold" / "config.yaml"
CONFIG_DIR = os.path.dirname(CONFIG_PATH)
PROJECT_DIR = "airfold"

PREFIX = "AIRFOLD"


def decode_short_uuid(short_uuid: str) -> str:
    return str(ShortUUID("0123456789abcdefghijklmnopqrstuvwxyz").decode(short_uuid))


def save_config(config: Config) -> str:
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        yaml.safe_dump(config.dict(unmask=True), f)
    return str(CONFIG_PATH)


def find_config() -> Path | None:
    current_dir = Path.cwd().absolute()
    while current_dir:
        config_path = current_dir / ".airfold" / "config.yaml"
        if config_path.exists() and config_path.is_file():
            return config_path
        if current_dir == current_dir.parent:
            return None
        else:
            current_dir = current_dir.parent
    return None


def load_config() -> Config:
    env_data: dict = dict_from_env(model_hierarchy(Config), PREFIX)
    data: dict = {}
    config_file = find_config()
    if config_file:
        config_data = yaml.safe_load(open(config_file))
        merge_dicts(data, config_data)
    merge_dicts(data, env_data)
    if not data:
        raise AirfoldError(
            f"Could not load config from {Path().cwd()} or environment variables, please run `af config`"
        )
    return Config(**data)


def normalize_path_args(path: list[str] | str | None) -> list[str]:
    res: list[str]
    if not path:
        path = [os.path.join(os.getcwd(), PROJECT_DIR)]
    if isinstance(path, str):
        res = [path]
    else:
        res = path
    return res


def dump_json(data: Any) -> str:
    return json.dumps(data, indent=2)


def get_org_permissions(user: UserProfile, _org_id: str | None = None) -> UserPermissions | None:
    org_id: str = _org_id or user.organizations[0].id
    for perm in user.permissions:
        if perm.org_id == org_id:
            return perm
    return None


def display_roles(user: UserProfile, org_id: str, proj_id: str) -> str:
    if bool([org for org in user.organizations if org.id == org_id]):
        return "Owner"
    for perm in user.permissions:
        if perm.org_id == org_id:
            roles = perm.roles
            for r in roles:
                if f"projects/{proj_id}" in r:
                    return r
            return ",".join(roles)
    return ""


def set_current_project(proj_id):
    config = load_config()
    conf = Config(**config.dict(exclude={"proj_id"}), proj_id=proj_id)
    save_config(conf)


def is_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def load_csv_file(path_or_url: str, chunk_size: Optional[int] = None) -> Iterator[list[dict]]:
    """Load data as a list of python dicts from CSV file."""
    data = duckdb.read_csv(path_or_url, header=True)
    if chunk_size is None:
        yield data.to_arrow_table().to_pylist()
    else:
        for batch in data.fetch_arrow_table().to_batches(chunk_size):
            yield batch.to_pylist()


def load_ndjson_file(path_or_url: str, chunk_size: Optional[int] = None) -> Iterator[list[dict]]:
    """Load data as a list of python dicts from NDJSON file."""
    data = duckdb.read_json(path_or_url)
    if chunk_size is None:
        yield data.to_arrow_table().to_pylist()
    else:
        for batch in data.fetch_arrow_table().to_batches(chunk_size):
            yield batch.to_pylist()


def load_data_file(path_or_url: str, file_format: str, chunk_size: Optional[int] = None) -> Iterator[list[dict]]:
    if file_format == "csv":
        return load_csv_file(path_or_url, chunk_size)
    elif file_format == "ndjson" or file_format == "json":
        return load_ndjson_file(path_or_url, chunk_size)
    else:
        raise ValueError(f"Unsupported file format {file_format}")


def get_file_type(path_or_url) -> Optional[str]:
    try:
        if is_url(path_or_url):
            path_or_url = urlparse(path_or_url).path
        return os.path.splitext(path_or_url)[1][1:].lower()
    except Exception:
        return None


def get_file_name(path_or_url: str) -> Optional[str]:
    try:
        if is_url(path_or_url):
            path_or_url = urlparse(path_or_url).path
        base_name = os.path.basename(path_or_url)
        return os.path.splitext(base_name)[0].lower()
    except Exception:
        return None


def get_file_size(path_or_url: str) -> Optional[int]:
    try:
        if is_url(path_or_url):
            r = requests.head(path_or_url)
            if r.status_code == requests.codes.ok:
                return int(r.headers["content-length"])
            else:
                return None
        else:
            return os.stat(path_or_url).st_size
    except Exception:
        return None
