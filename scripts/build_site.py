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
    "名词解释": "glossary",
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
        "label": "软件工程与系统",
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


def parse_glossary(value: str | list[str], source: str) -> list[dict[str, str]]:
    entries = []
    seen_terms = set()
    raw_entries = value if isinstance(value, list) else value.split("；")
    for raw_entry in raw_entries:
        raw_entry = raw_entry.strip()
        if not raw_entry:
            continue
        term, separator, definition = raw_entry.partition("：")
        if not separator or not term.strip() or not definition.strip():
            raise ValueError(f"{source}: glossary entry must use '术语：解释': {raw_entry!r}")
        normalized_term = term.strip().casefold()
        if normalized_term in seen_terms:
            raise ValueError(f"{source}: duplicate glossary term {term.strip()!r}")
        seen_terms.add(normalized_term)
        entries.append({"term": term.strip(), "definition": definition.strip()})
    if not 1 <= len(entries) <= 5:
        raise ValueError(f"{source}: glossary must contain 1-5 entries, found {len(entries)}")
    return entries


def validate_public_date(value: str, source: str) -> None:
    """Keep discovery notes separate from the public version timeline."""
    entry_pattern = re.compile(
        r"^\d{4}(?:-\d{2}(?:-\d{2})?)?(?: \d{2}:\d{2})? "
        r"(?:预印版本|正式发表)$"
    )
    entries = [entry.strip() for entry in value.split("；") if entry.strip()]
    if not entries or any(not entry_pattern.fullmatch(entry) for entry in entries):
        raise ValueError(
            f"{source}: public date must use '时间 预印版本' or "
            f"'时间 正式发表': {value!r}"
        )


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
                    if current_key == "glossary":
                        existing = fields.get(current_key)
                        fields[current_key] = [
                            *(existing if isinstance(existing, list) else []),
                            item_text,
                        ]
                    else:
                        existing = fields.get(current_key, "")
                        fields[current_key] = "；".join(filter(None, (existing, item_text)))
                elif current_key and raw_line.strip() and not raw_line.startswith(("#", "-", "|")):
                    if isinstance(fields.get(current_key), str):
                        fields[current_key] += " " + text_only(raw_line)
            if fields.get("glossary"):
                fields["glossary"] = parse_glossary(
                    fields["glossary"],
                    f"{path.relative_to(ROOT)}: {title}",
                )
            validate_public_date(
                fields.get("public_date", ""),
                f"{path.relative_to(ROOT)}: {title}",
            )
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
    records = registry.get(section, {})
    # Canonical source keys must win over display-name and alias collisions. This
    # lets an existing exact-name entity remain stable when a same-name scholar
    # is added under a qualified key and selected via a paper-level override.
    lookup: dict[str, dict[str, Any]] = dict(records)
    for record in records.values():
        for alias in [record.get("display_name", ""), *(record.get("aliases") or [])]:
            if alias:
                lookup.setdefault(alias, record)
    return lookup


def validate_entity_registry(registry: dict[str, Any]) -> None:
    """Fail closed on incomplete or unsupported public entity metadata."""
    for source_name, record in registry.get("institutions", {}).items():
        missing = {"id", "display_name", "language"} - set(record)
        if missing:
            raise ValueError(
                f"{ENTITY_REGISTRY_PATH.relative_to(ROOT)}: institution "
                f"{source_name!r} missing {sorted(missing)}"
            )
    for source_name, record in registry.get("scholars", {}).items():
        missing = {"id", "display_name", "publication_name", "language"} - set(record)
        if missing:
            raise ValueError(
                f"{ENTITY_REGISTRY_PATH.relative_to(ROOT)}: scholar "
                f"{source_name!r} missing {sorted(missing)}"
            )
        for field in ("homepage", "source"):
            value = record.get(field, "")
            if value and not re.match(r"^https?://", value):
                raise ValueError(
                    f"{ENTITY_REGISTRY_PATH.relative_to(ROOT)}: scholar "
                    f"{source_name!r} has invalid {field} URL"
                )
        if (
            str(record["language"]).startswith("zh")
            and record["display_name"] != record["publication_name"]
            and not record.get("source")
        ):
            raise ValueError(
                f"{ENTITY_REGISTRY_PATH.relative_to(ROOT)}: translated scholar "
                f"{source_name!r} requires a verification source"
            )
    scholars = registry.get("scholars", {})
    for paper_id, overrides in registry.get("paper_scholar_overrides", {}).items():
        if not isinstance(overrides, dict):
            raise ValueError(
                f"{ENTITY_REGISTRY_PATH.relative_to(ROOT)}: scholar overrides for "
                f"{paper_id!r} must be an object"
            )
        for publication_name, scholar_key in overrides.items():
            if scholar_key not in scholars:
                raise ValueError(
                    f"{ENTITY_REGISTRY_PATH.relative_to(ROOT)}: scholar override "
                    f"{paper_id!r}/{publication_name!r} references unknown key {scholar_key!r}"
                )
            if normalize_person_name(scholars[scholar_key]["publication_name"]) != normalize_person_name(publication_name):
                raise ValueError(
                    f"{ENTITY_REGISTRY_PATH.relative_to(ROOT)}: scholar override "
                    f"{paper_id!r}/{publication_name!r} has a mismatched publication name"
                )


