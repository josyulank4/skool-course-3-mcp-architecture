# Lab 11: Production — Run the Canary Rollback

Section 14 — Hands-On Labs: Build It Yourself, companion to the Skool
course **MCP Architecture: Building Tool-Using AI Systems**.

This lab builds the `s11/production` demo with your own hands: the code
is shown step by step, the demo is run for real, and its actual output
is read line by line.

## Checkpoints (git tags)

- Start:  `git checkout lab-11-start` — `demo.py` is a scaffold:
  docstring, imports and data are in place; every function body is a
  TODO for you to implement along with the video.
- Finish: `git checkout lab-11` — `demo.py` is the complete working
  demo, identical to `s11/production/demo.py`.

## Run it

```bash
git checkout lab-11
cd labs/lab-11
python3 demo.py
```

Expected output begins: `production: observability, packaging, scaling, canary`
Expected output ends:   `production demo: OK`

## Stranger test

From a fresh clone of this repository, check out `lab-11` and run the
demo as above. The output must match the lab video's run exactly.
