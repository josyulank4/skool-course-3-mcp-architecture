"""s04 / first_server — build your first MCP server and survive its mistakes.

Lesson mapping: Section 4, Lessons 13-17.
What it does:
  1. build_server(): metadata + declared capabilities, initialize echoes them
  2. check_declaration(): declared vs implemented handler mismatches
  3. word_count tool with validate_args(): structured, never-raising errors
  4. handshake_lab(): full vs stripped client capabilities, diffed
  5. find_mistakes(): the 5 planted first-server mistakes, then 0 when fixed
"""

from __future__ import annotations
import json
PROTOCOL_VERSION = "2025-03-26"

SUPPORTED_VERSIONS = ["2024-11-05", "2025-03-26", "2025-06-18"]

WORD_COUNT_SCHEMA = {
    "type": "object",
    "properties": {
        "text": {"type": "string", "maxLength": 1000},
        "locale": {"type": "string", "maxLength": 20},
    },
    "required": ["text"],
}

WORD_COUNT_DEF = {
    "name": "word_count",
    "description": "Count words in text. For models: pass 'text' (string, max 1000 chars); returns the count.",
    "inputSchema": WORD_COUNT_SCHEMA,
}

_TYPE_CHECKS = {
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: (isinstance(v, (int, float)) and not isinstance(v, bool)),
    "boolean": lambda v: isinstance(v, bool),
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
}

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

def validate_args(schema, args):
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

def _word_count_handler(args):
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

def _resources_handler():
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

def _prompts_handler():
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

_CAPABILITY_HANDLERS = {
    "tools": {"word_count": _word_count_handler},
    "resources": {"list": _resources_handler},
    "prompts": {"list": _prompts_handler},
    "logging": {"setLevel": lambda args: {}},
}

class FirstServer:
    """A first MCP server: metadata, declared caps, implemented handlers."""
    def __init__(self, metadata, capabilities, implemented=None):
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

    def handle(self, request):
        """TODO — implement this function.
        Watch the lab video: this function is built step by step,
        then diff your version against the lab finish tag."""
        raise NotImplementedError("your turn — see the lab video")


def build_server(metadata, capabilities, implemented=None):
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

def check_declaration(server):
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

DEMO_METADATA = {"name": "first-server", "version": "0.1.0",
                 "description": "A first MCP server built to the Section 4 spec."}

OVER_DECLARING_SERVER = build_server(
    DEMO_METADATA, {"tools": {}, "resources": {}}, implemented=["tools"])

CORRECTED_SERVER = build_server(DEMO_METADATA, {"tools": {}, "resources": {}})

def negotiate(client_caps, server_caps=None):
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

def handshake_lab(full_caps, stripped_caps, server_caps=None):
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

FULL_CAPS = {
    "protocol_versions": ["2025-03-26", "2025-06-18"],
    "capabilities": {"sampling": {}, "roots": {}, "tools": {}, "resources": {}},
}

STRIPPED_CAPS = {
    "protocol_versions": ["2025-03-26"],
    "capabilities": {"tools": {}},
}

ADVERSARIAL_ARGS = [
    {},                                        # missing required field
    {"text": 123},                             # wrong type
    {"text": "x" * 5000},                      # extra-long string (> maxLength 1000)
    {"text": "valid words here"},              # valid control case
    None,                                      # not even an object
]

MISTAKE_IDS = [
    "stdout_printing",
    "unimplemented_capability",
    "human_only_description",
    "accept_anything_schema",
    "raw_exception_leak",
]

def find_mistakes(server_config):
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

BROKEN_CONFIG = {
    "name": "first-server",
    "stdout_printing": True,
    "declared_capabilities": ["tools", "resources"],
    "implemented_capabilities": ["tools"],
    "human_only_description": True,
    "description_audience": "human_only",
    "tools": [{"name": "word_count", "inputSchema": {"type": "object"}}],
    "error_handling": "raw_exception",
    "raw_exception_leak": True,
    "accept_anything_schema": True,
}

FIXED_CONFIG = {
    "name": "first-server",
    "stdout_printing": False,
    "declared_capabilities": ["tools", "resources"],
    "implemented_capabilities": ["tools", "resources"],
    "human_only_description": False,
    "description_audience": "model",
    "tools": [{"name": "word_count", "inputSchema": WORD_COUNT_SCHEMA}],
    "error_handling": "structured",
    "raw_exception_leak": False,
    "accept_anything_schema": False,
}

def main():
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

if __name__ == "__main__":
    main()
