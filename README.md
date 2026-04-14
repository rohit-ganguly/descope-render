# MCP Server Template with Descope Auth (Python)

A simple FastMCP server template for [Render](https://render.com), with full MCP authentication by [Descope](https://descope.com).

## What's included

- A working MCP server using [FastMCP](https://gofastmcp.com/getting-started/welcome) with Streamable HTTP transport
- Full MCP Authorization Support with FastMCP's `DescopeProvider` and the `descope-mcp` SDK
- One example tool (`hello`) that returns `"Hello, world!"` and enforces tool-level scope requirements (`mcp:greet`)
- A `render.yaml` Blueprint for easy deployment

> **Note:** This template deploys on Render's free plan by default. Free services spin down after 15 minutes of inactivity, causing cold starts of 30-60 seconds on the next request. MCP clients may time out during this delay. For reliable use, upgrade to a [paid plan](https://render.com/pricing) in the Render Dashboard — the Starter plan keeps your service running continuously.

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- A [Descope](https://www.descope.com) account and project

## Descope Setup

1. Log in to the [Descope Console](https://app.descope.com).
2. Navigate to **Agentic Identity Hub → MCP Servers**.
3. Click **+ MCP Server** to create a new MCP server and give it a name.
4. Under **MCP Client Registration**, enable **Client ID Metadata Documents (CIMD)** and **Dynamic Client Registration (DCR)**. Optionally, you can restrict allowed domains for clients registering via CIMD (e.g. `https://claude.ai`) - feel free to leave this field blank.
5. Under **MCP Server Scopes**, add a scope named `mcp:greet` and a simple description like "Greet the user".
6. Click **Create**.
7. Expand the `Connect your MCP server to Descope` section on the confirmation page
8. Copy the **Well-Known URL**. It looks like this:

   ```url
   https://api.descope.com/v1/apps/agentic/.../.well-known/openid-configuration
   ```

   This is your `DESCOPE_CONFIG_URL`.

> **Note:** Descope issues tokens following Resource Indicators (RFC 8707), as required by the MCP spec. When you're deploying to Render or running locally, you'll need to update the MCP Server URLs section.

## Deploying to Render

> Ensure that you've completed the [Descope Setup](#descope-setup) step prior to developing locally, as you'll need your `DESCOPE_CONFIG_URL`.

1. Fork this repository to your GitHub account.
2. Click **Deploy to Render** (or fork this repo on GitHub and import it as a Blueprint in your Render account).

   [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

3. In your Specified Configurations, set the environment variable to the value obtained in the [Descope Setup](#descope-setup) step:

   | Key | Value |
   | --- | --- |
   | `DESCOPE_CONFIG_URL` | Your Well-Known URL from the Descope Console |

4. Click **Deploy Blueprint**.
5. Once live, copy your Render service URL (e.g. `https://<your-project>.onrender.com`), append `/mcp`, and add it to **MCP Server URLs** in the Descope Console.

*You now have a remotely hosted MCP Server with the full auth spec supported!*

## Local development

> Ensure that you've completed the [Descope Setup](#descope-setup) step prior to developing locally, as you'll need your `DESCOPE_CONFIG_URL`.

First, fork this repo to your GitHub account, then follow the instructions below to set up your environment.

```bash
# Install dependencies
uv sync

# Set required environment variables
export DESCOPE_CONFIG_URL="<your URL from Descope>"
export SERVER_URL="http://localhost:8000"

# Run the server
uv run server.py --transport http --port 8000
```

When you run this locally, your server will run at `http://localhost:8000/mcp`.

## Available tools

| Tool | Description | Required scope |
| --- | --- | --- |
| `hello` | Returns `"Hello, world!"` | `mcp:greet` |

## Next steps

Now that you're all set up, there's a few more steps we recommend if you're taking your MCP Server to production.

### Add your own tools

Replace or extend the `hello` tool in `server.py` with your own logic. For each new tool:

1. Define a new scope in the Descope Console under **MCP Server Scopes** (e.g. `mcp:your-scope`).
2. Add the tool using the `@mcp.tool()` decorator.
3. Call `require_scopes(token, ["mcp:your-scope"])` inside the tool body to enforce access control.
4. Add the new tool and its required scope to the **Available tools** table above.

```python
@mcp.tool()
def my_tool() -> str:
    token = validate_token()
    require_scopes(token, ["mcp:your-scope"])
    return "your result"
```

### Use a custom domain on Render

By default, your service is reachable at `https://<your-project>.onrender.com`. To use a custom domain:

1. In the Render Dashboard, go to your service → **Settings → Custom Domains**.
2. Add your domain and follow the DNS instructions provided.
3. Once the domain is verified, update **MCP Server URLs** in the Descope Console to use your custom domain (e.g. `https://mcp.yourdomain.com/mcp`).
4. No code changes are needed - `RENDER_EXTERNAL_URL` is set automatically by Render and will reflect the primary domain.

### Protect all tools with scopes

The `require_scopes()` check is intentionally opt-in per tool so you can add unauthenticated tools if needed. For a production server, it is good practice to call `require_scopes()` in every tool. You can also centralize this by writing a helper that wraps `validate_token()` and `require_scopes()` and calling it at the top of each tool handler.

## How MCP Auth works

1. An MCP client (e.g. Claude Desktop, Cursor) discovers OAuth metadata from `/.well-known/oauth-authorization-server` when trying to connect to your MCP Server.
2. The client registers dynamically (via CIMD or DCR) to the authorization server and redirects the user to Descope's login / consent flow.
3. After login, Descope issues a signed JWT. The client includes this as a Bearer token on every MCP request.
4. `DescopeProvider` validates the JWT using Descope's JWKS endpoint before any tool is called.
5. Inside the tool, `validate_token()` parses the claims and `require_scopes()` checks that `mcp:greet` is present, returning an error to the client if not.

## Learn more

- [Render Blueprints](https://render.com/docs/infrastructure-as-code)
- [MCP Authorization](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization)
- [FastMCP](https://github.com/prefecthq/fastmcp)
- [Descope Agentic Identity Hub docs](docs.descope.com/agentic-identity-hub)
- [Descope MCP SDK](https://docs.descope.com/mcp/python-sdk)
