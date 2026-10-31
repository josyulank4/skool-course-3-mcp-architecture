# Lab 5: Primitives — Tools, Resources, Prompts

Section 14 — Hands-On Labs: Build It Yourself, companion to the Skool
course **MCP Architecture: Building Tool-Using AI Systems**.

This lab builds the `s05/primitives` demo with your own hands: the code
is shown step by step, the demo is run for real, and its actual output
is read line by line.

## Checkpoints (git tags)

- Start:  `git checkout lab-05-start` — `demo.py` is a scaffold:
  docstring, imports and data are in place; every function body is a
  TODO for you to implement along with the video.
- Finish: `git checkout lab-05` — `demo.py` is the complete working
  demo, identical to `s05/primitives/demo.py`.

## Run it

```bash
git checkout lab-05
cd labs/lab-05
python3 demo.py
```

Expected output begins: `primitives: resources via URI templates`
Expected output ends:   `primitives demo: OK`

## The probe

This lab's failure beat is a separate script, `probe_lab05.py`
(added at the finish tag). Copy it beside the demo it probes and run:

```bash
cp labs/lab-05/probe_lab05.py s05/primitives/
cd s05/primitives && python3 probe_lab05.py
```

It performs the lab's wrong request for real, reads the server's
structured refusal, then performs the corrected request.

## Stranger test

From a fresh clone of this repository, check out `lab-05` and run the
demo as above. The output must match the lab video's run exactly.
