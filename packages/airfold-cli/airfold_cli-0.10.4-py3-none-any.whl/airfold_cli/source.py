import json
import os.path
from collections import deque
from typing import Annotated, Any, Optional

from airfold_common.error import AirfoldError
from airfold_common.format import ChFormat
from airfold_common.log import log
from airfold_common.plan import print_plan
from airfold_common.project import (
    LocalFile,
    ProjectFile,
    dump_project_files,
    dump_yaml,
    get_local_files,
)
from airfold_common.utils import STREAM_MARKER, find_files, is_path_stream
from rich.progress import TaskID
from rich.syntax import Syntax
from typer import Argument, Context, Option

from airfold_cli import app
from airfold_cli.api import AirfoldApi
from airfold_cli.cli import AirfoldTyper
from airfold_cli.error import RequestTooLargeError
from airfold_cli.models import SourceInfo
from airfold_cli.options import (
    DryRunOption,
    ForceOption,
    PathOrURL,
    SourceNameArgument,
    TargetDir,
    with_global_options,
)
from airfold_cli.root import catch_airfold_error
from airfold_cli.tui.progress import IngestProgress
from airfold_cli.tui.syntax import get_syntax_theme
from airfold_cli.utils import (
    dump_json,
    get_file_name,
    get_file_size,
    get_file_type,
    is_url,
    load_data_file,
)

source_app = AirfoldTyper(
    name="source",
    help="Source commands.",
)

app.add_typer(source_app)


@source_app.command("drop")
@catch_airfold_error()
@with_global_options
def drop(
    ctx: Context,
    name: Annotated[str, SourceNameArgument],
    dry_run: Annotated[bool, DryRunOption] = False,
    force: Annotated[bool, ForceOption] = False,
) -> None:
    """Delete source.
    \f

    Args:
        ctx: Typer context
        name: source name
        dry_run: show plan without executing it
        force: force delete/overwrite even if data will be lost

    """
    source_app.apply_options(ctx)

    api = AirfoldApi.from_config()
    commands = api.source_delete(name=name, dry_run=dry_run, force=force)

    if source_app.is_terminal():
        print_plan(commands, console=source_app.console)
    else:
        source_app.console.print(dump_json(commands))


@source_app.command("ls")
@catch_airfold_error()
@with_global_options
def ls(ctx: Context) -> None:
    """List sources.
    \f

    Args:
        ctx: Typer context

    """
    source_app.apply_options(ctx)

    api = AirfoldApi.from_config()
    sources_info: list[SourceInfo] = api.list_sources()

    if not sources_info:
        if source_app.is_terminal():
            source_app.console.print("\t[magenta]NO SOURCES[/magenta]")
        return

    data: list[dict] = [pipe_info.dict(humanize=True) for pipe_info in sources_info]
    if source_app.is_terminal():
        columns = {
            "Name": "name",
            "Rows": "rows",
            "Bytes": "bytes",
            "Errors": "errors",
            "Created": "created",
            "Updated": "updated",
        }
        source_app.ui.print_table(columns, data=data, title=f"{len(sources_info)} sources")
    else:
        for source_info in sources_info:
            source_app.console.print(dump_json(source_info.dict()))


# @source_app.command("rename")
@catch_airfold_error()
@with_global_options
def rename(
    ctx: Context,
    name: Annotated[str, SourceNameArgument],
    new_name: Annotated[str, Argument(help="New source name")],
    dry_run: Annotated[bool, DryRunOption] = False,
    force: Annotated[bool, ForceOption] = False,
) -> None:
    """Rename source.
    \f

    Args:
        ctx: Typer context
        name: source name
        new_name: new source name
        dry_run: show plan without executing it
        force: force delete/overwrite even if data will be lost

    """
    source_app.apply_options(ctx)

    api = AirfoldApi.from_config()
    commands = api.rename_source(name=name, new_name=new_name, dry_run=dry_run, force=force)
    if source_app.is_terminal():
        print_plan(commands, console=source_app.console)
    else:
        source_app.console.print(dump_json(commands))


class MovingAverage:
    def __init__(self, window_size):
        self.window_size = window_size
        self.values = deque(maxlen=window_size)
        self.sum = 0.0

    def update(self, value):
        if len(self.values) == self.window_size:
            self.sum -= self.values[0]
        self.values.append(value)
        self.sum += value

    def average(self):
        return self.sum / len(self.values)


