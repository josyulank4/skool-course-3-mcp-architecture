"""Lab 1 probe: a malformed first request, the protocol error, the fix.

Run from s01/hello_mcp (demo.py beside this probe). Three real calls
against the demo's own server: a request with no jsonrpc member, a
well-formed request naming a method that does not exist, and the
corrected initialize + tools/call sequence.
"""
import importlib.util
import json

spec = importlib.util.spec_from_file_location("demo", "demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

server = demo.HelloMCPServer()

bad = {"id": 1, "method": "initialize", "params": {}}
resp = server.handle(bad)
print("malformed request (the jsonrpc member is missing):")
print("  ->", json.dumps(resp["error"], sort_keys=True))

resp = server.handle(demo.make_request(2, "tools/destroy"))
print("well-formed envelope, unknown method tools/destroy:")
print("  ->", json.dumps(resp["error"], sort_keys=True))

client = demo.HelloMCPClient(server)
hs = client.initialize()
print("fixed: initialize with the full envelope")
print(f"  -> protocolVersion {hs['protocolVersion']}, "
      f"server {hs['serverInfo']['name']} {hs['serverInfo']['version']}")
print("  tools/call add(a=2, b=3) ->", client.call_tool("add", {"a": 2, "b": 3}))
