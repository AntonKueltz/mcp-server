from mcp_server.lifecycle.model import ClientCapabilities, ServerCapabilities
from mcp_server.lifecycle.protocol_version import negotiate_version


def initialize(protocolVersion: str, capabilities: dict, clientInfo: dict) -> dict:
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
    return result


def initialized_notification():
    print("Client initialized")
