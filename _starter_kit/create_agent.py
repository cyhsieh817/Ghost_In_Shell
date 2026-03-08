#!/usr/bin/env python3
"""
create_agent.py — Ghost In Shell Starter Kit  v3.0
Interactive CLI: collect all variables, generate a complete agent system
with hot/cold memory separation, CLAUDE.md @import, and zero placeholder residue.
"""

import os
import re
import shutil
import sys
from datetime import datetime


# ── ANSI Colors ──────────────────────────────────────────────────────────────
class C:
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    CYAN   = "\033[36m"
    GREEN  = "\033[32m"
    YELLOW = "\033[33m"
    RED    = "\033[31m"
    BLUE   = "\033[34m"
    RESET  = "\033[0m"


# ── UI Helpers ───────────────────────────────────────────────────────────────
def banner():
    print(f"""
{C.CYAN}{C.BOLD}╔══════════════════════════════════════════════════╗
║   🐚  Ghost In Shell — Agent Creator  v3.0      ║
║   Interactive wizard · Zero placeholder residue  ║
╚══════════════════════════════════════════════════╝{C.RESET}
""")


def section(title: str):
    print(f"\n{C.BLUE}{C.BOLD}{'─' * 50}{C.RESET}")
    print(f"{C.BLUE}{C.BOLD}  {title}{C.RESET}")
    print(f"{C.BLUE}{'─' * 50}{C.RESET}")


def ask(prompt: str, default: str = "", required: bool = True) -> str:
    hint = f"{C.DIM}[{default}]{C.RESET} " if default else ""
    while True:
        try:
            raw = input(f"  {C.BOLD}{prompt}{C.RESET} {hint}» ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{C.YELLOW}Aborted.{C.RESET}")
            sys.exit(0)
        value = raw if raw else default
        if value or not required:
            return value
        print(f"  {C.RED}⚠  This field is required.{C.RESET}")


def ask_path(prompt: str, default: str = "") -> str:
    while True:
        raw = ask(prompt, default)
        path = os.path.abspath(os.path.expanduser(raw.strip().strip('"').strip("'")))
        if os.path.exists(path):
            return path
        print(f"  {C.YELLOW}⚠  Path does not exist: {path}{C.RESET}")
        if ask("  Create this directory?", "y", required=False).lower() not in ("n", "no"):
            try:
                os.makedirs(path)
                print(f"  {C.GREEN}✅ Created: {path}{C.RESET}")
                return path
            except Exception as e:
                print(f"  {C.RED}❌ Failed: {e}{C.RESET}")
        else:
            print("  Please enter a valid path.")


# ── Placeholder Engine ───────────────────────────────────────────────────────
PLACEHOLDER_RE = re.compile(r"\{\{([A-Z0-9_]+)\}\}")


def replace_all(content: str, replacements: dict) -> str:
    for key, value in replacements.items():
        content = content.replace("{{" + key + "}}", str(value))
    return content


def scan_residual(content: str) -> list[str]:
    return list(set(PLACEHOLDER_RE.findall(content)))


# ── Output Structure ─────────────────────────────────────────────────────────
def create_workspace_structure(vault_path: str):
    """Create the full PARA-based workspace directory tree."""
    dirs = [
        # Agent System
        "_Agent_System/10_Projects",
        "_Agent_System/20_Areas",
        "_Agent_System/30_Resources",
        "_Agent_System/40_Archive",
        "_Agent_System/99_System/990_POLICY",
        "_Agent_System/99_System/991_Logs/Learning_Log",
        "_Agent_System/99_System/991_Logs/Evolution_Log",
        "_Agent_System/99_System/992_Config",
        "_Agent_System/99_System/993_Worker_Inbox",
        # User Workspace
        "_User_Workspace/01_Inbox",
        "_User_Workspace/02_Tasks",
        "_User_Workspace/03_Outbox",
    ]
    for d in dirs:
        full = os.path.join(vault_path, d)
        os.makedirs(full, exist_ok=True)
    return True


