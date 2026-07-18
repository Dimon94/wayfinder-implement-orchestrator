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
CODEX_METADATA = (
    ROOT
    / "skills"
    / "wayfinder-implement-orchestrator"
    / "agents"
    / "openai.yaml"
)


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
    for required in ("herdr pane status", "terminal fan-in", "watchdog"):
        if required not in claude_monitor.lower():
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
        "herdr agent start",
        "codex -s danger-full-access -a never",
        "codex-pane",
        "claude-native",
        "herdr wait agent-status",
        "强制",
    ):
        if required not in claude_channel:
            fail(f"Claude codex channel missing herdr guard: {required}")

    plugin_banned = re.compile(
        r"codex:codex-rescue|codex@openai-codex|codex-plugin|/codex:|"
        r"codex-companion|CLAUDE_PLUGIN_ROOT|--fresh|--resume"
    )
    plugin_hits = []
    for path in [
        *(ROOT / "claude" / "skills" / "wayfinder-implement-orchestrator").rglob("*.md"),
        *(ROOT / "claude" / "agents").glob("wayfinder-*.md"),
    ]:
        for lineno, line in enumerate(path.read_text().splitlines(), 1):
            if plugin_banned.search(line):
                plugin_hits.append(f"{path.relative_to(ROOT)}:{lineno}:{line}")
    if plugin_hits:
        fail(
            "retired codex plugin channel leaked into Claude skill:\n"
            + "\n".join(plugin_hits)
        )

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
        "--tab",
        "--no-focus",
        "herdr workspace list",
        "herdr tab list --workspace",
        "herdr pane list --workspace",
        "herdr tab rename",
        "herdr pane get",
    ):
        if required not in claude_placement:
            fail(f"Claude pane placement missing guard: {required}")


def check_codex_project_targeting() -> None:
    skill_root = ROOT / "skills" / "wayfinder-implement-orchestrator"
    required_by_path = {
        skill_root / "SKILL.md": ("`Source owner projectId`",),
        skill_root / "references" / "fresh-session-boundaries.md": (
            "`projectId` 不变量",
            "同一仓库",
            "child `cwd`",
            "--git-common-dir",
        ),
        skill_root / "references" / "child-monitoring.md": (
            "`clientThreadId`",
            "相同的 `projectId`",
        ),
    }
    for path, required_items in required_by_path.items():
        content = path.read_text()
        for required in required_items:
            if required not in content:
                fail(
                    "Codex project targeting missing guard in "
                    f"{path.relative_to(ROOT)}: {required}"
                )

    dispatch_packets = list((skill_root / "assets").glob("*DISPATCH_PACKET.md"))
    for path in dispatch_packets:
        if "Source owner projectId：" not in path.read_text():
            fail(
                "Codex dispatch packet missing source owner coordinate: "
                f"{path.relative_to(ROOT)}"
            )

    monitoring = (
        skill_root / "references" / "child-monitoring.md"
    ).read_text()
    if "pendingWorktreeId" in monitoring:
        fail("Codex monitoring still uses stale pendingWorktreeId")


def check_frontier_lane_basics() -> None:
    codex_root = ROOT / "skills" / "wayfinder-implement-orchestrator"
    claude_root = ROOT / "claude" / "skills" / "wayfinder-implement-orchestrator"
    frontier_refs = (
        codex_root / "references" / "frontier-lanes.md",
        claude_root / "references" / "frontier-lanes.md",
    )
    for path in frontier_refs:
        if not path.exists():
            fail(f"missing frontier/lane contract: {path.relative_to(ROOT)}")
        content = path.read_text().lower()
        for required in (
            "ready frontier",
            "maximal safe batch",
            "execution lane",
            "terminal fan-in",
            "lane blocked",
            "local execution authority",
            "remote publication authority",
            "remote authority 不阻塞本地 lanes",
            "lane 内按 dependency order",
            "不读取 routine progress",
            "不建立固定 cadence",
        ):
            if required not in content:
                fail(
                    "frontier/lane contract missing invariant in "
                    f"{path.relative_to(ROOT)}: {required}"
                )


