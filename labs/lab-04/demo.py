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
    """Build a JSON-RPC 2.0 request dict with jsonrpc/id/method/params keys."""
    return {"jsonrpc": "2.0", "id": req_id, "method": method, "params": params or {}}


def make_result(req_id, result):
    """Build a JSON-RPC 2.0 success response dict for the given request id."""
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def make_error(req_id, code, message):
    """Build a JSON-RPC 2.0 error response dict with a structured error object."""
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


def validate_args(schema, args):
    """Validate args against a JSON-schema subset; return a list of error dicts.

    Each error is {"field": str|None, "code": str, "message": str} with codes
    not_an_object, missing_required, wrong_type, too_long, too_short,
    out_of_range, invalid_enum, unexpected_field. Returns [] when valid.
    Never raises, whatever args contains (None, wrong types, huge strings).
    """
    errors = []
    try:
        if not isinstance(schema, dict):
            return []
        if not isinstance(args, dict):
            return [{"field": None, "code": "not_an_object",
                     "message": "arguments must be an object"}]
        properties = schema.get("properties") or {}
        for field in schema.get("required") or []:
            if field not in args:
                errors.append({"field": field, "code": "missing_required",
                               "message": f"missing required field: {field}"})
        if schema.get("additionalProperties") is False:
            for field in args:
                if field not in properties:
                    errors.append({"field": field, "code": "unexpected_field",
                                   "message": f"unexpected field: {field}"})
        for field, value in args.items():
            spec = properties.get(field)
            if not isinstance(spec, dict):
                continue
            expected = spec.get("type")
            checker = _TYPE_CHECKS.get(expected)
            if checker is not None and not checker(value):
                errors.append({"field": field, "code": "wrong_type",
                               "message": f"field {field} must be of type {expected}"})
                continue
            if isinstance(value, str):
                max_len = spec.get("maxLength")
                if isinstance(max_len, int) and len(value) > max_len:
                    errors.append({"field": field, "code": "too_long",
                                   "message": f"field {field} exceeds maxLength {max_len}"})
                min_len = spec.get("minLength")
                if isinstance(min_len, int) and len(value) < min_len:
                    errors.append({"field": field, "code": "too_short",
                                   "message": f"field {field} is shorter than minLength {min_len}"})
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                if "minimum" in spec and value < spec["minimum"]:
                    errors.append({"field": field, "code": "out_of_range",
                                   "message": f"field {field} is below minimum {spec['minimum']}"})
                if "maximum" in spec and value > spec["maximum"]:
                    errors.append({"field": field, "code": "out_of_range",
                                   "message": f"field {field} is above maximum {spec['maximum']}"})
            if "enum" in spec and value not in spec["enum"]:
                errors.append({"field": field, "code": "invalid_enum",
                               "message": f"field {field} must be one of {spec['enum']}"})
    except Exception as exc:  # validation itself must never leak a raise
        return [{"field": None, "code": "validation_error",
                 "message": f"validation failed: {type(exc).__name__}"}]
    return errors


def _word_count_handler(args):
    text = args["text"]
    words = text.split() if text.strip() else []
    return {"count": len(words)}


def _resources_handler():
    return {"resources": []}


def _prompts_handler():
    return {"prompts": []}


_CAPABILITY_HANDLERS = {
    "tools": {"word_count": _word_count_handler},
    "resources": {"list": _resources_handler},
    "prompts": {"list": _prompts_handler},
    "logging": {"setLevel": lambda args: {}},
}


