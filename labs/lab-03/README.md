# Lab 3: Transports — Move JSON-RPC Live

Section 14 — Hands-On Labs: Build It Yourself, companion to the Skool
course **MCP Architecture: Building Tool-Using AI Systems**.

This lab builds the `s03/transports` demo with your own hands: the code
is shown step by step, the demo is run for real, and its actual output
is read line by line.

## Checkpoints (git tags)

- Start:  `git checkout lab-03-start` — `demo.py` is a scaffold:
  docstring, imports and data are in place; every function body is a
  TODO for you to implement along with the video.
- Finish: `git checkout lab-03` — `demo.py` is the complete working
  demo, identical to `s03/transports/demo.py`.

## Run it

```bash
git checkout lab-03
cd labs/lab-03
python3 demo.py
```

Expected output begins: `transports: anatomy of the one server`
Expected output ends:   `transports demo: OK`

## The probe

This lab's failure beat is a separate script, `probe_lab03.py`
(added at the finish tag). Copy it beside the demo it probes and run:

```bash
cp labs/lab-03/probe_lab03.py s03/transports/
cd s03/transports && python3 probe_lab03.py
```

It performs the lab's wrong request for real, reads the server's
structured refusal, then performs the corrected request.

## Stranger test

From a fresh clone of this repository, check out `lab-03` and run the
demo as above. The output must match the lab video's run exactly.
