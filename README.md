# Overview
A server implementing the Model Context Protocol (MCP). This code is pre-alpha.

# Organization
TODO

# Development

### Prerequisites
* uv - `pip install uv`
* redis - [install](https://redis.io/docs/latest/operate/oss_and_stack/install/archive/install-redis/)

A redis server should be available for the application to use. By default the
application will try to connect to the default redis URI `redis://localhost:6379`.

### Run Server
For general development that does not require any coordination across requests

    uv run fastapi dev mcp_server/main.py

For development where you have multiple connections that need to coordinate (e.g.
you have an event stream open and want to test sending progress updates to it as
part of handling another request)

    uv run fastapi run --workers 2 mcp_server/main.py

### Run Tests

    uv run pytest

### Customize Queue and Session Providers

By default redis is used to provide a backend for event queuing and session storage.
Developers are free to implement their own backends. There are interfaces that the
client classes for the backend(s) must conform to -
* For event queuing - `mcp_server.sse.queue.QueueProvider`
* For session storage - `mcp_server.lifecycle.session.StoreProvider`

There are functions in `mcp_server.context` that must then be updated to use these
providers -
* `get_event_queue` which should `yield` an `mcp_server.sse.queue.EventQueue` instance that was instantiated with an instance of your custom queue provider passed to it.
* `get_session_store` which should `yield` an `mcp_server.lifecycle.session.SessionStore` instance that was instantiated with an instance of your custom session provider passed to it.
