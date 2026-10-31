"""Lab 5 probe: call an unregistered tool, register one, call again.

Run from s05/primitives (demo.py beside this probe). First a
tools/call for delete_ticket, which exists in neither the demo's
tool registry nor its schemas; then a small count_tickets tool is
registered into the same registry the handler reads, and the same
call shape succeeds.
"""
import importlib.util
import json

spec = importlib.util.spec_from_file_location("demo", "demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

resp = demo.handle_message({"jsonrpc": "2.0", "id": 9, "method": "tools/call",
                            "params": {"name": "delete_ticket",
                                       "arguments": {"ticket_id": 101}}})
print("tools/call delete_ticket (never registered):")
print("  ->", json.dumps(resp["error"], sort_keys=True))


def count_tickets():
    return {"tickets_found": len(demo.search_tickets(""))}


demo.TOOL_FUNCTIONS["count_tickets"] = count_tickets
resp = demo.handle_message({"jsonrpc": "2.0", "id": 10, "method": "tools/call",
                            "params": {"name": "count_tickets",
                                       "arguments": {}}})
print("after registering count_tickets in TOOL_FUNCTIONS:")
print("  ->", resp["result"]["content"][0]["text"])
