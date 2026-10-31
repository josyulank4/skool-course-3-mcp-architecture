# Lab 1: Hello MCP — Run Your First Server

Section 14 — Hands-On Labs: Build It Yourself, companion to the Skool
course **MCP Architecture: Building Tool-Using AI Systems**.

This lab builds the `s01/hello_mcp` demo with your own hands: the code
is shown step by step, the demo is run for real, and its actual output
is read line by line.

## Checkpoints (git tags)

- Start:  `git checkout lab-01-start` — `demo.py` is a scaffold:
  docstring, imports and data are in place; every function body is a
  TODO for you to implement along with the video.
- Finish: `git checkout lab-01` — `demo.py` is the complete working
  demo, identical to `s01/hello_mcp/demo.py`.

## Run it

```bash
git checkout lab-01
cd labs/lab-01
python3 demo.py
```

Expected output begins: `hello_mcp: initialize handshake`
Expected output ends:   `hello_mcp demo: OK`

## The probe

This lab's failure beat is a separate script, `probe_lab01.py`
(added at the finish tag). Copy it beside the demo it probes and run:

```bash
cp labs/lab-01/probe_lab01.py s01/hello_mcp/
cd s01/hello_mcp && python3 probe_lab01.py
```

It performs the lab's wrong request for real, reads the server's
structured refusal, then performs the corrected request.

## Stranger test

From a fresh clone of this repository, check out `lab-01` and run the
demo as above. The output must match the lab video's run exactly.
