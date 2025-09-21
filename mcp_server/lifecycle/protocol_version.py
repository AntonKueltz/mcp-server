from enum import Enum
from http.client import BAD_REQUEST

from fastapi import HTTPException


class ProtocolVersion(Enum):
    VERSION_2025_03_26 = "2025-03-26"
    VERSION_2025_06_18 = "2025-06-18"


def negotiate_version(client_version: str) -> ProtocolVersion:
    """Negotiate the version of the MCP that will be used between the client and server.

    If the server supports the requested protocol version, it MUST respond with the same
    version. Otherwise, the server MUST respond with another protocol version it supports.
    This SHOULD be the latest version supported by the server.
    """
    try:
        return ProtocolVersion(client_version)
    except ValueError:
        return ProtocolVersion.VERSION_2025_06_18


async def identify_protocol_version(headers: dict) -> ProtocolVersion:
    """The protocol version sent by the client SHOULD be the one negotiated during initialization.

    For backwards compatibility, if the server does not receive an MCP-Protocol-Version header,
    and has no other way to identify the version - for example, by relying on the protocol version
    negotiated during initialization - the server SHOULD assume protocol version 2025-03-26.

    If the server receives a request with an invalid or unsupported MCP-Protocol-Version, it MUST
    respond with 400 Bad Request.
    """
    from mcp_server.main import app

    client_provided = headers.get("mcp-protocol-version")

    if client_provided:
        try:
            return ProtocolVersion(client_provided)
        except ValueError:
            raise HTTPException(status_code=BAD_REQUEST)

    if version := await app.state.session_store.get_session_data(
        "mcp-protocol-version"
    ):
        return ProtocolVersion(version)

    return ProtocolVersion.VERSION_2025_03_26
