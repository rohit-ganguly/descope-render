# MCP Server Template with Descope Auth (Python)

A simple FastMCP server template for [Render](https://render.com), with full MCP authentication by [Descope](https://descope.com)

## What's included

- A working MCP server using the [FastMCP](https://gofastmcp.com/getting-started/welcome) with Streamable HTTP transport
- Full MCP Authorization Support with FastMCP's `DescopeProvider` and the `descope-mcp` SDK
- One example tool (`hello`) that returns `"Hello, world!"` and enforces the `mcp:greet` scope
- A `render.yaml` Blueprint for one-click deployment

> **Note:** This template deploys on the free plan by default. Free services spin down after 15 minutes of inactivity, causing cold starts of 30-60 seconds on the next request. MCP clients may time out during this delay. For reliable use, upgrade to a [paid plan](https://render.com/pricing) in the Render Dashboard — the Starter plan keeps your service running continuously.

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- A [Descope](https://www.descope.com) account and project

## Descope setup

1. Log in to the [Descope Console](https://app.descope.com).
2. Navigate to **Agentic Identity Hub → MCP Servers**.
3. Click **Create MCP Server** and give it a name.
4. In **MCP Server URLs**, add `http://localhost:8000/mcp`.
5. Under **MCP Client Registration**, enable **Client ID Metadata Documents (CIMD)** and **Dynamic Client Registration (DCR)**.
6. Under **MCP Server Scopes**, add a scope named `mcp:greet`. 
7. Copy the **Well-Known URL** — it looks like:
   ```
   https://api.descope.com/v1/apps/agentic/.../.well-known/openid-configuration
   ```
   This is your `DESCOPE_CONFIG_URL`.

## Local development

Now that you've set up your MCP Authorization Server, you can develop locally.

```bash
# Install dependencies
uv sync

# Set required environment variables
export DESCOPE_CONFIG_URL="<your URL from Descope>"
export SERVER_URL="http://localhost:8000"

# Run the server
uv run server.py --transport http --port 8000
```

When you run this locally, your server exposes an HTTP MCP endpoint at `http://localhost:8000/mcp`.

## Deploying to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

1. Click **Deploy to Render** above (or push this repo to GitHub and import it as a Blueprint).
2. When prompted, set the environment variable:
   | Key | Value |
   |---|---|
   | `DESCOPE_CONFIG_URL` | Your Well-Known URL from the Descope Console |
3. Deploy. `SERVER_URL` is not required — Render's `RENDER_EXTERNAL_URL` is used automatically.
4. Once live, copy your Render service URL (e.g. `https://<your-project>.onrender.com`) and add it to **MCP Server URLs** in the Descope Console.

*You now have a remotely hosted MCP Server with the full auth spec supported!*

## Available tools

| Tool | Description | Required scope |
|---|---|---|
| `hello` | Returns `"Hello, world!"` | `mcp:greet` |

## How auth works

1. An MCP client (e.g. Claude Desktop, Cursor) discovers OAuth metadata from `/.well-known/oauth-authorization-server` when trying to connect to your MCP Server.
2. The client registers dynamically (via CIMD or DCR) to the authorization server and redirects the user to Descope's login / consent flow.
3. After login, Descope issues a signed JWT. The client includes this as a Bearer token on every MCP request.
4. `DescopeProvider` validates the JWT using Descope's JWKS endpoint before any tool is called.
5. Inside the tool, `validate_token()` parses the claims and `require_scopes()` checks that `mcp:greet` is present, returning an error to the client if not.