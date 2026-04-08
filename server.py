import os
from fastmcp import FastMCP
from fastmcp.server.auth.providers.descope import DescopeProvider
from descope_mcp import validate_token, require_scopes
from starlette.requests import Request
from starlette.responses import JSONResponse

auth = DescopeProvider(
    config_url=os.environ["DESCOPE_CONFIG_URL"],
    base_url=os.environ.get("RENDER_EXTERNAL_URL") or os.environ.get("SERVER_URL"),
)

mcp = FastMCP("descope-render", auth=auth)


@mcp.tool()
def hello(mcp_access_token: str = None) -> str:
    """Say hello — requires the mcp:greet scope."""
    claims = validate_token(mcp_access_token)
    require_scopes(claims, ["mcp:greet"])
    return "Hello, world!"


# Custom route for Render's health checks.
@mcp.custom_route("/health", methods=["GET"])
async def health(_request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok"})


if __name__ == "__main__":
    mcp.run(transport="http")