class FirstServer:
    """A first MCP server: metadata, declared caps, implemented handlers."""

    def __init__(self, metadata, capabilities, implemented=None):
        self.metadata = dict(metadata or {})
        self.capabilities = dict(capabilities or {})
        if implemented is None:
            self.implemented = sorted(self.capabilities.keys())
        else:
            self.implemented = sorted(implemented)
        self.handlers = {}
        for cap in self.implemented:
            if cap in _CAPABILITY_HANDLERS:
                self.handlers[cap] = _CAPABILITY_HANDLERS[cap]

    def initialize(self, params=None):
        """Return the initialize result dict echoing metadata and declared caps."""
        params = params or {}
        client_versions = params.get("protocolVersions") or [params.get("protocolVersion", PROTOCOL_VERSION)]
        common = [v for v in client_versions if v in SUPPORTED_VERSIONS]
        negotiated = sorted(common)[-1] if common else PROTOCOL_VERSION
        return {
            "protocolVersion": negotiated,
            "capabilities": dict(self.capabilities),
            "serverInfo": {
                "name": self.metadata.get("name", "first-server"),
                "version": self.metadata.get("version", "0.1.0"),
                "description": self.metadata.get("description", ""),
            },
        }

    def list_tools(self):
        """Return the tool definitions actually implemented ([] if tools not implemented)."""
        if "tools" not in self.handlers:
            return []
        return [dict(WORD_COUNT_DEF)]

    def call_tool(self, name, args):
        """Validate args, then run the tool; return (structured, errors) — errors non-empty means reject."""
        if name != "word_count" or "tools" not in self.handlers:
            return None, [{"field": None, "code": "unknown_tool",
                           "message": f"unknown tool: {name}"}]
        errors = validate_args(WORD_COUNT_SCHEMA, args)
        if errors:
            return None, errors
        return _word_count_handler(args), []

    def handle(self, request):
        """Dispatch one JSON-RPC request dict and return the response dict."""
        if not isinstance(request, dict) or request.get("jsonrpc") != "2.0":
            return make_error(None, -32600, "Invalid Request: jsonrpc must be '2.0'")
        method = request.get("method")
        req_id = request.get("id")
        params = request.get("params") or {}
        if method == "initialize":
            return make_result(req_id, self.initialize(params))
        if method == "tools/list":
            return make_result(req_id, {"tools": self.list_tools()})
        if method == "tools/call":
            structured, errors = self.call_tool(params.get("name"), params.get("arguments") or {})
            if errors:
                first = errors[0]
                return make_error(req_id, -32602, f"{first['code']}: {first['message']}")
            return make_result(req_id, {
                "content": [{"type": "text", "text": json.dumps(structured, sort_keys=True)}],
                "structured": structured, "isError": False})
        if method == "ping":
            return make_result(req_id, {})
        return make_error(req_id, -32601, f"Method not found: {method}")


def build_server(metadata, capabilities, implemented=None):
    """Build a FirstServer from metadata and declared capabilities.

    capabilities is a declaration dict like {"tools": {...}, "resources": {...}}.
    implemented lists the capability names that actually have handlers;
    when None (the honest default) every declared capability is implemented.
    Returns the FirstServer object.
    """
    return FirstServer(metadata, capabilities, implemented=implemented)


def check_declaration(server):
    """Return the sorted list of capability names declared but not implemented.

    Each entry is the capability name string (e.g. "resources"). An honest
    server returns []; the over-declaring fixture returns exactly ["resources"].
    """
    declared = set((server.capabilities or {}).keys())
    implemented = set(getattr(server, "implemented", []) or [])
    return sorted(declared - implemented)


DEMO_METADATA = {"name": "first-server", "version": "0.1.0",
                 "description": "A first MCP server built to the Section 4 spec."}

# Over-declaring fixture: advertises resources, implements only tools.
OVER_DECLARING_SERVER = build_server(
    DEMO_METADATA, {"tools": {}, "resources": {}}, implemented=["tools"])
CORRECTED_SERVER = build_server(DEMO_METADATA, {"tools": {}, "resources": {}})


def negotiate(client_caps, server_caps=None):
    """Negotiate one client cap dict against server caps; return the session dict.

    Inputs use {"protocol_versions": [...], "capabilities": {...} or [...]}.
    Returns {"protocol_version": highest common or None,
    "capabilities": sorted shared names, "client_capabilities": sorted,
    "server_capabilities": sorted}.
    """
    server_caps = server_caps if server_caps is not None else {
        "protocol_versions": list(SUPPORTED_VERSIONS),
        "capabilities": {"tools": {}, "resources": {}, "prompts": {}, "logging": {}},
    }
    client_versions = list((client_caps or {}).get("protocol_versions") or [])
    server_versions = list(server_caps.get("protocol_versions") or [])
    common = sorted(set(client_versions) & set(server_versions))
    client_names = set(((client_caps or {}).get("capabilities") or {}).keys()) \
        if isinstance((client_caps or {}).get("capabilities"), dict) \
        else set((client_caps or {}).get("capabilities") or [])
    server_raw = server_caps.get("capabilities") or {}
    server_names = set(server_raw.keys()) if isinstance(server_raw, dict) else set(server_raw)
    return {
        "protocol_version": common[-1] if common else None,
        "capabilities": sorted(client_names & server_names),
        "client_capabilities": sorted(client_names),
        "server_capabilities": sorted(server_names),
    }


