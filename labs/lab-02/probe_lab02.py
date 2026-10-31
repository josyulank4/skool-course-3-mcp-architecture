"""Lab 2 probe: an unregistered resource, a version-less handshake, fixes.

Run from s02/fundamentals (demo.py beside this probe). Three real
calls: resources/read for a URI the server never registered, a
handshake capture whose two sides share no protocol version, and the
corrected capture over the demo's own fixtures.
"""
import importlib.util
import json

spec = importlib.util.spec_from_file_location("demo", "demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

client = demo.FundamentalsClient()
resp = client.server.handle(
    demo.make_request(7, "resources/read", {"uri": "data://secrets"}))
print("resources/read data://secrets (never registered):")
print("  ->", json.dumps(resp["error"], sort_keys=True))

cap = demo.handshake_capture(
    {"protocol_versions": ["2024-11-05"], "capabilities": {"tools": {}}},
    {"protocol_versions": ["2025-06-18"], "capabilities": {"tools": {}}})
print("handshake with no shared protocol version:")
print(f"  -> negotiated {cap['protocol_version']}, shared {cap['capabilities']}")

cap = demo.handshake_capture(demo.CLIENT_CAPS_FIXTURE, demo.SERVER_CAPS_FIXTURE)
print("corrected handshake (the demo's own fixtures):")
print(f"  -> negotiated {cap['protocol_version']}, shared {cap['capabilities']}")
