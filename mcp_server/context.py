from contextvars import ContextVar

mcp_session_id_var: ContextVar[str | None] = ContextVar("mcp_session_id", default=None)
meta_progress_token_var: ContextVar[str | int | None] = ContextVar(
    "_meta.progress_token", default=None
)
