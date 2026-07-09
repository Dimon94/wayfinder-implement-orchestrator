#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
CODEX_SKILL = ROOT / "skills" / "wayfinder-implement-orchestrator" / "SKILL.md"
CLAUDE_SKILL = ROOT / "claude" / "skills" / "wayfinder-implement-orchestrator" / "SKILL.md"
CLAUDE_AGENTS = ROOT / "claude" / "agents"
MANIFEST = ROOT / "skill-bundle.json"


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def frontmatter(path: Path) -> str:
    text = path.read_text()
    end = text.find("\n---\n", 4)
    if not text.startswith("---\n") or end == -1:
        fail(f"frontmatter fences invalid: {path.relative_to(ROOT)}")
    return text[4:end]


def require_frontmatter(path: Path, required: dict[str, Optional[str]]) -> None:
    fm = frontmatter(path)
    for key, expected in required.items():
        match = re.search(rf"^{re.escape(key)}:\s*(.+)$", fm, re.MULTILINE)
        if not match:
            fail(f"missing frontmatter field in {path.relative_to(ROOT)}: {key}")
        if expected is not None and match.group(1).strip() != expected:
            fail(f"invalid frontmatter field in {path.relative_to(ROOT)}: {key}")


def check_references(skill_path: Path) -> None:
    text = skill_path.read_text()
    missing = []
    for ref in re.findall(r"`((?:references|assets)/[^`]+)`", text):
        if not (skill_path.parent / ref).exists():
            missing.append(ref)
    if missing:
        fail(
            f"missing referenced files in {skill_path.relative_to(ROOT)}: "
            + ", ".join(missing)
        )


def check_no_runtime_leaks() -> None:
    codex_hits = []
    for path in (ROOT / "skills" / "wayfinder-implement-orchestrator").rglob("*.md"):
        for lineno, line in enumerate(path.read_text().splitlines(), 1):
            if re.search(r"Herdr|HERDR_ENV|pane worker|worker pane", line):
                codex_hits.append(f"{path.relative_to(ROOT)}:{lineno}:{line}")
    if codex_hits:
        fail("Herdr runtime leaked into Codex skill:\n" + "\n".join(codex_hits))

    claude_banned = re.compile(
        r"create_thread|read_thread|send_message_to_thread|automation_update|"
        r"pendingWorktreeId|threadId|list_projects|spawn_agent|fork_thread|"
        r"(?<!sub)agent_type|fork_context|Codex thread|Codex 线程|child thread|"
        r"child session|fresh\s+`?/?[A-Za-z-]*`?\s*session|fresh session|"
        r"child commit|child 报告|父线程|子线程|线程|heartbeat|"
        r"automation|reminder|wake-up"
    )
    claude_hits = []
    for path in [
        *(ROOT / "claude" / "skills" / "wayfinder-implement-orchestrator").rglob("*.md"),
        *(ROOT / "claude" / "agents").glob("wayfinder-*.md"),
    ]:
        for lineno, line in enumerate(path.read_text().splitlines(), 1):
            if claude_banned.search(line):
                claude_hits.append(f"{path.relative_to(ROOT)}:{lineno}:{line}")
    if claude_hits:
        fail("Codex runtime leaked into Claude skill:\n" + "\n".join(claude_hits))

    claude_monitor = (
        ROOT
        / "claude"
        / "skills"
        / "wayfinder-implement-orchestrator"
        / "references"
        / "child-monitoring.md"
    ).read_text()
    for required in ("Herdr pane status", "进度快照", "5 分钟检查"):
        if required not in claude_monitor:
            fail(f"Claude monitoring missing runtime guard: {required}")

    claude_channel = (
        ROOT
        / "claude"
        / "skills"
        / "wayfinder-implement-orchestrator"
        / "references"
        / "codex-first-channel.md"
    ).read_text()
    for required in (
        "codex@openai-codex",
        "codex:codex-rescue",
        "--fresh",
        "--resume",
        "raw Codex CLI",
    ):
        if required not in claude_channel:
            fail(f"Claude codex channel missing plugin guard: {required}")

    claude_placement = (
        ROOT
        / "claude"
        / "skills"
        / "wayfinder-implement-orchestrator"
        / "references"
        / "herdr-pane-placement.md"
    ).read_text()
    for required in (
        "--workspace",
        "--no-focus",
        "herdr workspace list",
        "herdr pane list --workspace",
        "同名加尾号",
        "herdr pane get",
    ):
        if required not in claude_placement:
            fail(f"Claude pane placement missing guard: {required}")


def main() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("format") != "codex-claude-skill-bundle/v1":
        fail("invalid bundle format")

    expected_requires = [
        "ask-matt",
        "wayfinder",
        "grilling",
        "domain-modeling",
        "prototype",
        "research",
        "to-spec",
        "to-tickets",
        "implement",
        "code-review",
        "writing-great-skills",
    ]
    actual_requires = [item.get("name") for item in manifest.get("requires") or []]
    if actual_requires != expected_requires:
        fail("requires mismatch")

    expected_entrypoints = {
        "codex": "skills/wayfinder-implement-orchestrator/SKILL.md",
        "claude": "claude/skills/wayfinder-implement-orchestrator/SKILL.md",
        "claudeAgents": "claude/agents",
    }
    if manifest.get("entrypoints") != expected_entrypoints:
        fail("entrypoints mismatch")

    install = manifest.get("install") or {}
    for key in ("codexSkillDirectory", "claudeSkillDirectory", "claudeAgentsDirectory"):
        if key not in install:
            fail(f"missing install target: {key}")

    require_frontmatter(
        CODEX_SKILL,
        {
            "name": "wayfinder-implement-orchestrator",
            "description": None,
            "disable-model-invocation": "true",
        },
    )
    require_frontmatter(
        CLAUDE_SKILL,
        {
            "name": "wayfinder-implement-orchestrator",
            "description": None,
        },
    )

    check_references(CODEX_SKILL)
    check_references(CLAUDE_SKILL)
    check_no_runtime_leaks()

    expected_agents = {
        "wayfinder-frontier-worker.md",
        "wayfinder-gate-worker.md",
        "wayfinder-implementation-worker.md",
        "wayfinder-integration-reviewer.md",
    }
    actual_agents = {path.name for path in CLAUDE_AGENTS.glob("wayfinder-*.md")}
    if actual_agents != expected_agents:
        fail("claude agent set mismatch")
    for agent in CLAUDE_AGENTS.glob("wayfinder-*.md"):
        require_frontmatter(agent, {"name": None, "description": None})

    banned = re.compile(
        r"PDCA|cc-plan|cc-do|cc-check|cc-act|task\.md#Execution Environments|Parallel PDCA"
    )
    hits = []
    for path in [
        *(ROOT / "skills" / "wayfinder-implement-orchestrator").rglob("*.md"),
        *(ROOT / "claude").rglob("*.md"),
    ]:
        for lineno, line in enumerate(path.read_text().splitlines(), 1):
            if banned.search(line):
                hits.append(f"{path.relative_to(ROOT)}:{lineno}:{line}")
    if hits:
        fail("cc-dev PDCA state-machine leak:\n" + "\n".join(hits))

    print("bundle: pass")


if __name__ == "__main__":
    main()