# ── Template Output Routing ──────────────────────────────────────────────────
def get_output_path(template_name: str, workspace: str, vault: str) -> str:
    """Route each template to its correct output location."""
    name = template_name.replace(".template", "")
    routes = {
        # Root files (workspace level)
        "CLAUDE.md":          os.path.join(workspace, "CLAUDE.md"),
        "IDENTITY.md":        os.path.join(workspace, "IDENTITY.md"),
        "SOUL.md":            os.path.join(workspace, "SOUL.md"),
        "USER.md":            os.path.join(workspace, "USER.md"),
        "MEMORY.md":          os.path.join(workspace, "MEMORY.md"),
        # Memory layer
        "fact.yml":           os.path.join(workspace, "memory", "fact.yml"),
        "fact_archive.yml":   os.path.join(workspace, "memory", "fact_archive.yml"),
        "fact_decisions.yml": os.path.join(workspace, "memory", "fact_decisions.yml"),
        "episodic.jsonl":     os.path.join(workspace, "memory", "episodic.jsonl"),
        "scratchpad.md":      os.path.join(workspace, "memory", "scratchpad.md"),
        # Policies (in vault)
        "ACCESS_POLICY.md":   os.path.join(vault, "_Agent_System/99_System/990_POLICY/ACCESS_POLICY.md"),
        "AUTONOMY_POLICY.md": os.path.join(vault, "_Agent_System/99_System/990_POLICY/AUTONOMY_POLICY.md"),
        # Workspace rules
        "TRIAGE.md":          os.path.join(vault, "_Agent_System/99_System/TRIAGE.md"),
        "CAPABILITIES.md":    os.path.join(vault, "_Agent_System/99_System/CAPABILITIES.md"),
    }
    return routes.get(name, os.path.join(workspace, name))


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    banner()

    kit_dir    = os.path.dirname(os.path.abspath(__file__))
    config_dir = os.path.join(kit_dir, "config")

    if not os.path.isdir(config_dir):
        print(f"{C.RED}❌ Cannot find config/ directory at {kit_dir}{C.RESET}")
        sys.exit(1)

    today = datetime.now().strftime("%Y-%m-%d")

    # ── 1. Agent Identity ────────────────────────────────────────
    section("1 / 4  🤖  Agent Identity")
    agent_name    = ask("Agent name",          "MyAgent")
    agent_emoji   = ask("Agent emoji",         "🤖")
    agent_type    = ask("Agent type",          "AI Assistant")
    agent_vibe    = ask("Personality style",   "Professional & Helpful")
    agent_tagline = ask("Tagline (one-liner)", "Here to help.")

    # ── 2. User Profile ──────────────────────────────────────────
    section("2 / 4  👤  User Profile")
    user_name    = ask("Your name",                            "User")
    call_as      = ask("How should the agent address you?",    "Boss")
    primary_lang = ask("Primary language",                     "English")
    timezone     = ask("Timezone (IANA format)",               "UTC")
    org_1        = ask("Organization / company",               "Personal")
    title_1      = ask("Your role / title",                    "Owner")
    tech_stack   = ask("Tech stack (comma-separated)",         "Python, TypeScript")
    comm_style   = ask("Communication style",                  "Direct and concise")
    sensitive    = ask("Sensitive areas (e.g., patents, financials)", "None", required=False)

    # ── 3. Paths ─────────────────────────────────────────────────
    section("3 / 4  📂  Paths")
    print(f"  {C.DIM}💡 You can drag folders into the terminal!{C.RESET}")
    workspace_path = ask_path("Workspace root (where CLAUDE.md lives)", os.getcwd())
    vault_path     = ask_path("Vault root (for _Agent_System/)",        workspace_path)

    # Ensure memory dir exists
    memory_dir = os.path.join(workspace_path, "memory")
    os.makedirs(memory_dir, exist_ok=True)

    # ── 4. Optional Settings ─────────────────────────────────────
    section("4 / 4  ⚙️   Optional Settings (press Enter for defaults)")
    rule_1 = ask("Rule 1", "Always use absolute file paths",    required=False)
    rule_2 = ask("Rule 2", "Ask before any irreversible action", required=False)
    rule_3 = ask("Rule 3", "Never expose sensitive data",        required=False)

    # ── Build Replacement Dictionary ─────────────────────────────
    replacements = {
        # Auto
        "DATE": today,
        # Agent
        "AGENT_NAME":    agent_name,
        "AGENT_EMOJI":   agent_emoji,
        "EMOJI":         agent_emoji,
        "AGENT_TYPE":    agent_type,
        "AGENT_VIBE":    agent_vibe,
        "AGENT_TAGLINE": agent_tagline,
        # User
        "USER_NAME":          user_name,
        "CALL_AS":            call_as,
        "PRIMARY_LANGUAGE":   primary_lang,
        "LANGUAGE":           primary_lang,
        "USER_TIMEZONE":      timezone,
        "TIMEZONE":           timezone,
        "ORG_1":              org_1,
        "TITLE_1":            title_1,
        "TECH_STACK":         tech_stack,
        "TECH_1":             tech_stack,
        "COMMUNICATION_STYLE": comm_style,
        "PREF_1":             comm_style,
        "SENSITIVE_AREAS":    sensitive or "None",
        "SENSITIVE_1":        sensitive or "None",
        # Paths
        "VAULT_PATH":      vault_path,
        "WORKSPACE_PATH":  workspace_path,
        # Rules
        "RULE_1": rule_1 or "Always use absolute file paths",
        "RULE_2": rule_2 or "Ask before any irreversible action",
        "RULE_3": rule_3 or "Never expose sensitive data",
    }

    # ── Confirmation Summary ─────────────────────────────────────
    print(f"\n{C.CYAN}{C.BOLD}{'═' * 50}")
    print("  📋  Configuration Summary")
    print(f"{'═' * 50}{C.RESET}")
    rows = [
        ("Workspace",  workspace_path),
        ("Vault",      vault_path),
        ("Agent",      f"{agent_emoji} {agent_name}  — \"{agent_tagline}\""),
        ("Type/Style", f"{agent_type} / {agent_vibe}"),
        ("User",       f"{user_name} (addressed as: {call_as})"),
        ("Language",   f"{primary_lang} / {timezone}"),
        ("Org/Role",   f"{org_1} / {title_1}"),
        ("Tech",       tech_stack),
        ("Style",      comm_style),
    ]
    for label, val in rows:
        print(f"  {C.DIM}{label:<12}{C.RESET}  {val}")
    print()

    confirm = ask("Proceed? (y/n)", "y", required=False)
    if confirm.lower() not in ("", "y", "yes"):
        print(f"{C.YELLOW}Aborted.{C.RESET}")
        sys.exit(0)

    # ── Create Directory Structure ───────────────────────────────
    print(f"\n{C.BOLD}Creating workspace structure...{C.RESET}")
    create_workspace_structure(vault_path)
    print(f"{C.GREEN}✅ Directory structure created{C.RESET}")

    # ── Process Templates ────────────────────────────────────────
    print(f"\n{C.BOLD}Processing templates...{C.RESET}")

    residual_report: list[tuple[str, list[str]]] = []
    template_files = sorted(f for f in os.listdir(config_dir) if f.endswith(".template"))

    for tfile in template_files:
        src       = os.path.join(config_dir, tfile)
        dest      = get_output_path(tfile, workspace_path, vault_path)
        dest_name = os.path.basename(dest)

        # Ensure parent directory exists
        os.makedirs(os.path.dirname(dest), exist_ok=True)

        if os.path.exists(dest):
            if ask(f"  {dest_name} exists. Overwrite?", "n", required=False).lower() != "y":
                print(f"   {C.DIM}Skipped {dest_name}{C.RESET}")
                continue

        try:
            with open(src, "r", encoding="utf-8") as f:
                content = f.read()

            new_content = replace_all(content, replacements)
            residuals   = scan_residual(new_content)

            with open(dest, "w", encoding="utf-8") as f:
                f.write(new_content)

            if residuals:
                residual_report.append((dest_name, residuals))
                tag = f"{C.YELLOW}⚠ residual: {', '.join(residuals)}{C.RESET}"
            else:
                tag = f"{C.GREEN}✅{C.RESET}"
            print(f"   {tag}  {dest_name} → {os.path.dirname(dest)}/")

        except Exception as e:
            print(f"   {C.RED}❌ Failed {tfile}: {e}{C.RESET}")

    # ── Final Report ─────────────────────────────────────────────
    print(f"\n{C.CYAN}{C.BOLD}{'═' * 50}")
    print("  🐚  Agent Generation Complete!")
    print(f"{'═' * 50}{C.RESET}")

    if residual_report:
        print(f"\n{C.YELLOW}{C.BOLD}⚠  Files with unresolved placeholders:{C.RESET}")
        for fname, keys in residual_report:
            formatted = ", ".join("{{" + k + "}}" for k in keys)
            print(f"   {C.YELLOW}{fname}{C.RESET}: {formatted}")
    else:
        print(f"\n{C.GREEN}{C.BOLD}  Perfect! All placeholders resolved. Zero residue.{C.RESET}")

    print(f"""
{C.BOLD}What's next:{C.RESET}
  1. Review your files:
     - {workspace_path}/CLAUDE.md  (entry point)
     - {workspace_path}/SOUL.md    (personality)
     - {workspace_path}/memory/    (memory layers)

  2. Start your AI tool:
     $ cd {workspace_path}
     $ claude   # or cursor, etc.

  3. Test: Ask "Who are you?" — the agent should respond with its identity.

{C.DIM}Docs: https://github.com/your-repo/Ghost_In_Shell/docs/{C.RESET}
""")


if __name__ == "__main__":
    main()
