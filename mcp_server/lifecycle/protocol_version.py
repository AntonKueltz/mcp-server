from enum import Enum


class ProtocolVersion(Enum):
    VERSION_2024_11_05 = "2024-11-05"
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
