# Lab 2: Fundamentals — Speak the Protocol

Section 14 — Hands-On Labs: Build It Yourself, companion to the Skool
course **MCP Architecture: Building Tool-Using AI Systems**.

This lab builds the `s02/fundamentals` demo with your own hands: the code
is shown step by step, the demo is run for real, and its actual output
is read line by line.

## Checkpoints (git tags)

- Start:  `git checkout lab-02-start` — `demo.py` is a scaffold:
  docstring, imports and data are in place; every function body is a
  TODO for you to implement along with the video.
- Finish: `git checkout lab-02` — `demo.py` is the complete working
  demo, identical to `s02/fundamentals/demo.py`.

## Run it

```bash
git checkout lab-02
cd labs/lab-02
python3 demo.py
```

Expected output begins: `fundamentals: sample server fundamentals-sample protocol 2025-06-18`
Expected output ends:   `fundamentals demo: OK`

## The probe

This lab's failure beat is a separate script, `probe_lab02.py`
(added at the finish tag). Copy it beside the demo it probes and run:

```bash
cp labs/lab-02/probe_lab02.py s02/fundamentals/
cd s02/fundamentals && python3 probe_lab02.py
```

It performs the lab's wrong request for real, reads the server's
structured refusal, then performs the corrected request.

## Stranger test

From a fresh clone of this repository, check out `lab-02` and run the
demo as above. The output must match the lab video's run exactly.
