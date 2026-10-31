# Lab 10: Testing — Pass the Regression Gate

Section 14 — Hands-On Labs: Build It Yourself, companion to the Skool
course **MCP Architecture: Building Tool-Using AI Systems**.

This lab builds the `s10/testing` demo with your own hands: the code
is shown step by step, the demo is run for real, and its actual output
is read line by line.

## Checkpoints (git tags)

- Start:  `git checkout lab-10-start` — `demo.py` is a scaffold:
  docstring, imports and data are in place; every function body is a
  TODO for you to implement along with the video.
- Finish: `git checkout lab-10` — `demo.py` is the complete working
  demo, identical to `s10/testing/demo.py`.

## Run it

```bash
git checkout lab-10
cd labs/lab-10
python3 demo.py
```

Expected output begins: `testing: the full gate on the good server`
Expected output ends:   `testing demo: OK`

## Stranger test

From a fresh clone of this repository, check out `lab-10` and run the
demo as above. The output must match the lab video's run exactly.
