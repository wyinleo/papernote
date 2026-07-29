#!/usr/bin/env python3
"""Build the dependency-free papernote site data from repository caches."""

from __future__ import annotations

import argparse
import datetime as dt
import itertools
import json
import re
import unicodedata
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "papers" / "index.jsonl"
WEEKLY_ROOT = ROOT / "weekly"
VIEWPOINTS_PATH = ROOT / "industry" / "viewpoints.json"
VIEWPOINT_SOURCES_PATH = ROOT / "industry" / "sources.json"
GRAPH_PATH = ROOT / "papers" / "academic_graph.json"
TAXONOMY_PATH = ROOT / "papers" / "topic_taxonomy.json"
ENTITY_REGISTRY_PATH = ROOT / "papers" / "entity_registry.json"
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

TOP_VENUE_GROUPS = {
    "security": {
        "label": "网络与信息安全",
        "signals": ("usenix security", "ieee s&p", "ieee symposium on security and privacy",
                    "acm ccs", "computer and communications security", "ndss"),
    },
    "software": {
        "label": "软件工程/系统软件/程序设计语言",
        "signals": ("icse", "fse", "ase", "issta"),
    },
    "ai": {
        "label": "人工智能",
        "signals": ("neurips", "icml", "aaai", "ijcai", "acl", "cvpr"),
    },
}


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


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def choose_theme(paper: dict[str, Any], taxonomy: dict[str, Any]) -> tuple[str, str]:
    domains = {item["id"]: item for item in taxonomy["domains"]}
    override = taxonomy.get("primary_domain_overrides", {}).get(paper["id"])
    if override:
        if override not in domains:
            raise ValueError(f"{TAXONOMY_PATH}: unknown domain {override!r} for {paper['id']}")
        return override, domains[override]["label"]

    topic_set = set(paper.get("topics", []))
    matches = [
        domain for domain in taxonomy["domains"]
        if topic_set & set(domain.get("signals", []))
    ]
    if len(matches) != 1:
        raise ValueError(
            f"{paper['id']}: primary domain is ambiguous or missing; "
            f"add it to primary_domain_overrides"
        )
    return matches[0]["id"], matches[0]["label"]


def iso_week(date_value: str) -> str:
    date = dt.date.fromisoformat(date_value)
    year, week, _ = date.isocalendar()
    return f"{year}-W{week:02d}"


def normalize_person_name(value: str) -> str:
    value = re.sub(r"\([^)]*\)", "", value)
    value = "".join(
        char for char in unicodedata.normalize("NFKD", value)
        if not unicodedata.combining(char)
    )
    return "".join(char for char in normalize_title(value) if char.isalnum())


def registry_lookup(registry: dict[str, Any], section: str) -> dict[str, dict[str, Any]]:
    lookup: dict[str, dict[str, Any]] = {}
    for source_name, record in registry.get(section, {}).items():
        for alias in [source_name, record.get("display_name", ""), *(record.get("aliases") or [])]:
            if alias:
                lookup[alias] = record
    return lookup


