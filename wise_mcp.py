import os
import httpx
from mcp.server.fastmcp import FastMCP

WISE_API_TOKEN = os.environ.get("WISE_API_TOKEN", "")
WISE_ACCOUNT_LABEL = os.environ.get("WISE_ACCOUNT_LABEL", "Wise")
BASE_URL = "https://api.wise.com"

mcp = FastMCP("wise")


def _headers() -> dict:
    return {"Authorization": f"Bearer {WISE_API_TOKEN}"}


def _get(path: str, params: dict | None = None) -> dict | list:
    url = BASE_URL + path
    response = httpx.get(url, headers=_headers(), params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def _profile_id() -> int:
    profiles = _get("/v1/profiles")
    # Return the first profile's id
    return profiles[0]["id"]


@mcp.tool()
def get_profile() -> dict:
    """Fetch the profile associated with the API token (name, type, ID)."""
    profiles = _get("/v1/profiles")
    return {
        "account": WISE_ACCOUNT_LABEL,
        "profiles": profiles,
    }


@mcp.tool()
def get_balances() -> dict:
    """List all balances with currency and current amount."""
    profile_id = _profile_id()
    accounts = _get("/v2/borderless-accounts", params={"profileId": profile_id})
    return {
        "account": WISE_ACCOUNT_LABEL,
        "balances": accounts,
    }


@mcp.tool()
def get_transactions(
    currency: str | None = None,
    since: str | None = None,
    until: str | None = None,
    limit: int | None = None,
) -> dict:
    """Fetch transactions with optional filters.

    Args:
        currency: ISO 4217 currency code (e.g. "USD").
        since: ISO date string for the start of the range (e.g. "2024-01-01").
        until: ISO date string for the end of the range (e.g. "2024-12-31").
        limit: Maximum number of transactions to return.
    """
    profile_id = _profile_id()
    params: dict = {}
    if currency:
        params["currency"] = currency
    if since:
        params["intervalStart"] = since
    if until:
        params["intervalEnd"] = until
    if limit:
        params["limit"] = limit

    transactions = _get(f"/v1/profiles/{profile_id}/balance-movements", params=params)
    return {
        "account": WISE_ACCOUNT_LABEL,
        "transactions": transactions,
    }


@mcp.tool()
def get_statement(currency: str, start: str, end: str) -> dict:
    """Get a statement for a specific currency over a date range.

    Args:
        currency: ISO 4217 currency code (e.g. "EUR").
        start: ISO date string for the start of the range (e.g. "2024-01-01").
        end: ISO date string for the end of the range (e.g. "2024-12-31").
    """
    profile_id = _profile_id()

    # Fetch balances to find the balance ID for the given currency
    accounts = _get("/v2/borderless-accounts", params={"profileId": profile_id})
    balance_id = None
    for account in accounts:
        for balance in account.get("balances", []):
            if balance.get("currency") == currency:
                balance_id = balance.get("id")
                break
        if balance_id:
            break

    if balance_id is None:
        return {
            "account": WISE_ACCOUNT_LABEL,
            "error": f"No balance found for currency {currency}",
        }

    params = {
        "currency": currency,
        "intervalStart": start,
        "intervalEnd": end,
        "type": "COMPACT",
    }
    statement = _get(
        f"/v3/profiles/{profile_id}/balances/{balance_id}/statement", params=params
    )
    return {
        "account": WISE_ACCOUNT_LABEL,
        "statement": statement,
    }


if __name__ == "__main__":
    mcp.run()
