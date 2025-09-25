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


### Add Prompts

Use the `mcp_server.prompts.prompt` decorator to create a new prompt. The decorator
should be applied to a function with the following signature (takes in the prompt
arguments from the client and returns the appropriate message(s))

```python
f: Callable[..., Awaitable[list[mcp_server.prompts.model.Message]]]
```

As an example, this is how we might implement the
[code review prompt from the MCP spec](https://modelcontextprotocol.io/specification/2025-06-18/server/prompts#getting-a-prompt)

```python
from mcp_server.prompts import prompt
from mcp_server.prompts.model import Argument, Message, Role, TextContent


@prompt(
    name="code_review",
    title="Request Code Review",
    description="Asks the LLM to analyze code quality and suggest improvements",
    arguments=[Argument(name="code", description="The code to review", required=True)],
)
async def code_review(code: str) -> list[Message]:
    text = f"Please review this code:\n```{code}```"
    message = Message(role=Role.USER, content=TextContent(text=text))
    return [message]
```


### Add Tools

Use the `mcp_server.tools.tool` decorator to create a new tool. The decorator
should be applied to a function with the following signature (takes in the tool
arguments from the client and returns the appropriate content)

```python
f: Callable[..., Awaitable[mcp_server.model.Content]]
```

As an example, this is how we might implement the
[get weather tool from the MCP spec](https://modelcontextprotocol.io/specification/2025-06-18/server/tools#protocol-messages)

```python
from mcp_server.model import TextContent
from mcp_server.tools import tool


@tool(
    name="get_weather",
    title="Weather Information Provider",
    description="Get current weather information for a location",
    input_schema={
        "type": "object",
        "properties": {
            "location": {"type": "string", "description": "City name or zip code"}
        },
        "required": ["location"],
    },
)
async def get_weather(location: str) -> TextContent:
    text = (
        f"Current weather in {location}:\nTemperature: 72°F\nConditions: Partly cloudy"
    )
    return TextContent(text=text)
```


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


# TODO

## Prompts
- pagination support
- list changed notifications (hook into `add_prompt` method)

## Resources
- pagination support
- resource templates
- annotations support
- list changed notifications (hook into `add-resource` method)
- subscription notifications

## Tools
- pagination support
- list changed notifications (hook into `add_prompt` method)