def parse_affiliations(
    value: str,
    registry: dict[str, Any],
    paper_authors: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Parse, normalize and validate the institution-first weekly format."""
    rows = []
    institution_lookup = registry_lookup(registry, "institutions")
    scholar_lookup = registry_lookup(registry, "scholars")
    paper_author_keys = {normalize_person_name(item) for item in (paper_authors or [])}
    for raw in re.split(r"[；\n]+", value or ""):
        raw = raw.strip()
        if not raw or "：" not in raw:
            continue
        institution, author_text = raw.split("：", 1)
        institution = institution.strip()
        institution_record = institution_lookup.get(institution)
        if not institution_record:
            raise ValueError(
                f"Unregistered institution {institution!r}; "
                f"add a verified entry to {ENTITY_REGISTRY_PATH.relative_to(ROOT)}"
            )
        source_authors = [
            item.strip()
            for item in re.split(r"[、,]", author_text)
            if item.strip()
        ]
        authors = []
        for source_author in source_authors:
            record = scholar_lookup.get(source_author, {})
            publication_name = record.get("publication_name") or source_author
            if paper_author_keys and normalize_person_name(publication_name) not in paper_author_keys:
                raise ValueError(
                    f"Affiliation author {source_author!r} does not match the paper author list"
                )
            authors.append({
                "id": record.get("id") or f"scholar:{normalize_person_name(source_author)}",
                "name": record.get("display_name") or source_author,
                "publication_name": publication_name,
            })
        if authors:
            rows.append({
                "institution_id": institution_record["id"],
                "institution": institution_record["display_name"],
                "authors": authors,
            })
    return rows


def format_affiliations(rows: list[dict[str, Any]]) -> str:
    return "；".join(
        f"{row['institution']}：{'、'.join(author['name'] for author in row['authors'])}"
        for row in rows
    )


def accepted_venue_group(paper: dict[str, Any]) -> str | None:
    status = str(paper.get("status", "")).casefold()
    if "accepted" not in status:
        return None
    venue_text = " ".join(paper.get("venues") or []).casefold()
    for group_id, group in TOP_VENUE_GROUPS.items():
        if any(signal in venue_text for signal in group["signals"]):
            return group_id
    return None


def publication_year(paper: dict[str, Any]) -> int:
    venue_text = " ".join(paper.get("venues") or [])
    match = re.search(r"\b(20\d{2})\b", venue_text)
    if match:
        return int(match.group(1))
    return int(str(paper.get("first_seen", dt.date.today().isoformat()))[:4])


def build_academic_graph(
    papers: list[dict[str, Any]],
    registry: dict[str, Any],
) -> dict[str, Any]:
    institutions: dict[str, dict[str, Any]] = {}
    scholars: dict[str, dict[str, Any]] = {}
    collaborations: dict[tuple[str, str], dict[str, Any]] = {}
    publications = []

    for paper in papers:
        affiliations = parse_affiliations(
            paper.get("details", {}).get("author_affiliations", ""),
            registry,
            paper.get("authors", []),
        )
        if not affiliations:
            continue
        year = publication_year(paper)
        venue_group = accepted_venue_group(paper)
        publication = {
            "id": paper["id"],
            "title": paper["title"],
            "year": year,
            "venue": (paper.get("venues") or [""])[0],
            "venue_group": venue_group,
            "status": paper.get("status", ""),
            "institutions": [row["institution_id"] for row in affiliations],
            "authors": [author["id"] for row in affiliations for author in row["authors"]],
        }
        publications.append(publication)

        scored_institutions: set[str] = set()
        scored_scholars: set[str] = set()
        for row in affiliations:
            institution_id = row["institution_id"]
            institution_name = row["institution"]
            entry = institutions.setdefault(institution_id, {
                "id": institution_id,
                "name": institution_name,
                "papers": set(),
                "scholars": set(),
                "annual_scores": {},
            })
            entry["papers"].add(paper["id"])
            entry["scholars"].update(author["name"] for author in row["authors"])
            if venue_group and institution_id not in scored_institutions:
                annual = entry["annual_scores"].setdefault(str(year), {
                    "security": 0,
                    "software": 0,
                    "ai": 0,
                    "total": 0,
                })
                annual[venue_group] += 1
                annual["total"] += 1
                scored_institutions.add(institution_id)

            for author in row["authors"]:
                author_id = author["id"]
                scholar = scholars.setdefault(author_id, {
                    "id": author_id,
                    "name": author["name"],
                    "publication_name": author["publication_name"],
                    "institutions": set(),
                    "papers": set(),
                    "annual_scores": {},
                })
                scholar["institutions"].add(institution_name)
                scholar["papers"].add(paper["id"])
                if venue_group and author_id not in scored_scholars:
                    annual = scholar["annual_scores"].setdefault(str(year), {
                        "security": 0,
                        "software": 0,
                        "ai": 0,
                        "total": 0,
                    })
                    annual[venue_group] += 1
                    annual["total"] += 1
                    scored_scholars.add(author_id)

        institution_ids = sorted({row["institution_id"] for row in affiliations})
        for left, right in itertools.combinations(institution_ids, 2):
            edge = collaborations.setdefault((left, right), {
                "source": left,
                "target": right,
                "papers": [],
            })
            edge["papers"].append({
                "id": paper["id"],
                "year": year,
                "venue_group": venue_group,
            })

    def finalize_node(node: dict[str, Any], collection_key: str) -> dict[str, Any]:
        annual_scores = node["annual_scores"]
        return {
            **node,
            collection_key: sorted(node[collection_key]),
            "papers": sorted(node["papers"]),
            "verified_score": sum(item["total"] for item in annual_scores.values()),
        }

    institution_rows = [
        finalize_node(node, "scholars")
        for node in institutions.values()
    ]
    scholar_rows = [
        finalize_node(node, "institutions")
        for node in scholars.values()
    ]
    institution_rows.sort(key=lambda item: (-item["verified_score"], -len(item["papers"]), item["name"]))
    scholar_rows.sort(key=lambda item: (-item["verified_score"], -len(item["papers"]), item["name"]))
    collaboration_rows = [
        {**edge, "weight": len(edge["papers"])}
        for edge in collaborations.values()
    ]
    collaboration_rows.sort(key=lambda item: (-item["weight"], item["source"], item["target"]))

    years = sorted(
        {str(item["year"]) for item in publications if item["venue_group"]},
        reverse=True,
    )
    return {
        "generated_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "coverage": {
            "basis": "papernote 已收录且周报中具有可解析“单位与作者”字段的论文",
            "score_definition": "年度评价分数为库内经正式接收核验的网络与信息安全、软件工程/系统软件/程序设计语言、人工智能领域 CCF-A 会议论文数；当前是已核验下界，不代表单位完整产出。",
            "indexed_papers": len(papers),
            "papers_with_affiliations": len(publications),
            "scored_top_venue_papers": sum(1 for item in publications if item["venue_group"]),
        },
        "categories": [
            {"id": group_id, "label": group["label"]}
            for group_id, group in TOP_VENUE_GROUPS.items()
        ],
        "years": years,
        "institutions": institution_rows,
        "scholars": scholar_rows,
        "collaborations": collaboration_rows,
        "publications": publications,
    }


def build_payload() -> dict[str, Any]:
    papers = load_index()
    cache = parse_weekly_cache()
    taxonomy = load_json(TAXONOMY_PATH)
    registry = load_json(ENTITY_REGISTRY_PATH)
    week_counts: dict[str, int] = {}
    theme_counts: dict[str, dict[str, Any]] = {}
    known_topics = set(taxonomy["topics"])

    for paper in papers:
        unknown_topics = set(paper.get("topics", [])) - known_topics
        if unknown_topics:
            raise ValueError(
                f"{paper['id']}: unknown controlled topics {sorted(unknown_topics)}; "
                f"update {TAXONOMY_PATH.relative_to(ROOT)} before ingesting"
            )
        note_path = (paper.get("weekly_notes") or [""])[-1]
        week = Path(note_path).stem if note_path else iso_week(paper["first_seen"])
        theme_id, theme_label = choose_theme(paper, taxonomy)
        details = cache.get(normalize_title(paper["title"]), {})
        if details.get("author_affiliations"):
            details["author_affiliations"] = format_affiliations(
                parse_affiliations(
                    details["author_affiliations"],
                    registry,
                    paper.get("authors", []),
                )
            )

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
    viewpoints = load_json(VIEWPOINTS_PATH)
    viewpoint_sources = load_json(VIEWPOINT_SOURCES_PATH)
    required_viewpoint_fields = {
        "id", "title", "source", "source_type", "content_type", "published_at",
        "url", "topics", "summary", "highlights", "evidence_basis", "limitations",
        "commercial_interest",
    }
    for item in viewpoints:
        missing = required_viewpoint_fields - set(item)
        if missing:
            raise ValueError(f"{VIEWPOINTS_PATH}: {item.get('id', '<unknown>')} missing {sorted(missing)}")
    academic = build_academic_graph(papers, registry)

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
        "viewpoint_sources": viewpoint_sources,
        "academic": academic,
        "taxonomy": {
            "version": taxonomy["version"],
            "facets": taxonomy["facets"],
            "topics": taxonomy["topics"],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--check", action="store_true", help="validate inputs without writing generated files")
    args = parser.parse_args()

    payload = build_payload()
    if args.check:
        print(
            f"Validated {payload['counts']['papers']} papers, "
            f"{payload['counts']['themes']} domains and "
            f"{payload['counts']['viewpoints']} viewpoints."
        )
        return
    GRAPH_PATH.write_text(
        json.dumps(payload["academic"], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
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
        f"{payload['counts']['viewpoints']} viewpoints, "
        f"{len(payload['academic']['institutions'])} institutions."
    )


if __name__ == "__main__":
    main()
