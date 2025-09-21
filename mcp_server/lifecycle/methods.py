from mcp_server.context import mcp_session_id_var
from mcp_server.data_types import MethodResult
from mcp_server.lifecycle.model import ClientCapabilities, ServerCapabilities
from mcp_server.lifecycle.protocol_version import negotiate_version


async def initialize(
    protocolVersion: str, capabilities: dict, clientInfo: dict
) -> MethodResult:
    from mcp_server.main import app

    ClientCapabilities.model_validate(capabilities)

    server_capabilities = ServerCapabilities()
    negotiated_version = negotiate_version(protocolVersion)

    session_id = await app.state.session_store.assign_session()
    mcp_session_id_var.set(session_id)

    await app.state.session_store.set_session_data(
        "mcp-protocol-version", negotiated_version.value
    )

    result = {
        "protocolVersion": negotiated_version.value,
        "capabilities": server_capabilities.model_dump(),
        "serverInfo": {
            "name": "Anton's example MCP Server",
            "version": "0.1.0",
        },
    }
    headers = {"mcp-session-id": session_id}
    return result, headers


async def initialized_notification() -> MethodResult:
    print("Client initialized")
    return None, {}