def require_strings(path: Path, required: tuple[str, ...], contract: str) -> None:
    if not path.exists():
        fail(f"missing {contract}: {path.relative_to(ROOT)}")
    content = path.read_text()
    for item in required:
        if item not in content:
            fail(
                f"{contract} missing invariant in "
                f"{path.relative_to(ROOT)}: {item}"
            )


def normalized_text(path: Path) -> str:
    return " ".join(path.read_text().split())


def require_patterns(
    path: Path, required: tuple[str, ...], forbidden: tuple[str, ...], contract: str
) -> None:
    content = normalized_text(path)
    for pattern in required:
        if not re.search(pattern, content):
            fail(
                f"{contract} missing positive semantic assertion in "
                f"{path.relative_to(ROOT)}: {pattern}"
            )
    for pattern in forbidden:
        if re.search(pattern, content):
            fail(
                f"{contract} contains forbidden semantic reversal in "
                f"{path.relative_to(ROOT)}: {pattern}"
            )


def parse_simple_yaml(path: Path) -> dict[str, object]:
    root: dict[str, object] = {}
    stack: list[tuple[int, dict[str, object]]] = [(-1, root)]
    for lineno, raw_line in enumerate(path.read_text().splitlines(), 1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if indent % 2:
            fail(f"invalid YAML indentation in {path.relative_to(ROOT)}:{lineno}")
        line = raw_line.strip()
        key, separator, raw_value = line.partition(":")
        if not separator or not re.fullmatch(r"[a-z_][a-z0-9_]*", key):
            fail(f"unsupported YAML entry in {path.relative_to(ROOT)}:{lineno}")
        while stack[-1][0] >= indent:
            stack.pop()
        parent = stack[-1][1]
        value = raw_value.strip()
        if not value:
            child: dict[str, object] = {}
            parent[key] = child
            stack.append((indent, child))
        elif value in ("true", "false"):
            parent[key] = value == "true"
        elif value.startswith('"'):
            try:
                parent[key] = json.loads(value)
            except json.JSONDecodeError as error:
                fail(
                    f"invalid quoted YAML value in "
                    f"{path.relative_to(ROOT)}:{lineno}: {error.msg}"
                )
        else:
            parent[key] = value
    return root


def packet_fields(path: Path) -> set[str]:
    fields = set()
    in_packet = False
    for line in path.read_text().splitlines():
        if line == "```text":
            in_packet = True
            continue
        if in_packet and line == "```":
            break
        if not in_packet or line.startswith(("-", " ")) or "：" not in line:
            continue
        fields.add(line.split("：", 1)[0])
    return fields


def check_extended_contracts() -> None:
    codex_root = ROOT / "skills" / "wayfinder-implement-orchestrator"
    claude_root = ROOT / "claude" / "skills" / "wayfinder-implement-orchestrator"

    for root in (codex_root, claude_root):
        require_strings(
            root / "SKILL.md",
            ("decision tickets", "小型化跳过证据", "/to-spec"),
            "spec-first route",
        )
        require_strings(
            root / "references" / "gate-state-machine.md",
            (
                "大型 Wayfinder",
                "小型化跳过证据",
                "linked decision tickets",
                "single worker invocation",
            ),
            "post-discovery route",
        )
        require_strings(
            root / "references" / "wayfinder-frontier-loop.md",
            ("/research", "research/<name>", "context pointer", "不重复派发"),
            "research dispatch",
        )
        require_strings(
            root / "assets" / "WAYFINDER_TICKET_DISPATCH_PACKET.md",
            ("/research", "research/<ticket-name>", "context pointer", "不得 close ticket"),
            "research packet",
        )
        require_strings(
            root / "assets" / "GATE_CHILD_DISPATCH_PACKET.md",
            ("五因子分", "XL", "L 必须带不拆理由", "估档读回"),
            "ticket estimation packet",
        )
        require_strings(
            root / "references" / "ticket-split-coverage.md",
            (
                "不得添加 Wayfinder child label",
                "不得把完成结果",
                "implementation graph",
                "map 只索引 decisions",
            ),
            "decision/implementation separation",
        )
        require_strings(
            root / "references" / "map-dashboard.md",
            ("联网单文件", "textContent", "innerHTML", "https:", "http:"),
            "dashboard input safety",
        )
        require_patterns(
            root / "references" / "gate-state-machine.md",
            (
                r"大型 Wayfinder map 清雾后默认先进入 `/to-spec`",
                r"只有通过下方「小型化跳过证据」时才可绕过 spec",
                r"任一条无法证明就选择 `needs-spec`",
            ),
            (
                r"大型 Wayfinder map 清雾后默认直接",
                r"无需.{0,20}小型化跳过证据",
                r"不需要.{0,20}小型化跳过证据",
            ),
            "spec-first route semantics",
        )
        require_patterns(
            root / "references" / "wayfinder-frontier-loop.md",
            (
                r"`Research` (?:worker|pane) 必须走 `/research` subagent 路线",
                r"不得统一改走 `/wayfinder`",
                r"已 assigned 的 research ticket 不在 frontier 内",
            ),
            (
                r"`Research` (?:worker|pane) 必须走 `/wayfinder`",
                r"允许.{0,20}research ticket.{0,20}重复派发",
            ),
            "research route semantics",
        )
        require_patterns(
            root / "assets" / "GATE_CHILD_DISPATCH_PACKET.md",
            (
                r"每张票必须 带 S/M/L 估档和五因子分",
                r"XL 必须拆分",
                r"L 必须带不拆理由",
                r"任一票不满足 就报告 blocked，不发布 tickets",
            ),
            (r"XL 可以发布", r"L 无需不拆理由"),
            "ticket estimation semantics",
        )

    metadata = parse_simple_yaml(CODEX_METADATA)
    interface = metadata.get("interface")
    policy = metadata.get("policy")
    if not isinstance(interface, dict) or not isinstance(policy, dict):
        fail("Codex metadata must contain interface and policy mappings")
    expected_interface = {
        "display_name": "Wayfinder Implement Orchestrator",
        "short_description": "Orchestrate Wayfinder through implementation",
        "default_prompt": (
            "Use $wayfinder-implement-orchestrator to carry this tracker-backed "
            "Wayfinder map through its approved delivery gates."
        ),
    }
    if interface != expected_interface:
        fail("Codex metadata interface mismatch")
    if policy != {"allow_implicit_invocation": False}:
        fail("Codex metadata must disable implicit invocation")

    gate_packet_fields = []
    research_packet_fields = []
    for root in (codex_root, claude_root):
        gate_packet_fields.append(
            packet_fields(root / "assets" / "GATE_CHILD_DISPATCH_PACKET.md")
        )
        research_packet_fields.append(
            packet_fields(root / "assets" / "WAYFINDER_TICKET_DISPATCH_PACKET.md")
        )
    for fields in gate_packet_fields:
        for required in ("小型化跳过证据", "估档读回"):
            if required not in fields:
                fail(f"gate packet missing structured field: {required}")
    for fields in research_packet_fields:
        for required in ("Research branch", "Research context pointer"):
            if required not in fields:
                fail(f"research packet missing structured field: {required}")

    codex_research_packet = (
        codex_root / "assets" / "WAYFINDER_TICKET_DISPATCH_PACKET.md"
    ).read_text()
    if "不要创建 descendants" in codex_research_packet:
        fail("Codex research packet forbids newly surfaced decision tickets")
    for required in ("descendant threads", "新 decision", "创建并连线"):
        if required not in codex_research_packet:
            fail(f"Codex research packet missing descendant boundary: {required}")

    descendant_ambiguity = re.compile(r"不(?:创建|打开) descendants(?:、|。|；|$)")
    ambiguity_hits = []
    for path in [
        *codex_root.rglob("*.md"),
        *claude_root.rglob("*.md"),
        *(ROOT / "claude" / "agents").glob("wayfinder-*.md"),
    ]:
        for lineno, line in enumerate(path.read_text().splitlines(), 1):
            if descendant_ambiguity.search(line):
                ambiguity_hits.append(f"{path.relative_to(ROOT)}:{lineno}:{line}")
    if ambiguity_hits:
        fail(
            "worker descendant boundary must name threads or panes:\n"
            + "\n".join(ambiguity_hits)
        )

    require_strings(
        ROOT / "scripts" / "install.sh",
        ("AGENTS_HOME_DIR", "has_codex_dependency", "npx skills@latest add"),
        "Codex dependency discovery",
    )

    frontier_refs = (
        codex_root / "references" / "frontier-lanes.md",
        claude_root / "references" / "frontier-lanes.md",
    )
    claude_frontier = frontier_refs[1].read_text()
    for required in ("runtime 是 lane-local routing", "不需要逐 lane 询问用户"):
        if required not in claude_frontier:
            fail(f"Claude frontier contract missing runtime routing: {required}")

    for path in (CODEX_SKILL, CLAUDE_SKILL):
        if "references/frontier-lanes.md" not in path.read_text():
            fail(
                "skill does not load frontier/lane contract: "
                f"{path.relative_to(ROOT)}"
            )

    context = (ROOT / "CONTEXT.md").read_text()
    for required in ("Execution lane", "Lane ID", "Terminal fan-in"):
        if required not in context:
            fail(f"CONTEXT missing lane vocabulary: {required}")

    claude_placement = (
        claude_root / "references" / "herdr-pane-placement.md"
    ).read_text()
    for required in ("L1(#", "X-L1"):
        if required not in claude_placement:
            fail(f"Claude pane placement missing lane label: {required}")

    lane_packets = (
        codex_root / "assets" / "ISSUE_IMPLEMENT_DISPATCH_PACKET.md",
        claude_root / "assets" / "ISSUE_IMPLEMENT_DISPATCH_PACKET.md",
        claude_root / "assets" / "CODEX_PANE_DISPATCH_PACKET.md",
    )
    for path in lane_packets:
        content = path.read_text()
        for required in ("Lane ID", "terminal"):
            if required.lower() not in content.lower():
                fail(
                    "execution dispatch packet missing lane invariant in "
                    f"{path.relative_to(ROOT)}: {required}"
                )

    active_docs = [
        ROOT / "README.md",
        ROOT / "README.zh-CN.md",
        ROOT / "CONTEXT.md",
        *codex_root.rglob("*.md"),
        *claude_root.rglob("*.md"),
        *(ROOT / "claude" / "agents").glob("wayfinder-*.md"),
    ]
    legacy_patterns = (
        re.compile(r"只有用户明确(?:要求并行|选择)"),
        re.compile(r"explicitly requested parallel", re.IGNORECASE),
        re.compile(r"explicitly selects?", re.IGNORECASE),
        re.compile(r"(?:整个|entire)\s*(?:冻结\s*)?queue", re.IGNORECASE),
        re.compile(r"--status\s+idle"),
        re.compile(r"每次\s*5\s*分钟检查"),
        re.compile(r"5\s*分钟检查(?:清单|照常|时)"),
    )
    legacy_hits = []
    for path in active_docs:
        for lineno, line in enumerate(path.read_text().splitlines(), 1):
            if any(pattern.search(line) for pattern in legacy_patterns):
                legacy_hits.append(f"{path.relative_to(ROOT)}:{lineno}:{line}")
    if legacy_hits:
        fail(
            "legacy serial/polling execution contract remains:\n"
            + "\n".join(legacy_hits)
        )

    for path in (
        codex_root / "references" / "child-monitoring.md",
        claude_root / "references" / "child-monitoring.md",
    ):
        content = path.read_text().lower()
        for required in ("terminal fan-in", "watchdog"):
            if required not in content:
                fail(
                    "monitoring contract missing terminal-only behavior in "
                    f"{path.relative_to(ROOT)}: {required}"
                )


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
    check_codex_project_targeting()
    check_frontier_lane_basics()
    check_extended_contracts()

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
