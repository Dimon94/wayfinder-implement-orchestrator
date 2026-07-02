#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "wayfinder-implement-orchestrator" / "SKILL.md"
MANIFEST = ROOT / "skill-bundle.json"


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("format") != "single-codex-skill/v1":
        fail("invalid bundle format")
    if manifest.get("entrypoint") != "skills/wayfinder-implement-orchestrator/SKILL.md":
        fail("entrypoint mismatch")

    text = SKILL.read_text()
    end = text.find("\n---\n", 4)
    if not text.startswith("---\n") or end == -1:
        fail("frontmatter fences invalid")

    frontmatter = text[4:end]
    required = {
        "name": "wayfinder-implement-orchestrator",
        "description": None,
        "disable-model-invocation": "true",
    }
    for key, expected in required.items():
        match = re.search(rf"^{re.escape(key)}:\s*(.+)$", frontmatter, re.MULTILINE)
        if not match:
            fail(f"missing frontmatter field: {key}")
        if expected is not None and match.group(1).strip() != expected:
            fail(f"invalid frontmatter field: {key}")

    missing = []
    for ref in re.findall(r"`((?:references|assets)/[^`]+)`", text):
        if not (SKILL.parent / ref).exists():
            missing.append(ref)
    if missing:
        fail("missing referenced files: " + ", ".join(missing))

    banned = re.compile(
        r"PDCA|cc-plan|cc-do|cc-check|cc-act|task\.md#Execution Environments|Parallel PDCA"
    )
    hits = []
    for path in (ROOT / "skills" / "wayfinder-implement-orchestrator").rglob("*.md"):
        for lineno, line in enumerate(path.read_text().splitlines(), 1):
            if banned.search(line):
                hits.append(f"{path.relative_to(ROOT)}:{lineno}:{line}")
    if hits:
        fail("cc-dev PDCA state-machine leak:\n" + "\n".join(hits))

    print("bundle: pass")


if __name__ == "__main__":
    main()
