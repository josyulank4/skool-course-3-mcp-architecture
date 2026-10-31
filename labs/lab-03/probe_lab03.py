"""Lab 3 probe: call the HTTP transport before it is up, then start it.

Run from s03/transports (demo.py beside this probe). First a real
POST to a localhost port where nothing is listening yet; then the
demo's own start_http_server brings the transport up and the very
same initialize request succeeds.
"""
import importlib.util
import urllib.error

spec = importlib.util.spec_from_file_location("demo", "demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

req = demo.make_request(1, "initialize", {
    "protocolVersion": demo.PROTOCOL_VERSION, "capabilities": {},
    "clientInfo": {"name": "probe", "version": "1.0.0"}})

try:
    demo.http_call("http://127.0.0.1:8765", req, timeout=3)
    print("unexpected: something answered on port 8765")
except urllib.error.URLError as exc:
    print("POST initialize to http://127.0.0.1:8765 — nothing listening yet:")
    print(f"  -> {type(exc.reason).__name__}: {exc.reason}")

httpd, thread, url = demo.start_http_server()
try:
    resp = demo.http_call(url, req)
    print("the same call after start_http_server brings the transport up:")
    print(f"  -> initialize answered by server "
          f"{resp['result']['serverInfo']['name']}")
finally:
    demo.stop_http_server(httpd, thread)
