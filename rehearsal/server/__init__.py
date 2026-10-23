"""Reference MCP server package containing flawed and corrected tool implementations."""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from rehearsal.server.server import create_reference_server, get_streamable_http_app, get_sse_app, app, reference_server

__all__ = ["create_reference_server", "get_streamable_http_app", "get_sse_app", "app", "reference_server"]


def __getattr__(name: str) -> Any:
    """Lazy-load server objects to avoid runpy circular execution warnings."""
    if name in __all__:
        import rehearsal.server.server as srv
        return getattr(srv, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
