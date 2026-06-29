# wisemcp

MCP server that wraps the [Wise API](https://docs.wise.com/api-reference) so you can query your account data directly from Claude.

## Tools

| Tool | Description |
|------|-------------|
| `get_profile` | Fetch the profile associated with the token (name, type, ID) |
| `get_balances` | List all balances with currency and current amount |
| `get_transactions` | Fetch transactions — optional filters: `currency`, `since`, `until`, `limit` |
| `get_statement` | Get a compact statement for a currency over a date range |

All responses include the `WISE_ACCOUNT_LABEL` so it's always clear which account the data belongs to.

## Setup

### 1. Install dependencies

```bash
pip install mcp httpx
```

### 2. Smoke-test your token

```bash
curl -s -H "Authorization: Bearer $WISE_API_TOKEN" https://api.wise.com/v1/profiles | python3 -m json.tool
```

Or with Python:

```python
import os, httpx, json
r = httpx.get("https://api.wise.com/v1/profiles", headers={"Authorization": f"Bearer {os.environ['WISE_API_TOKEN']}"})
print(json.dumps(r.json(), indent=2))
```

### 3. Register in `claude_desktop_config.json`

Merge the contents of `claude_desktop_config_snippet.json` into your config, updating the `args` path and tokens:

```json
"wise-personal": {
  "command": "python",
  "args": ["/path/to/wise_mcp.py"],
  "env": {
    "WISE_API_TOKEN": "token_A",
    "WISE_ACCOUNT_LABEL": "Personal"
  }
},
"wise-business": {
  "command": "python",
  "args": ["/path/to/wise_mcp.py"],
  "env": {
    "WISE_API_TOKEN": "token_B",
    "WISE_ACCOUNT_LABEL": "Business"
  }
}
```

## Environment variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `WISE_API_TOKEN` | Yes | — | Your Wise API token |
| `WISE_ACCOUNT_LABEL` | No | `"Wise"` | Label shown in all responses (e.g. `"Personal"` or `"Business"`) |
