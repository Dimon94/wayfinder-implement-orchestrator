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


def main() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("format") != "codex-claude-skill-bundle/v1":
        fail("invalid bundle format")

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
