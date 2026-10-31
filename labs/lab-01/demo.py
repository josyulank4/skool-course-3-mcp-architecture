"""s01 / hello_mcp — minimal MCP server + client, capability audit, N x M counter.

Lesson mapping: Section 1, Lessons 1-4.
What it does:
  1. In-process JSON-RPC 2.0: initialize handshake, tools/list, tools/call
  2. Tools that actually compute: add, word_count
  3. capability_audit: which perceive/change needs exist as tools today
  4. nxm_counts: bespoke N*M vs standard N+M integrations
"""

from __future__ import annotations
import json
PROTOCOL_VERSION = "2025-03-26"

SERVER_INFO = {"name": "hello-mcp", "version": "1.0.0"}

TOOL_DEFS = [
    {
        "name": "add",
        "description": "Add two numbers and return their sum.",
        "inputSchema": {
            "type": "object",
            "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
            "required": ["a", "b"],
        },
    },
    {
        "name": "word_count",
        "description": "Count the whitespace-separated words in a text string.",
        "inputSchema": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    },
]

def make_request(req_id, method, params=None):
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

def make_result(req_id, result):
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

def make_error(req_id, code, message):
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

def _tool_add(args):
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

def _tool_word_count(args):
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

_TOOL_HANDLERS = {"add": _tool_add, "word_count": _tool_word_count}

class HelloMCPServer:
    """Minimal MCP server speaking JSON-RPC 2.0 dicts in-process."""
    def __init__(self):
        """TODO — implement this function.
        Watch the lab video: this function is built step by step,
        then diff your version against the lab finish tag."""
        raise NotImplementedError("your turn — see the lab video")

    def handle(self, request):
        """TODO — implement this function.
        Watch the lab video: this function is built step by step,
        then diff your version against the lab finish tag."""
        raise NotImplementedError("your turn — see the lab video")

    def initialize(self, params=None):
        """TODO — implement this function.
        Watch the lab video: this function is built step by step,
        then diff your version against the lab finish tag."""
        raise NotImplementedError("your turn — see the lab video")

    def list_tools(self):
        """TODO — implement this function.
        Watch the lab video: this function is built step by step,
        then diff your version against the lab finish tag."""
        raise NotImplementedError("your turn — see the lab video")

    def call_tool(self, name, args):
        """TODO — implement this function.
        Watch the lab video: this function is built step by step,
        then diff your version against the lab finish tag."""
        raise NotImplementedError("your turn — see the lab video")

    def _call_tool(self, req_id, params):
        """TODO — implement this function.
        Watch the lab video: this function is built step by step,
        then diff your version against the lab finish tag."""
        raise NotImplementedError("your turn — see the lab video")


class HelloMCPClient:
    """In-process MCP client: initialize handshake, tools/list, tools/call."""
    def __init__(self, server=None):
        """TODO — implement this function.
        Watch the lab video: this function is built step by step,
        then diff your version against the lab finish tag."""
        raise NotImplementedError("your turn — see the lab video")

    def _send(self, method, params=None):
        """TODO — implement this function.
        Watch the lab video: this function is built step by step,
        then diff your version against the lab finish tag."""
        raise NotImplementedError("your turn — see the lab video")

    def initialize(self):
        """TODO — implement this function.
        Watch the lab video: this function is built step by step,
        then diff your version against the lab finish tag."""
        raise NotImplementedError("your turn — see the lab video")

    def list_tools(self):
        """TODO — implement this function.
        Watch the lab video: this function is built step by step,
        then diff your version against the lab finish tag."""
        raise NotImplementedError("your turn — see the lab video")

    def call_tool(self, name, args):
        """TODO — implement this function.
        Watch the lab video: this function is built step by step,
        then diff your version against the lab finish tag."""
        raise NotImplementedError("your turn — see the lab video")


def capability_audit(use_case):
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

def nxm_counts(n_apps, m_tools):
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

USE_CASE_FIXTURE = {
    "perceive": ["read_invoice", "read_account"],
    "change": ["file_report", "update_ticket"],
    "available_tools": ["read_invoice", "update_ticket"],
}

def main():
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

if __name__ == "__main__":
    main()
