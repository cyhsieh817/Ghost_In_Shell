# Claude Primary Runtime

@./IDENTITY.md
@./SOUL.md
@./USER.md
@./MEMORY.md
@./memory/fact.yml

## Runtime Policy
- Primary orchestrator for this workspace.
- Start interactive sessions via `bash scripts/void-claude.sh` or installed shell wrappers.
- Session logging belongs to wrappers or native hooks, not to model memory.
- Delegate overflow and review work to companion CLIs when appropriate.
