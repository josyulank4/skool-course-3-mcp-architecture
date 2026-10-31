# Lab 7: Security — Stop the Injection Drill

Section 14 — Hands-On Labs: Build It Yourself, companion to the Skool
course **MCP Architecture: Building Tool-Using AI Systems**.

This lab builds the `s07/security` demo with your own hands: the code
is shown step by step, the demo is run for real, and its actual output
is read line by line.

## Checkpoints (git tags)

- Start:  `git checkout lab-07-start` — `demo.py` is a scaffold:
  docstring, imports and data are in place; every function body is a
  TODO for you to implement along with the video.
- Finish: `git checkout lab-07` — `demo.py` is the complete working
  demo, identical to `s07/security/demo.py`.

## Run it

```bash
git checkout lab-07
cd labs/lab-07
python3 demo.py
```

Expected output begins: `security: injection through tool output`
Expected output ends:   `security demo: OK`

## Stranger test

From a fresh clone of this repository, check out `lab-07` and run the
demo as above. The output must match the lab video's run exactly.
