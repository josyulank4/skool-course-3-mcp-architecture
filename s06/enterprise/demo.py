"""s06 / enterprise — connecting MCP to enterprise systems.

Lesson mapping: Section 6, Lessons 22-26 (facade, DB/file wrappers, REST
wrappers, safety tiers, rate limits + the ticketing scenario).
What it does:
  1. in-memory sample DB behind curated, parameterized tools only
  2. file-store wrapper with root-bound path resolution (traversal refused)
  3. fake REST wrapper: pagination flattened, HTTP statuses -> error classes
  4. facade exposing domain tools only + a read/write safety register
  5. token-bucket rate limiter; the wrong-tax-rate ticket resolved across
     all three stores inside quota, with a cache doing real work
  Plus a small honest JSON-RPC 2.0 handler (initialize, tools/list, tools/call).
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

# ------------------------------------------------------------ sample DB
DB = {
    "customers": {
        1: {"id": 1, "name": "Northwind Traders", "account_id": "A-1"},
        2: {"id": 2, "name": "Contoso Retail", "account_id": "A-2"},
    },
    "invoices": {
        1001: {"id": 1001, "customer_id": 1, "net": 1000.0,
               "tax_key": "reduced", "tax_rate": 0.10, "total": 1100.0},
        1002: {"id": 1002, "customer_id": 2, "net": 500.0,
               "tax_key": "standard", "tax_rate": 0.20, "total": 600.0},
    },
    "tax_rates": {"standard": 0.20, "reduced": 0.10},
}

_db = copy.deepcopy(DB)


def reset_db() -> None:
    global _db
    _db = copy.deepcopy(DB)


def get_invoice(invoice_id) -> dict:
    """Curated read: exact id lookup only. Non-integer ids are refused."""
    if not isinstance(invoice_id, int) or isinstance(invoice_id, bool):
        raise ValueError(f"invoice id must be an integer, got {invoice_id!r}")
    if invoice_id not in _db["invoices"]:
        raise KeyError(f"no invoice {invoice_id}")
    return copy.deepcopy(_db["invoices"][invoice_id])


def find_customer(name_query: str) -> list[dict]:
    """Curated read: case-insensitive substring match on customer names.

    The query is data, never query language: an injection-shaped string
    simply matches no name and returns [].
    """
    q = str(name_query).lower()
    return [copy.deepcopy(c) for c in sorted(_db["customers"].values(),
                                              key=lambda c: c["id"])
            if q in c["name"].lower()]


def update_invoice_tax(invoice_id: int, tax_key: str) -> dict:
    """Write tool: re-price one invoice using a named rate from tax_rates."""
    invoice = get_invoice(invoice_id)
    if tax_key not in _db["tax_rates"]:
        raise KeyError(f"no tax rate {tax_key!r}")
    rate = _db["tax_rates"][tax_key]
    invoice["tax_key"] = tax_key
    invoice["tax_rate"] = rate
    invoice["total"] = round(invoice["net"] * (1 + rate), 2)
    _db["invoices"][invoice_id] = invoice
    return copy.deepcopy(invoice)


# ------------------------------------------------------------- file store
FILE_ROOT = Path("/srv/demo-files")
FILES = {
    "tax-policy.txt": "Standard rate applies to EU accounts unless a reduced-rate "
                      "certificate is on file.",
    "guides/billing.txt": "Correct the rate on the invoice, then resolve the ticket.",
}


def resolve_path(root, name: str) -> Path:
    """Resolve `name` under `root`, or raise ValueError.

    Absolute names and any '..' escape are refused: the resolved path
    must stay inside the resolved root.
    """
    root_path = Path(root).resolve()
    candidate = (root_path / name).resolve()
    if candidate != root_path and root_path not in candidate.parents:
        raise ValueError(f"path escapes root: {name!r}")
    return candidate


class FileStore:
    """Reads named documents, always through resolve_path."""

    def __init__(self, root=FILE_ROOT, files=None) -> None:
        self.root = Path(root)
        self.files = dict(FILES if files is None else files)

    def read_document(self, name: str) -> dict:
        path = resolve_path(self.root, name)  # raises on traversal
        if name not in self.files:
            raise KeyError(f"no document {name!r}")
        return {"name": name, "path": str(path), "text": self.files[name]}


# -------------------------------------------------------------- fake REST
# The fake upstream: accounts behind a paginated endpoint, 2 per page.
FAKE_ACCOUNT_PAGES = {
    1: [{"id": "A-1", "name": "Northwind Traders", "tax_region": "EU"},
        {"id": "A-2", "name": "Contoso Retail", "tax_region": "US"}],
    2: [{"id": "A-3", "name": "Fabrikam Parts", "tax_region": "EU"}],
}


class RestError(Exception):
    def __init__(self, status: int, error_class: str, category: str) -> None:
        super().__init__(f"HTTP {status}: {error_class} ({category})")
        self.status = status
        self.error_class = error_class
        self.category = category


def http_error_class(status: int) -> tuple[str, str]:
    """Map an HTTP status to (error class, category).

    404 -> ('not_found', 'caller-fixable'); 429 -> ('rate_limited',
    'retryable'); 5xx -> ('upstream_error', 'fatal'); other 4xx ->
    ('bad_request', 'caller-fixable').
    """
    if status == 404:
        return "not_found", "caller-fixable"
    if status == 429:
        return "rate_limited", "retryable"
    if 500 <= status <= 599:
        return "upstream_error", "fatal"
    if 400 <= status <= 499:
        return "bad_request", "caller-fixable"
    return "unknown", "fatal"


class FakeRestEndpoint:
    """Stands in for the upstream API: paginated GETs, scripted statuses."""

    def __init__(self, forced_status: dict | None = None) -> None:
        self.forced_status = dict(forced_status or {})

    def get(self, path: str, page: int = 1) -> tuple[int, dict]:
        if path in self.forced_status:
            return self.forced_status[path], {}
        if path == "/accounts":
            if page not in FAKE_ACCOUNT_PAGES:
                return 404, {}
            last = max(FAKE_ACCOUNT_PAGES)
            return 200, {"data": copy.deepcopy(FAKE_ACCOUNT_PAGES[page]),
                         "next_page": page + 1 if page < last else None}
        if path.startswith("/accounts/"):
            wanted = path.rsplit("/", 1)[1]
            for rows in FAKE_ACCOUNT_PAGES.values():
                for row in rows:
                    if row["id"] == wanted:
                        return 200, {"data": copy.deepcopy(row)}
            return 404, {}
        return 404, {}


class RestWrapper:
    """Translates the fake API: pagination flattened, statuses classified."""

    def __init__(self, endpoint: FakeRestEndpoint | None = None) -> None:
        self.endpoint = endpoint or FakeRestEndpoint()

    def _get(self, path: str, page: int = 1) -> dict:
        status, payload = self.endpoint.get(path, page=page)
        if status != 200:
            error_class, category = http_error_class(status)
            raise RestError(status, error_class, category)
        return payload

    def list_accounts(self) -> list[dict]:
        accounts, page = [], 1
        while page is not None:
            payload = self._get("/accounts", page=page)
            accounts.extend(payload["data"])
            page = payload["next_page"]
        return accounts

    def get_account(self, account_id: str) -> dict:
        return self._get(f"/accounts/{account_id}")["data"]


# ---------------------------------------------------------------- facade
class EnterpriseFacade:
    """Domain tools only: no table names, no endpoints, no file paths."""

    def __init__(self, file_store: FileStore | None = None,
                 rest: RestWrapper | None = None) -> None:
        self.file_store = file_store or FileStore()
        self.rest = rest or RestWrapper()

    def tool_names(self) -> list[str]:
        return ["find_customer", "get_account", "get_invoice",
                "list_accounts", "read_document"]

    def get_invoice(self, invoice_id) -> dict:
        return get_invoice(invoice_id)

    def find_customer(self, name_query: str) -> list[dict]:
        return find_customer(name_query)

    def get_account(self, account_id: str) -> dict:
        return self.rest.get_account(account_id)

    def list_accounts(self) -> list[dict]:
        return self.rest.list_accounts()

    def read_document(self, name: str) -> dict:
        return self.file_store.read_document(name)


FACADE = EnterpriseFacade()

# ----------------------------------------------------------- safety tiers
TOOL_TIERS = {
    "get_invoice": "read",
    "find_customer": "read",
    "list_accounts": "read",
    "get_account": "read",
    "read_document": "read",
    "update_invoice_tax": "write",
    "update_ticket_status": "write",
    "issue_refund": "write",
}

_CREDENTIAL_SCOPES = {
    "get_invoice": "billing-db:read",
    "find_customer": "crm-db:read",
    "list_accounts": "accounts-api:read",
    "get_account": "accounts-api:read",
    "read_document": "file-store:read",
    "update_invoice_tax": "billing-db:write",
    "update_ticket_status": "ticketing:write",
    "issue_refund": "payments:write",
}


def tier_tool(name: str) -> str:
    """tier_tool('get_invoice') -> 'read'; unknown names raise KeyError."""
    if name not in TOOL_TIERS:
        raise KeyError(f"unknown tool: {name}")
    return TOOL_TIERS[name]


def safety_register() -> list[dict]:
    """One dict per tool, in TOOL_TIERS order: tool, tier,
    credential_scope, approval_required (True for every write)."""
    return [{"tool": name, "tier": tier,
             "credential_scope": _CREDENTIAL_SCOPES[name],
             "approval_required": tier == "write"}
            for name, tier in TOOL_TIERS.items()]


# ------------------------------------------------------------ rate limits
class TokenBucket:
    """Deterministic limiter: starts full, tick() refills up to capacity."""

    def __init__(self, capacity: int, refill_per_tick: int) -> None:
        self.capacity = capacity
        self.refill_per_tick = refill_per_tick
        self.tokens = capacity

    def consume(self, n: int = 1) -> bool:
        if n > self.tokens:
            return False
        self.tokens -= n
        return True

    def tick(self, n: int = 1) -> None:
        self.tokens = min(self.capacity, self.tokens + self.refill_per_tick * n)


def run_ticketing_scenario(quota: int = 6) -> dict:
    """Resolve the wrong-tax-rate ticket across DB + file store + REST.

    Each uncached upstream read costs 1 quota; the second invoice read is
    a cache hit and costs 0. Returns a dict with steps, quota_used (== 3)
    and quota (== 6 by default), so quota_used <= quota.
    """
    reset_db()
    bucket = TokenBucket(capacity=quota, refill_per_tick=1)
    facade = EnterpriseFacade()
    cache: dict = {}
    steps: list[str] = []
    spent = 0

    def spend(label: str) -> None:
        nonlocal spent
        if not bucket.consume(1):
            raise RuntimeError(f"quota exhausted before: {label}")
        spent += 1
        steps.append(label)

    invoice = facade.get_invoice(1001)
    spend("db: read invoice 1001 (tax_key='reduced', total 1100.0)")
    cache[1001] = invoice

    again = cache[1001]  # cache hit: same object the first read produced
    steps.append("cache: invoice 1001 hit (0 quota)")
    assert again["id"] == 1001

    policy = facade.read_document("tax-policy.txt")
    spend("files: read tax-policy.txt")
    assert "Standard rate" in policy["text"]

    account = facade.get_account("A-1")
    spend("rest: read account A-1 (tax_region EU)")
    assert account["tax_region"] == "EU"

    # The fix itself is local computation on data already fetched: the EU
    # account with no reduced-rate certificate belongs on 'standard'.
    fixed = update_invoice_tax(1001, "standard")
    steps.append("fix: invoice 1001 tax_key reduced -> standard, total 1100.0 -> 1200.0")

    return {"ticket_id": "T-501", "status": "resolved",
            "invoice_id": 1001, "account_id": account["id"],
            "correct_tax_key": fixed["tax_key"],
            "correct_tax_rate": fixed["tax_rate"],
            "correct_total": fixed["total"],
            "steps": steps, "quota_used": spent, "quota": quota}


# --------------------------------------------------------- JSON-RPC 2.0
_FACADE_CALLS = {
    "get_invoice": lambda a: FACADE.get_invoice(a["invoice_id"]),
    "find_customer": lambda a: FACADE.find_customer(a["name_query"]),
    "get_account": lambda a: FACADE.get_account(a["account_id"]),
    "list_accounts": lambda a: FACADE.list_accounts(),
    "read_document": lambda a: FACADE.read_document(a["name"]),
}


def handle_message(msg: dict) -> dict:
    """One JSON-RPC 2.0 request dict -> one response dict."""
    method = msg.get("method")
    params = msg.get("params") or {}
    req_id = msg.get("id", 1)

    def ok(result):
        return {"jsonrpc": "2.0", "id": req_id, "result": result}

    def err(code, message):
        return {"jsonrpc": "2.0", "id": req_id,
                "error": {"code": code, "message": message}}

    try:
        if method == "initialize":
            return ok({"protocolVersion": "2025-06-18",
                       "capabilities": {"tools": {}},
                       "serverInfo": {"name": "enterprise-demo", "version": "1.0.0"}})
        if method == "tools/list":
            return ok({"tools": [{"name": n, "tier": tier_tool(n)}
                                 for n in FACADE.tool_names()]})
        if method == "tools/call":
            result = _FACADE_CALLS[params["name"]](params.get("arguments", {}))
            return ok({"content": [{"type": "text",
                                    "text": json.dumps(result, sort_keys=True)}],
                       "isError": False})
        return err(-32601, f"method not found: {method}")
    except (KeyError, ValueError) as exc:
        return err(-32602, str(exc))


def main() -> None:
    reset_db()
    print("enterprise: curated DB tools (parameterized access only)")
    print(f"  find_customer('northwind') -> {[c['name'] for c in find_customer('northwind')]}")
    injection = find_customer("' OR 1=1 --")
    print(f"  injection-shaped query -> {injection} (treated as data, no rows)")
    assert injection == []
    try:
        get_invoice("1001 OR 1=1")  # type: ignore[arg-type]
        raise AssertionError("string invoice id was not refused")
    except ValueError:
        print("  string invoice id refused (integer ids only)")

    print("enterprise: file store (root-bound)")
    try:
        resolve_path(FILE_ROOT, "../secret.txt")
        raise AssertionError("traversal was not refused")
    except ValueError:
        print("  traversal '../secret.txt' refused")
    doc = FileStore().read_document("tax-policy.txt")
    print(f"  read_document('tax-policy.txt') -> {doc['path']}")
    assert doc["path"] == "/srv/demo-files/tax-policy.txt"

    print("enterprise: REST wrapper (pagination + error classes)")
    wrapper = RestWrapper()
    accounts = wrapper.list_accounts()
    print(f"  list_accounts -> {[a['id'] for a in accounts]} across 2 pages")
    assert [a["id"] for a in accounts] == ["A-1", "A-2", "A-3"]
    for status in (404, 429, 500):
        print(f"  HTTP {status} -> {http_error_class(status)}")
    assert http_error_class(404) == ("not_found", "caller-fixable")
    assert http_error_class(429) == ("rate_limited", "retryable")
    assert http_error_class(500) == ("upstream_error", "fatal")
    try:
        wrapper.get_account("A-99")
        raise AssertionError("missing account was not an error")
    except RestError as exc:
        print(f"  get_account('A-99') -> RestError {exc.error_class} ({exc.category})")
        assert exc.error_class == "not_found"

    print(f"facade tools (domain only): {FACADE.tool_names()}")
    register = safety_register()
    print(f"safety register: {len(register)} tools, "
          f"{sum(1 for r in register if r['tier'] == 'write')} write-tier")
    assert tier_tool("get_invoice") == "read"
    assert tier_tool("issue_refund") == "write"
    assert all(r["approval_required"] for r in register if r["tier"] == "write")

    bucket = TokenBucket(capacity=3, refill_per_tick=1)
    assert [bucket.consume(), bucket.consume(), bucket.consume(), bucket.consume()] == \
        [True, True, True, False]
    bucket.tick()
    assert bucket.consume() is True

    result = run_ticketing_scenario()
    print("ticketing scenario (wrong tax rate, 3 stores, cached):")
    for step in result["steps"]:
        print(f"  - {step}")
    print(f"  quota used {result['quota_used']}/{result['quota']}; "
          f"invoice 1001 total corrected to {result['correct_total']}")
    assert result["status"] == "resolved"
    assert result["quota_used"] == 3 and result["quota_used"] <= result["quota"]
    assert result["correct_tax_rate"] == 0.20 and result["correct_total"] == 1200.0

    print("enterprise demo: OK")


if __name__ == "__main__":
    main()
