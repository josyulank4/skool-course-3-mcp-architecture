"""s02 / fundamentals — discovery, three roles, primitive sorter, handshake.

Lesson mapping: Section 2, Lessons 5-8.
What it does:
  1. Sample server: 2 tools, 2 resources, 1 prompt over JSON-RPC 2.0
  2. discover(): list all three primitive sets exactly as a client sees them
  3. three_role_trace(): who owns each decision, host -> client -> server
  4. classify_primitive(): tool / resource / prompt by who decides
  5. handshake_capture(): negotiated intersection of client/server caps
"""

from __future__ import annotations
import json
SUPPORTED_VERSIONS = ["2024-11-05", "2025-03-26", "2025-06-18"]

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
        "name": "greet",
        "description": "Build a greeting string for a name.",
        "inputSchema": {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        },
    },
]

RESOURCE_DEFS = [
    {"uri": "notes://welcome", "name": "Welcome Notes", "mimeType": "text/plain"},
    {"uri": "data://server-config", "name": "Server Config", "mimeType": "application/json"},
]

RESOURCE_CONTENTS = {
    "notes://welcome": "Welcome to the fundamentals sample server.",
    "data://server-config": '{"region": "local", "mode": "demo"}',
}

PROMPT_DEFS = [
    {
        "name": "daily_brief",
        "description": "Build a daily briefing prompt for a topic.",
        "arguments": [{"name": "topic", "description": "Briefing topic", "required": True}],
    }
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

class FundamentalsServer:
    """Sample MCP server exposing 2 tools, 2 resources, and 1 prompt."""
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

    def _call_tool(self, req_id, params):
        """TODO — implement this function.
        Watch the lab video: this function is built step by step,
        then diff your version against the lab finish tag."""
        raise NotImplementedError("your turn — see the lab video")


class FundamentalsClient:
    """In-process MCP client used by discover() and the demo."""
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

    def request(self, method, params=None):
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

    def list_resources(self):
        """TODO — implement this function.
        Watch the lab video: this function is built step by step,
        then diff your version against the lab finish tag."""
        raise NotImplementedError("your turn — see the lab video")

    def list_prompts(self):
        """TODO — implement this function.
        Watch the lab video: this function is built step by step,
        then diff your version against the lab finish tag."""
        raise NotImplementedError("your turn — see the lab video")

    def call_tool(self, name, args):
        """TODO — implement this function.
        Watch the lab video: this function is built step by step,
        then diff your version against the lab finish tag."""
        raise NotImplementedError("your turn — see the lab video")


def discover(client):
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

def three_role_trace(request):
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

_WHO_TO_PRIMITIVE = {
    "model": "tool",
    "application": "resource",
    "app": "resource",
    "host": "resource",
    "user": "prompt",
}

def classify_primitive(capability):
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

def _caps_of(side):
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

def handshake_capture(client_caps, server_caps):
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

SAMPLE_CAPABILITIES = [
    {"name": "run_report", "who_decides": "model"},
    {"name": "account_record", "who_decides": "application"},
    {"name": "weekly_review_template", "who_decides": "user"},
]

CLIENT_CAPS_FIXTURE = {
    "protocol_versions": ["2024-11-05", "2025-03-26", "2025-06-18"],
    "capabilities": {"sampling": {}, "roots": {}, "tools": {}},
}

SERVER_CAPS_FIXTURE = {
    "protocol_versions": ["2025-03-26", "2025-06-18"],
    "capabilities": {"tools": {}, "resources": {}, "prompts": {}},
}

def main():
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

if __name__ == "__main__":
    main()
