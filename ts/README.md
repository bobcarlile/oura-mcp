# @proscar87/oura-mcp

The [Oura](https://ouraring.com) v2 API as an [MCP](https://modelcontextprotocol.io)
server, in TypeScript. The same build the one-click `.mcpb` ships.

It paginates to the end before answering, keeps every date range inclusive
(Oura's isn't, and `workout` filters in UTC), rejects `latest` where Oura would
silently return the whole collection, and reports fields it could not project.
Each of those is a way Oura under-delivers without saying so, measured against
the real API: see the [main README](https://github.com/proscar87/oura-mcp#readme).

## Try it on Oura's sample data

```
OURA_SANDBOX=1 npx -y @proscar87/oura-mcp --check
```

## Your own data

Oura retired personal access tokens in December 2025, so it's OAuth2: register
an application at
[cloud.ouraring.com/oauth/applications](https://cloud.ouraring.com/oauth/applications)
with the redirect `http://localhost:9876/callback/` (the trailing slash is
required), then once:

```
OURA_CLIENT_ID=… OURA_CLIENT_SECRET=… npx -y @proscar87/oura-mcp --authorize
```

And in your MCP client:

```json
{
  "mcpServers": {
    "oura": {
      "command": "npx",
      "args": ["-y", "@proscar87/oura-mcp"],
      "env": { "OURA_CLIENT_ID": "…", "OURA_CLIENT_SECRET": "…" }
    }
  }
}
```

The client ID and secret stay in the config because Oura's refresh needs them.

Documentation, privacy policy and examples:
[github.com/proscar87/oura-mcp](https://github.com/proscar87/oura-mcp).

MIT.
