from pathlib import Path

from pydantic import AnyUrl

from mcp_server.resources.inventory import all_resources
from mcp_server.resources.model import TextContent


def _determine_mime_type(path: Path) -> str:
    match path.suffix:
        case ".py":
            return "text/x-python"
        case ".rs":
            return "text/x-rust"
        case _:
            return "text/plain"


def read_file(uri: AnyUrl) -> TextContent:
    if not uri.path or uri not in all_resources:
        raise ValueError("Invalid file URI")

    path = Path(uri.path)
    if not path.exists() or path.is_dir():
        raise ValueError("Invalid file URI")

    with path.open() as f:
        text = f.read()
    mime_type = _determine_mime_type(path)

    return TextContent(mime_type=mime_type, text=text)