def handshake_lab(full_caps, stripped_caps, server_caps=None):
    """Run the handshake twice and return {"full": negotiated, "stripped": negotiated}.

    full_caps / stripped_caps are client cap dicts in negotiate() format;
    each value is the negotiate() result dict for that client.
    """
    return {
        "full": negotiate(full_caps, server_caps),
        "stripped": negotiate(stripped_caps, server_caps),
    }


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
    """Return the planted first-server mistake ids present in server_config, in canonical order.

    Detection (any alias triggers the id):
      stdout_printing — stdout_printing/prints_to_stdout is true
      unimplemented_capability — declared_capabilities exceed implemented_capabilities
      human_only_description — human_only_description is true, or
        description_audience is "human"/"human_only"/"humans"
      accept_anything_schema — accept_anything_schema is true, or any tool's
        inputSchema has no "properties"
      raw_exception_leak — raw_exception_leak is true, or error_handling is
        "raw"/"raw_exception"/"leak"
    Returns a sublist of MISTAKE_IDS in MISTAKE_IDS order; [] when clean.
    """
    config = server_config or {}
    found = set()
    if config.get("stdout_printing") or config.get("prints_to_stdout"):
        found.add("stdout_printing")
    declared = set(config.get("declared_capabilities") or [])
    implemented = set(config.get("implemented_capabilities") or [])
    if declared - implemented:
        found.add("unimplemented_capability")
    if config.get("declared_capabilities") is None:
        caps = config.get("capabilities") or {}
        impl = config.get("implemented") or []
        if isinstance(caps, dict) and set(caps.keys()) - set(impl):
            found.add("unimplemented_capability")
    if config.get("human_only_description") or \
            config.get("description_audience") in ("human", "human_only", "humans"):
        found.add("human_only_description")
    if config.get("accept_anything_schema"):
        found.add("accept_anything_schema")
    else:
        for tool in config.get("tools") or []:
            schema = tool.get("inputSchema") or tool.get("input_schema") or {}
            if isinstance(schema, dict) and "properties" not in schema:
                found.add("accept_anything_schema")
    if config.get("raw_exception_leak") or \
            config.get("error_handling") in ("raw", "raw_exception", "leak"):
        found.add("raw_exception_leak")
    return [m for m in MISTAKE_IDS if m in found]


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
    server = build_server(DEMO_METADATA, {"tools": {}, "resources": {}})
    init = server.initialize({"protocolVersion": PROTOCOL_VERSION})
    assert init["capabilities"] == {"tools": {}, "resources": {}}, init
    print("first_server: minimal server")
    print(f"  serverInfo: {init['serverInfo']['name']} {init['serverInfo']['version']}")
    print(f"  initialize echoes declared capabilities: {sorted(init['capabilities'])}")
    print(f"  tools/list: {[t['name'] for t in server.list_tools()]}")

    over = check_declaration(OVER_DECLARING_SERVER)
    fixed_decl = check_declaration(CORRECTED_SERVER)
    assert over == ["resources"], over
    assert fixed_decl == [], fixed_decl
    print("declaration checker:")
    print(f"  over-declaring server mismatches (exactly 1): {over}")
    print(f"  corrected server mismatches (0): {fixed_decl}")

    happy, happy_errors = server.call_tool("word_count", {"text": "the quick brown fox"})
    assert happy == {"count": 4} and happy_errors == [], (happy, happy_errors)
    print(f"  word_count('the quick brown fox') -> count={happy['count']}")

    print("adversarial args (validate_args, none raise):")
    expected_codes = ["missing_required", "wrong_type", "too_long", None, "not_an_object"]
    for args, expected in zip(ADVERSARIAL_ARGS, expected_codes):
        errors = validate_args(WORD_COUNT_SCHEMA, args)
        codes = [e["code"] for e in errors]
        label = "valid" if not errors else ",".join(codes)
        shown = repr(args)[:40] + ("..." if len(repr(args)) > 40 else "")
        print(f"  args={shown} -> {label}")
        if expected is None:
            assert errors == [], (args, errors)
        else:
            assert expected in codes, (args, errors)

    lab = handshake_lab(FULL_CAPS, STRIPPED_CAPS)
    assert lab["full"]["protocol_version"] == "2025-06-18", lab
    assert lab["stripped"]["protocol_version"] == "2025-03-26", lab
    print("handshake lab:")
    print(f"  full caps:     version={lab['full']['protocol_version']} "
          f"shared={lab['full']['capabilities']}")
    print(f"  stripped caps: version={lab['stripped']['protocol_version']} "
          f"shared={lab['stripped']['capabilities']}")

    broken = find_mistakes(BROKEN_CONFIG)
    fixed = find_mistakes(FIXED_CONFIG)
    assert broken == MISTAKE_IDS, broken
    assert fixed == [], fixed
    print("mistake hunt:")
    print(f"  broken config mistakes ({len(broken)}/5): {broken}")
    print(f"  fixed config mistakes (0/5): {fixed}")

    print("first_server demo: OK")


if __name__ == "__main__":
    main()
