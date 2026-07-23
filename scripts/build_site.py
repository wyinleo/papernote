#!/usr/bin/env python3
"""Build the dependency-free papernote site data from repository caches."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "papers" / "index.jsonl"
WEEKLY_ROOT = ROOT / "weekly"
VIEWPOINTS_PATH = ROOT / "industry" / "viewpoints.json"
OUTPUT_PATH = ROOT / "site" / "data.js"

FIELD_ALIASES = {
    "方向": "direction",
    "关键词": "keywords",
    "作者与单位": "author_affiliations",
    "单位与作者": "author_affiliations",
    "出处与状态": "venue_status",
    "公开或更新时间": "public_date",
    "标识符": "original_links",
    "原文链接": "original_links",
    "核心问题": "question",
    "方法与贡献": "method",
    "方法示例": "method_example",
    "实验与证据": "evidence",
    "局限与风险": "limitations",
    "实践关系": "practice",
    "推荐理由": "recommendation",
    "事实与主张边界": "claim_boundary",
}

THEME_RULES = [
    (
        "mobile-security",
        "移动与身份安全",
        {"mobile-security", "android", "ios", "sideloading", "web-to-app-tracking",
         "passkeys", "webauthn", "authentication"},
    ),
    (
        "agent-security",
        "智能体与大模型安全",
        {"agent-security", "multi-agent-security", "agent-memory", "persistent-memory",
         "self-hosted-agent", "rag-security", "indirect-prompt-injection",
         "prompt-injection", "adaptive-red-teaming", "llm-security", "web-agent",
         "coding-agent"},
    ),
    (
        "systems-security",
        "系统、固件与侧信道",
        {"operating-system-security", "embedded-security", "firmware-fuzzing",
         "em-side-channel", "network-side-channel"},
    ),
    (
        "application-security",
        "应用与协议安全",
        {"application-security", "program-analysis", "api-misuse", "protocol-security",
         "desynchronization", "tls", "software-supply-chain", "secure-code-generation"},
    ),
]


def normalize_title(value: str) -> str:
    value = value.casefold().replace("’", "'").replace("–", "-").replace("—", "-")
    return " ".join(re.findall(r"[\w]+", value, flags=re.UNICODE))


def text_only(value: str) -> str:
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"\1", value)
    value = value.replace("`", "")
    return re.sub(r"\s+", " ", value).strip()


def extract_links(value: str) -> list[dict[str, str]]:
    links = [
        {"label": text_only(label), "url": url}
        for label, url in re.findall(r"\[([^\]]+)\]\((https?://[^)]+)\)", value)
    ]
    if links:
        return links
    return [
        {"label": "原文", "url": url}
        for url in re.findall(r"https?://[^\s；]+", value)
    ]


def load_index() -> list[dict[str, Any]]:
    papers = []
    for line_number, raw in enumerate(INDEX_PATH.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            papers.append(json.loads(raw))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{INDEX_PATH}:{line_number}: {exc}") from exc
    return papers


def parse_weekly_cache() -> dict[str, dict[str, Any]]:
    cached: dict[str, dict[str, Any]] = {}
    heading = re.compile(r"^###\s+\d+\.\s+(.+?)\s*$", re.MULTILINE)
    field_line = re.compile(r"^-\s+\*\*(.+?)\*\*：\s*(.*)$")
    list_item = re.compile(r"^\s{2,}-\s+(.+?)\s*$")

    for path in sorted(WEEKLY_ROOT.glob("*/*.md")):
        content = path.read_text(encoding="utf-8")
        matches = list(heading.finditer(content))
        for index, match in enumerate(matches):
            title = text_only(match.group(1))
            end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
            block = content[match.end():end]
            fields: dict[str, Any] = {
                "cache_path": path.relative_to(ROOT).as_posix(),
                "week": path.stem,
            }
            current_key = ""
            for raw_line in block.splitlines():
                found = field_line.match(raw_line)
                if found:
                    label, value = found.groups()
                    current_key = FIELD_ALIASES.get(label.strip(), "")
                    if current_key:
                        fields[current_key] = (
                            extract_links(value)
                            if current_key == "original_links"
                            else text_only(value)
                        )
                elif current_key and (item := list_item.match(raw_line)):
                    item_text = text_only(item.group(1))
                    existing = fields.get(current_key, "")
                    fields[current_key] = "；".join(filter(None, (existing, item_text)))
                elif current_key and raw_line.strip() and not raw_line.startswith(("#", "-", "|")):
                    if isinstance(fields.get(current_key), str):
                        fields[current_key] += " " + text_only(raw_line)
            cached[normalize_title(title)] = fields
    return cached


def choose_theme(topics: list[str]) -> tuple[str, str]:
    topic_set = set(topics)
    for theme_id, label, signals in THEME_RULES:
        if topic_set & signals:
            return theme_id, label
    return "other-security", "其他安全研究"


def iso_week(date_value: str) -> str:
    date = dt.date.fromisoformat(date_value)
    year, week, _ = date.isocalendar()
    return f"{year}-W{week:02d}"


def build_payload() -> dict[str, Any]:
    papers = load_index()
    cache = parse_weekly_cache()
    week_counts: dict[str, int] = {}
    theme_counts: dict[str, dict[str, Any]] = {}

    for paper in papers:
        note_path = (paper.get("weekly_notes") or [""])[-1]
        week = Path(note_path).stem if note_path else iso_week(paper["first_seen"])
        theme_id, theme_label = choose_theme(paper.get("topics", []))
        details = cache.get(normalize_title(paper["title"]), {})

        paper["week"] = week
        paper["theme"] = theme_id
        paper["theme_label"] = theme_label
        paper["cached"] = bool(details)
        paper["details"] = details
        paper["primary_url"] = (paper.get("urls") or [""])[0]

        week_counts[week] = week_counts.get(week, 0) + 1
        theme = theme_counts.setdefault(theme_id, {"id": theme_id, "label": theme_label, "count": 0})
        theme["count"] += 1

    papers.sort(key=lambda item: (item["first_seen"], item["title"]), reverse=True)
    weeks = [
        {"id": week, "label": week, "count": count}
        for week, count in sorted(week_counts.items(), reverse=True)
    ]
    themes = sorted(theme_counts.values(), key=lambda item: (-item["count"], item["label"]))
    viewpoints = json.loads(VIEWPOINTS_PATH.read_text(encoding="utf-8"))

    return {
        "generated_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "counts": {
            "papers": len(papers),
            "weeks": len(weeks),
            "themes": len(themes),
            "viewpoints": len(viewpoints),
            "cached": sum(1 for paper in papers if paper["cached"]),
        },
        "weeks": weeks,
        "themes": themes,
        "papers": papers,
        "viewpoints": viewpoints,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    args = parser.parse_args()

    payload = build_payload()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    args.output.write_text(
        "/* Generated by scripts/build_site.py. Do not edit by hand. */\n"
        f"window.PAPERNOTE_DATA={serialized};\n",
        encoding="utf-8",
    )
    print(
        f"Built {args.output.relative_to(ROOT)}: "
        f"{payload['counts']['papers']} papers, "
        f"{payload['counts']['cached']} cached summaries, "
        f"{payload['counts']['viewpoints']} viewpoints."
    )


if __name__ == "__main__":
    main()
