# Chapter 13 — Carryover

> Stub. Filled out in M6-C.

Cross-session task hand-off. Default 7-day expiry. Status transitions:
active -> expired (on expiry sweep) or active -> promoted (on episodic
promotion, which moves the file to memory/_archive/).

## CLI

- `gish carryover create --project X --topic Y`
- `gish carryover list`
- `gish carryover expire`
- `gish carryover promote-to-episodic --project X --topic Y`
