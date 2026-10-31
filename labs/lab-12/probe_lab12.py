"""Lab 12 probe: a sloppy direction string misclassifies, then resolves.

Run from s12/ecosystem (demo.py beside this probe). The classifier
reads a fixed vocabulary — tool, tools, data, agent. Describing the
account database with the everyday word 'database' lands in
'neither' without a sound; the same connection, described in the
classifier's own vocabulary, resolves to mcp.
"""
import importlib.util

spec = importlib.util.spec_from_file_location("demo", "demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

sloppy = {"direction": "agent -> database"}
print(f"sloppy direction 'agent -> database' -> {demo.classify_connection(sloppy)}")
fixed = {"direction": "agent->data"}
print(f"corrected direction 'agent->data' -> {demo.classify_connection(fixed)}")
named = {"from_kind": "agent", "to_kind": "agent"}
print(f"explicit fields agent->agent -> {demo.classify_connection(named)}")
