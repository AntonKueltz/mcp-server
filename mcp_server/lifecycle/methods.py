from mcp_server.context import RequestContext
from mcp_server.data_types import MethodResult
from mcp_server.lifecycle.model import (
    ClientCapabilities,
    ServerCapabilities,
    SubCapabilities,
)
from mcp_server.lifecycle.protocol_version import negotiate_version


async def initialize(
    protocolVersion: str,
    capabilities: dict,
    clientInfo: dict,
    request_context: RequestContext,
) -> MethodResult:
    ClientCapabilities.model_validate(capabilities)

    server_capabilities = ServerCapabilities(
        prompts=SubCapabilities(list_changed=False)
    )
    negotiated_version = negotiate_version(protocolVersion)

    session_id = await request_context.session_store.assign_session()

    await request_context.session_store.set_session_data(
        session_id, "mcp-protocol-version", negotiated_version.value
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


async def initialized_notification(request_context: RequestContext) -> MethodResult:
    print("Client initialized")
    return None, {}
