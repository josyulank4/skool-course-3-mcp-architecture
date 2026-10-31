"""s08 / orchestration — multi-server orchestration.

Lesson mapping: Section 8, Lessons 32-35 (discovery, namespacing,
composing workflows, failure isolation).
What it does:
  1. three mini servers (ticketing, accounts, billing) in a Registry;
     discover() reports what a host knows before the first call
  2. both ticketing and accounts expose 'search': a bare call is
     ambiguous and raises; namespace() prefixes tools as 'server.tool'
     and both become callable side by side
  3. compose_workflow resolves the sample ticket across all three
     servers; with fail_at_step=4 the billing write is compensated
     and the state is rolled back
  4. failure isolation: killing billing degrades the agent (ticketing
     still readable, billing reported unavailable) and restarting it
     recovers full capability
  Plus a small JSON-RPC handler: initialize + tools/list (namespaced).
"""

from __future__ import annotations

import copy
import json


class AmbiguousToolError(ValueError):
    """A bare tool name owned by more than one server."""


class ServerUnavailableError(RuntimeError):
    """The owning server is down."""


# ------------------------------------------------------------ mini servers
class TicketingServer:
    name = "ticketing"

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.tickets = {
            501: {"id": 501, "account_id": "A-1", "billing_id": "B-1",
                  "issue": "Billing charged the wrong tax rate", "status": "open"},
            502: {"id": 502, "account_id": "A-2", "billing_id": "B-2",
                  "issue": "Login fails after SSO change", "status": "open"},
        }

    def read_ticket(self, ticket_id: int) -> dict:
        return copy.deepcopy(self.tickets[ticket_id])

    def update_ticket(self, ticket_id: int, status: str) -> dict:
        self.tickets[ticket_id]["status"] = status
        return copy.deepcopy(self.tickets[ticket_id])

    def search(self, query: str) -> list[dict]:
        q = query.lower()
        return [copy.deepcopy(t) for t in sorted(self.tickets.values(),
                                                 key=lambda t: t["id"])
                if q in t["issue"].lower()]

    @property
    def tools(self) -> dict:
        return {"read_ticket": self.read_ticket,
                "update_ticket": self.update_ticket,
                "search": self.search}


class AccountsServer:
    name = "accounts"

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.accounts = {
            "A-1": {"id": "A-1", "name": "Northwind Traders", "billing_id": "B-1",
                    "tax_region": "EU"},
            "A-2": {"id": "A-2", "name": "Contoso Retail", "billing_id": "B-2",
                    "tax_region": "US"},
        }

    def read_account(self, account_id: str) -> dict:
        return copy.deepcopy(self.accounts[account_id])

    def search(self, query: str) -> list[dict]:
        q = query.lower()
        return [copy.deepcopy(a) for a in sorted(self.accounts.values(),
                                                 key=lambda a: a["id"])
                if q in a["name"].lower()]

    @property
    def tools(self) -> dict:
        return {"read_account": self.read_account, "search": self.search}


class BillingServer:
    name = "billing"

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.configs = {
            "B-1": {"id": "B-1", "account_id": "A-1", "tax_rate": 0.10,
                    "correct_tax_rate": 0.20},
            "B-2": {"id": "B-2", "account_id": "A-2", "tax_rate": 0.20,
                    "correct_tax_rate": 0.20},
        }

    def read_billing(self, billing_id: str) -> dict:
        return copy.deepcopy(self.configs[billing_id])

    def set_tax_rate(self, billing_id: str, tax_rate: float) -> dict:
        self.configs[billing_id]["tax_rate"] = tax_rate
        return copy.deepcopy(self.configs[billing_id])

    @property
    def tools(self) -> dict:
        return {"read_billing": self.read_billing, "set_tax_rate": self.set_tax_rate}


def build_servers() -> dict:
    """Fresh fixture servers: {'ticketing': ..., 'accounts': ..., 'billing': ...}."""
    return {"ticketing": TicketingServer(),
            "accounts": AccountsServer(),
            "billing": BillingServer()}