def parse_affiliations(
    value: str,
    registry: dict[str, Any],
    paper_authors: list[str] | None = None,
    paper_id: str = "",
) -> list[dict[str, Any]]:
    """Parse, normalize and validate the institution-first weekly format."""
    rows = []
    institution_lookup = registry_lookup(registry, "institutions")
    scholar_lookup = registry_lookup(registry, "scholars")
    scholar_overrides = registry.get("paper_scholar_overrides", {}).get(paper_id, {})
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
            override_key = scholar_overrides.get(source_author)
            record = (
                registry.get("scholars", {}).get(override_key, {})
                if override_key
                else scholar_lookup.get(source_author, {})
            )
            publication_name = record.get("publication_name") or source_author
            if paper_author_keys and normalize_person_name(publication_name) not in paper_author_keys:
                raise ValueError(
                    f"Affiliation author {source_author!r} does not match the paper author list"
                )
            authors.append({
                "id": record.get("id") or f"scholar:{normalize_person_name(source_author)}",
                "name": record.get("display_name") or source_author,
                "publication_name": publication_name,
                "homepage": record.get("homepage", ""),
                "profile_source": record.get("source", ""),
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
            paper.get("id", ""),
        )
        if not affiliations:
            continue
        year = publication_year(paper)
        venue_group = accepted_venue_group(paper)
        affiliated_author_ids = list(dict.fromkeys(
            author["id"] for row in affiliations for author in row["authors"]
        ))
        author_id_by_publication_name = {
            normalize_person_name(author["publication_name"]): author["id"]
            for row in affiliations
            for author in row["authors"]
        }
        publication_author_ids = list(dict.fromkeys(
            author_id_by_publication_name[normalize_person_name(author)]
            for author in paper.get("authors", [])
            if normalize_person_name(author) in author_id_by_publication_name
        ))
        publication_author_ids.extend(
            author_id for author_id in affiliated_author_ids
            if author_id not in publication_author_ids
        )
        publication = {
            "id": paper["id"],
            "title": paper["title"],
            "year": year,
            "venue": (paper.get("venues") or [""])[0],
            "venue_group": venue_group,
            "status": paper.get("status", ""),
            "first_seen": paper.get("first_seen", ""),
            "url": paper.get("primary_url") or ((paper.get("urls") or [""])[0]),
            "institutions": list(dict.fromkeys(
                row["institution_id"] for row in affiliations
            )),
            "authors": publication_author_ids,
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
                    "homepage": author["homepage"],
                    "profile_source": author["profile_source"],
                    "institutions": set(),
                    "papers": set(),
                    "annual_scores": {},
                })
                if author["homepage"] and not scholar["homepage"]:
                    scholar["homepage"] = author["homepage"]
                    scholar["profile_source"] = author["profile_source"]
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

    publication_lookup = {item["id"]: item for item in publications}

    def finalize_node(node: dict[str, Any], collection_key: str) -> dict[str, Any]:
        annual_scores = node["annual_scores"]
        result = {
            **node,
            collection_key: sorted(node[collection_key]),
            "papers": sorted(node["papers"]),
            "verified_score": sum(item["total"] for item in annual_scores.values()),
        }
        if collection_key == "institutions":
            recent_papers = sorted(
                (publication_lookup[paper_id] for paper_id in node["papers"]),
                key=lambda item: (item.get("first_seen", ""), item["year"], item["title"]),
                reverse=True,
            )[:3]
            result["recent_papers"] = [
                {
                    "id": paper["id"],
                    "title": paper["title"],
                    "year": paper["year"],
                    "venue": paper["venue"],
                    "url": paper["url"],
                }
                for paper in recent_papers
            ]
        return result

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
            "score_definition": "年度评价分数为库内经正式接收核验的网络与信息安全、软件工程与系统、人工智能领域 CCF-A 会议论文数；当前是已核验下界，不代表单位完整产出。",
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
    validate_entity_registry(registry)
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
        if not details.get("glossary"):
            raise ValueError(
                f"{paper['id']}: cached weekly entry must include 1-5 glossary explanations"
            )
        if details.get("author_affiliations"):
            details["author_affiliations"] = format_affiliations(
                parse_affiliations(
                    details["author_affiliations"],
                    registry,
                    paper.get("authors", []),
                    paper.get("id", ""),
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
    viewpoints.sort(key=lambda item: (item["published_at"], item["id"]), reverse=True)
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