@source_app.command("append")
@catch_airfold_error()
@with_global_options
def append(
    ctx: Context,
    name: Annotated[str, SourceNameArgument],
    path: Annotated[list[str], PathOrURL],
) -> None:
    """Append data to source.
    \f

    Args:
        ctx: Typer context
        name: source name
        path: path to local file(s) or URL(s)

    """
    source_app.apply_options(ctx)

    api = AirfoldApi.from_config()

    paths: list[str] = []

    for p in list(set(path)):
        if is_url(p):
            paths.append(p)
        else:
            paths.extend([str(f) for f in find_files(p)])

    chunk_size: int = 2000
    avg_event_size = MovingAverage(chunk_size)
    total_events_sent: int = 0

    with IngestProgress() as progress:
        total_task = progress.add_task("Ingesting...", total=len(paths), progress_type="overall")
        for path_or_url in paths:
            if is_path_stream(path_or_url):
                source_app.ui.print_warning(f"Cannot append data from stdin: {path_or_url}. Skipping.")
                continue

            file_type: Optional[str] = get_file_type(path_or_url)
            if not file_type:
                source_app.ui.print_warning(f"Failed to detect file type for: {path_or_url}. Skipping.")
                continue

            ingest_task: TaskID = progress.add_task(
                f"",
                path_or_url=path_or_url,
                total=get_file_size(path_or_url),
                start=True,
                progress_type="ingest",
            )

            for chunk in load_data_file(path_or_url, file_type, chunk_size=chunk_size):
                events_chunk: list[str] = []

                for row in chunk:
                    event = json.dumps(row, default=str)
                    events_chunk.append(event)
                    avg_event_size.update(len(event))

                max_batch_size = max(1, int((api.get_max_events_length() // avg_event_size.average()) * 0.9))
                batch_size = min(max_batch_size, len(events_chunk))
                events_sent: int = 0
                while events_sent < len(events_chunk):
                    try:
                        events_batch: list[str] = events_chunk[
                            events_sent : min(len(events_chunk), events_sent + batch_size)
                        ]
                        api.send_events(src_name=name, events=events_batch)
                        events_sent += len(events_batch)
                        # TODO: needs to update progress by events count or by read bytes.
                        progress.update(ingest_task, advance=sum([len(e.encode("utf-8")) for e in events_batch]))
                        total_events_sent += len(events_batch)
                    except RequestTooLargeError:
                        if batch_size == 1:
                            raise AirfoldError(f"Event is too large: avg {avg_event_size.average()} bytes")
                        log.debug(f"Events batch is too large. Reducing batch size.")
                        batch_size = max(1, int(batch_size * 0.75))
                        log.debug(f"New batch size: {batch_size}")
            progress.update(total_task, advance=1)
    log.debug(f"Total events sent: {total_events_sent}")


@source_app.command("create")
@catch_airfold_error()
@with_global_options
def create(
    ctx: Context,
    events_path: Annotated[list[str], PathOrURL],
    path: Annotated[Optional[str], TargetDir] = None,
    out: Annotated[
        Optional[str],
        Option("--out", help="New source output path, ex.: sources/src1.yaml. It overrides `path` argument."),
    ] = None,
) -> None:
    """Create source.
    \f

    Args:
        ctx: Typer context
        path: path to local file(s) or URL(s)
        out: new source output path


    """
    source_app.apply_options(ctx)

    api = AirfoldApi.from_config()

    paths: list[str] = []

    for p in list(set(events_path)):
        if is_url(p):
            paths.append(p)
        else:
            paths.extend([str(f) for f in find_files(p)])

    source_schema: dict[str, Any] = {}
    for path_or_url in paths:
        if is_path_stream(path_or_url):
            source_app.ui.print_warning(f"Cannot get data from stdin: {path_or_url}. Skipping.")
            continue

        file_type: Optional[str] = get_file_type(path_or_url)
        if not file_type:
            source_app.ui.print_warning(f"Failed to detect file type for: {path_or_url}. Skipping.")
            continue

        for chunk in load_data_file(path_or_url, file_type, chunk_size=50):
            events_chunk: list[str] = [json.dumps(row, default=str) for row in chunk]
            source_schema = api.infer_schema(events=events_chunk)
            if not source_schema.get("name"):
                source_schema["name"] = get_file_name(out) if out else get_file_name(path_or_url)
            break
        break

    if not path:
        path = STREAM_MARKER

    pf = ProjectFile(
        name=source_schema["name"], data=ChFormat().normalize(source_schema.copy(), source_schema["name"]), pulled=False
    )
    if not out:
        source_file = get_local_files(ChFormat(), [pf])[0]
    else:
        source_file = LocalFile(**pf.dict(), path=os.path.basename(out))
    out_dir = os.path.dirname(out) if out else path

    if not is_path_stream(out_dir):
        dump_project_files([source_file], out_dir)
        if source_app.is_terminal():
            source_app.ui.print_success(f"Source saved to: {os.path.join(out_dir, source_file.path)}")
    else:
        app.console.print(Syntax(dump_yaml(pf.data), "yaml", theme=get_syntax_theme()))


@source_app.command("truncate")
@catch_airfold_error()
@with_global_options
def truncate(
    ctx: Context,
    name: Annotated[str, SourceNameArgument],
) -> None:
    """Truncate source (delete all data).
    \f

    Args:
        ctx: Typer context
        name: source name

    """
    source_app.apply_options(ctx)

    api = AirfoldApi.from_config()
    api.source_truncate(name=name)
    if source_app.is_interactive():
        source_app.ui.print_success(f"Source truncated")


@source_app.command("delete")
@catch_airfold_error()
@with_global_options
def delete(
    ctx: Context,
    name: Annotated[str, SourceNameArgument],
    where: Annotated[str, Option("--where", help="SQL WHERE condition to delete data. Ex.: logLevel='ERROR'")],
) -> None:
    """Delete source data.
    \f

    Args:
        ctx: Typer context
        name: source name
        where: delete condition
    """
    source_app.apply_options(ctx)

    api = AirfoldApi.from_config()
    api.source_delete_data(name=name, where=where)
    if source_app.is_interactive():
        source_app.ui.print_success(f"Source data deleted")