# ---------------------------------------------------------------- registry
class Registry:
    """What exists and what it offers, known before any call is made."""

    def __init__(self) -> None:
        self._servers: dict[str, object] = {}

    def register(self, name: str, server) -> None:
        self._servers[name] = server

    def get(self, name: str):
        return self._servers[name]

    def names(self) -> list[str]:
        return sorted(self._servers)

    def discover(self) -> dict:
        """-> {server_name: sorted tool-name list} for every registered server."""
        return {name: sorted(server.tools)
                for name, server in sorted(self._servers.items())}


# -------------------------------------------------------------------- host
class Host:
    """Routes calls to servers. Routing is mechanical: bare names must be
    unique, namespaced names are 'server.tool'."""

    def __init__(self, servers: dict | None = None) -> None:
        self.servers = dict(servers or build_servers())
        self.registry = Registry()
        for name, server in self.servers.items():
            self.registry.register(name, server)
        self._down: set[str] = set()
        self._namespaced = False

    # -- discovery / namespacing -------------------------------------
    def discover(self) -> dict:
        return self.registry.discover()

    def namespace(self) -> dict:
        """Prefix every tool as 'server.tool'.

        Returns {namespaced_name: (server_name, tool_name)} covering all
        registered tools, and marks the host namespaced.
        """
        mapping = {}
        for server_name, tools in self.registry.discover().items():
            for tool in tools:
                mapping[f"{server_name}.{tool}"] = (server_name, tool)
        self._namespaced = True
        return mapping

    # -- calling ------------------------------------------------------
    def host_call(self, name: str, **args):
        """Call a tool by namespaced name ('billing.set_tax_rate') or by a
        unique bare name ('read_ticket').

        A bare name owned by two servers (both expose 'search') raises
        AmbiguousToolError; a call to a down server raises
        ServerUnavailableError; unknown names raise KeyError.
        """
        if "." in name:
            server_name, tool = name.split(".", 1)
            return self._dispatch(server_name, tool, args)
        owners = [s for s, srv in self.servers.items() if name in srv.tools]
        if len(owners) > 1:
            raise AmbiguousToolError(
                f"ambiguous tool {name!r}: owned by {sorted(owners)}; "
                "call it namespaced as 'server.tool'")
        if not owners:
            raise KeyError(f"no server exposes tool {name!r}")
        return self._dispatch(owners[0], name, args)

    # Spec-worded alias.
    def call(self, name: str, **args):
        return self.host_call(name, **args)

    def _dispatch(self, server_name: str, tool: str, args: dict):
        if server_name not in self.servers:
            raise KeyError(f"unknown server: {server_name}")
        if server_name in self._down:
            raise ServerUnavailableError(f"server unavailable: {server_name}")
        server = self.servers[server_name]
        if tool not in server.tools:
            raise KeyError(f"server {server_name} has no tool {tool!r}")
        return server.tools[tool](**args)

    # -- failure isolation -------------------------------------------
    def kill_server(self, name: str) -> None:
        if name not in self.servers:
            raise KeyError(f"unknown server: {name}")
        self._down.add(name)

    def restart_server(self, name: str) -> None:
        if name not in self.servers:
            raise KeyError(f"unknown server: {name}")
        self._down.discard(name)

    def agent_status(self) -> dict:
        """-> {'overall': 'ok'|'degraded', 'servers': {name: 'up'|'down'},
        'available_capabilities': sorted namespaced tools of up servers,
        'unavailable_capabilities': sorted namespaced tools of down ones}."""
        available, unavailable = [], []
        servers_status = {}
        for name, server in sorted(self.servers.items()):
            tools = [f"{name}.{tool}" for tool in sorted(server.tools)]
            if name in self._down:
                servers_status[name] = "down"
                unavailable.extend(tools)
            else:
                servers_status[name] = "up"
                available.extend(tools)
        return {"overall": "degraded" if self._down else "ok",
                "servers": servers_status,
                "available_capabilities": sorted(available),
                "unavailable_capabilities": sorted(unavailable)}

    # -- JSON-RPC ------------------------------------------------------
    def handle_message(self, msg: dict) -> dict:
        method = msg.get("method")
        req_id = msg.get("id", 1)

        def ok(result):
            return {"jsonrpc": "2.0", "id": req_id, "result": result}

        def err(code, message):
            return {"jsonrpc": "2.0", "id": req_id,
                    "error": {"code": code, "message": message}}

        if method == "initialize":
            return ok({"protocolVersion": "2025-06-18",
                       "capabilities": {"tools": {}},
                       "serverInfo": {"name": "orchestration-host",
                                      "version": "1.0.0"}})
        if method == "tools/list":
            return ok({"tools": [{"name": n} for n in sorted(self.namespace())]})
        return err(-32601, f"method not found: {method}")


