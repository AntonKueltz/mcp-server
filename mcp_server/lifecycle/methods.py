from mcp_server.data_types import MethodResult
from mcp_server.lifecycle.model import ClientCapabilities, ServerCapabilities
from mcp_server.lifecycle.protocol_version import negotiate_version
from mcp_server.lifecycle.session import session_store


def initialize(
    protocolVersion: str, capabilities: dict, clientInfo: dict
) -> MethodResult:
    ClientCapabilities.model_validate(capabilities)

    server_capabilities = ServerCapabilities()
    negotiated_version = negotiate_version(protocolVersion)

    result = {
        "protocolVersion": negotiated_version.value,
        "capabilities": server_capabilities.model_dump(),
        "serverInfo": {
            "name": "Anton's example MCP Server",
            "version": "0.1.0",
        },
    }
    headers = {"Mcp-Session-Id": session_store.assign_session()}

    return result, headers


def initialized_notification() -> MethodResult:
    print("Client initialized")
    return None, {}
