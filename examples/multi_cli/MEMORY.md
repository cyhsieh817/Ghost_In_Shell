# Memory Index

This workspace uses Ghost In Shell v5 for persistent memory.

## Active regions: prefrontal, hippocampus

### Prefrontal (working context)
@./memory/fact.yml

### Hippocampus (recent episodes)
@./memory/episodic.jsonl

## Memory store location
All memory files are in `./memory/`.

## Commands
```bash
# Search memory
gish recall --workspace . "<query>"

# Add a memory
gish log --workspace . --title "<title>" --content "<content>" --importance 5

# Health check
gish doctor --workspace .
```