def _as_host(servers) -> Host:
    """Accept a Host, a Registry, a {name: server} dict, or a server list."""
    if isinstance(servers, Host):
        return servers
    if isinstance(servers, Registry):
        return Host({name: servers.get(name) for name in servers.names()})
    if isinstance(servers, dict):
        return Host(servers)
    return Host({server.name: server for server in servers})


def compose_workflow(servers, fail_at_step: int | None = None) -> dict:
    """Resolve ticket 501 across ticketing -> accounts -> billing.

    Steps (numbered from 1):
      1. ticketing.read_ticket 501
      2. accounts.read_account for the ticket's account
      3. billing.read_billing for the account's billing config
      4. billing.set_tax_rate to the config's correct rate
      5. ticketing.update_ticket -> 'resolved'

    Server state is reset first, so runs are repeatable. fail_at_step=4
    injects a failure just after step 4's write: the workflow compensates
    (restores the previous tax rate) and returns status 'compensated'
    with final_tax_rate back at 0.10.
    """
    host = _as_host(servers)
    for server in host.servers.values():
        server.reset()
    steps: list[str] = []
    undo: list[tuple[str, object]] = []  # (label, restore callable)

    ticket = host.host_call("ticketing.read_ticket", ticket_id=501)
    steps.append("1. ticketing.read_ticket 501 -> wrong tax rate, account A-1")

    account = host.host_call("accounts.read_account", account_id=ticket["account_id"])
    steps.append(f"2. accounts.read_account {account['id']} -> billing {account['billing_id']}")

    billing = host.host_call("billing.read_billing", billing_id=account["billing_id"])
    steps.append(f"3. billing.read_billing {billing['id']} -> tax_rate "
                 f"{billing['tax_rate']} (correct {billing['correct_tax_rate']})")

    previous_rate = billing["tax_rate"]
    host.host_call("billing.set_tax_rate", billing_id=billing["id"],
                   tax_rate=billing["correct_tax_rate"])
    undo.append((f"billing.set_tax_rate {billing['id']}: "
                  f"{billing['correct_tax_rate']} -> {previous_rate}",
                 lambda: host.host_call("billing.set_tax_rate",
                                        billing_id=billing["id"],
                                        tax_rate=previous_rate)))
    steps.append(f"4. billing.set_tax_rate {billing['id']} -> {billing['correct_tax_rate']}")

    if fail_at_step == 4:
        compensated = []
        for label, restore in reversed(undo):
            restore()
            compensated.append(label)
            steps.append(f"compensate: {label}")
        final = host.host_call("billing.read_billing", billing_id=billing["id"])
        return {"status": "compensated", "ticket_id": 501,
                "account_id": account["id"], "billing_id": billing["id"],
                "steps": steps, "compensated_actions": compensated,
                "final_tax_rate": final["tax_rate"],
                "ticket_status": host.host_call("ticketing.read_ticket",
                                                ticket_id=501)["status"]}

    updated = host.host_call("ticketing.update_ticket", ticket_id=501, status="resolved")
    steps.append("5. ticketing.update_ticket 501 -> resolved")
    return {"status": "resolved", "ticket_id": 501,
            "account_id": account["id"], "billing_id": billing["id"],
            "steps": steps, "compensated_actions": [],
            "final_tax_rate": billing["correct_tax_rate"],
            "ticket_status": updated["status"]}


# ------------------------------------------- module-level default host
_default_host = Host()


def register(name: str, server) -> None:
    """Register a server on the module-level default host's registry."""
    _default_host.servers[name] = server
    _default_host.registry.register(name, server)


def discover() -> dict:
    return _default_host.discover()


def namespace() -> dict:
    return _default_host.namespace()


def host_call(name: str, **args):
    return _default_host.host_call(name, **args)


def kill_server(name: str) -> None:
    _default_host.kill_server(name)


def restart_server(name: str) -> None:
    _default_host.restart_server(name)


def agent_status() -> dict:
    return _default_host.agent_status()


def main() -> None:
    host = Host(build_servers())

    found = host.discover()
    print("orchestration: discovery before any call")
    for name, tools in found.items():
        print(f"  {name}: {tools}")
    assert found == {
        "accounts": ["read_account", "search"],
        "billing": ["read_billing", "set_tax_rate"],
        "ticketing": ["read_ticket", "search", "update_ticket"],
    }

    print("orchestration: name collision on 'search'")
    try:
        host.host_call("search", query="tax")
        raise AssertionError("bare 'search' was not ambiguous")
    except AmbiguousToolError as exc:
        print(f"  bare host_call('search') -> {exc}")
    mapping = host.namespace()
    tickets = host.host_call("ticketing.search", query="tax")
    accounts = host.host_call("accounts.search", query="northwind")
    print(f"  ticketing.search 'tax' -> tickets {[t['id'] for t in tickets]}")
    print(f"  accounts.search 'northwind' -> {[a['id'] for a in accounts]}")
    assert [t["id"] for t in tickets] == [501]
    assert [a["id"] for a in accounts] == ["A-1"]
    assert "ticketing.search" in mapping and "accounts.search" in mapping

    result = compose_workflow(host)
    print("orchestration: composed workflow across three servers")
    for step in result["steps"]:
        print(f"  {step}")
    print(f"  -> status {result['status']}, final tax rate {result['final_tax_rate']}")
    assert result["status"] == "resolved" and result["final_tax_rate"] == 0.20
    assert result["ticket_status"] == "resolved"

    failed = compose_workflow(host, fail_at_step=4)
    print("orchestration: failure at step 4 -> compensation")
    for step in failed["steps"]:
        print(f"  {step}")
    billing_now = host.host_call("billing.read_billing", billing_id="B-1")
    print(f"  -> status {failed['status']}, billing tax_rate rolled back to "
          f"{billing_now['tax_rate']}")
    assert failed["status"] == "compensated"
    assert failed["final_tax_rate"] == 0.10 and billing_now["tax_rate"] == 0.10
    assert failed["ticket_status"] == "open"

    print("orchestration: failure isolation")
    host.kill_server("billing")
    status = host.agent_status()
    print(f"  billing down -> overall {status['overall']}; "
          f"unavailable {status['unavailable_capabilities']}")
    assert status["overall"] == "degraded"
    assert "ticketing.read_ticket" in status["available_capabilities"]
    assert "billing.set_tax_rate" in status["unavailable_capabilities"]
    assert host.host_call("ticketing.read_ticket", ticket_id=501)["id"] == 501
    try:
        host.host_call("billing.read_billing", billing_id="B-1")
        raise AssertionError("down server accepted a call")
    except ServerUnavailableError:
        print("  billing call while down -> ServerUnavailableError; ticketing still reads")
    host.restart_server("billing")
    recovered = host.agent_status()
    print(f"  billing restarted -> overall {recovered['overall']}")
    assert recovered["overall"] == "ok" and recovered["unavailable_capabilities"] == []

    resp = host.handle_message({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    assert "billing.set_tax_rate" in [t["name"] for t in resp["result"]["tools"]]
    print(f"  JSON-RPC tools/list -> {len(resp['result']['tools'])} namespaced tools")

    print("orchestration demo: OK")


if __name__ == "__main__":
    main()
