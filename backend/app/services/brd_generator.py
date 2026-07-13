import logging
import re
from collections import Counter

from .claude_client import claude_client

logger = logging.getLogger(__name__)

MAX_SOURCE_CHARS = 12000


def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 150) -> list[str]:
    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        return []
    if len(normalized) <= chunk_size:
        return [normalized]

    chunks: list[str] = []
    start = 0
    while start < len(normalized):
        end = min(start + chunk_size, len(normalized))
        chunk = normalized[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(normalized):
            break
        start = max(end - overlap, start + 1)
    return chunks


def _section_id(title: str) -> str:
    return title.lower().replace(" ", "-")


def _source_excerpt(chunks: list[str]) -> str:
    combined = "\n\n".join(chunks).strip()
    if len(combined) <= MAX_SOURCE_CHARS:
        return combined
    head = combined[: int(MAX_SOURCE_CHARS * 0.7)]
    tail = combined[-int(MAX_SOURCE_CHARS * 0.3) :]
    return f"{head}\n\n...[truncated]...\n\n{tail}"


def _sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [part.strip() for part in parts if part.strip()]


def _keyword_sentences(chunks: list[str], keywords: list[str], limit: int = 5) -> list[str]:
    matches: list[str] = []
    for chunk in chunks:
        for sentence in _sentences(chunk):
            lowered = sentence.lower()
            if any(keyword in lowered for keyword in keywords):
                matches.append(sentence)
            if len(matches) >= limit:
                return matches
    return matches


def _fallback_sentences(chunks: list[str], limit: int = 4) -> list[str]:
    sentences: list[str] = []
    for chunk in chunks:
        sentences.extend(_sentences(chunk))
        if len(sentences) >= limit:
            break
    return sentences[:limit]


def _generate_section_heuristic(title: str, chunks: list[str], feedback: str | None = None) -> str:
    if not chunks:
        return f"### {title}\n\nNo source content was available to draft this section."

    keyword_map = {
        "Executive Summary": ["purpose", "scope", "objective", "summary", "overview"],
        "Business Goals": ["goal", "objective", "business", "reduce", "improve"],
        "Functional Requirements": ["requirement", "must", "shall", "feature", "process"],
        "Non-Functional Requirements": ["performance", "scalability", "security", "reliability", "quality"],
        "Constraints": ["constraint", "limit", "only", "compliance", "valid"],
        "Assumptions": ["assume", "assumption", "expected", "believe"],
        "Acceptance Criteria": ["acceptance", "criteria", "success", "validate", "ensure"],
        "Technical Specifications": ["technical", "architecture", "database", "platform", "integration"],
        "Implementation Plan": ["phase", "timeline", "deployment", "plan", "resource"],
        "Risk Assessment": ["risk", "mitigation", "impact", "probability", "challenge"],
        "Stakeholder Analysis": ["stakeholder", "owner", "analyst", "user", "team"],
        "Traceability Matrix": ["trace", "mapping", "source", "document", "requirement"],
    }

    keywords = keyword_map.get(title, ["requirement"])
    selected = _keyword_sentences(chunks, keywords) or _fallback_sentences(chunks)

    if feedback:
        selected = [f"Revision note: {feedback}", *selected[:3]]

    lines = [f"### {title}", ""]
    for index, sentence in enumerate(selected, start=1):
        prefix = {
            "Business Goals": "BG",
            "Functional Requirements": "FR",
            "Non-Functional Requirements": "NFR",
            "Constraints": "CON",
            "Assumptions": "ASM",
            "Acceptance Criteria": "AC",
        }.get(title, "ITEM")
        lines.append(f"- **{prefix}-{index:03d}**: {sentence}")

    if title == "Executive Summary":
        lines = [
            f"### {title}",
            "",
            "**Purpose**",
            selected[0] if selected else "Define the business problem and expected outcomes.",
            "",
            "**Scope**",
            selected[1] if len(selected) > 1 else "Cover end-to-end delivery of the proposed solution.",
            "",
            "**Business Objectives**",
            selected[2] if len(selected) > 2 else "Deliver measurable improvements aligned with stakeholder goals.",
        ]
    elif title == "Risk Assessment":
        lines.extend(
            [
                "",
                "| Risk | Impact | Probability | Mitigation |",
                "| --- | --- | --- | --- |",
                "| Technical complexity | High | Medium | Prototype critical integrations early |",
            ]
        )
    elif title == "Stakeholder Analysis":
        lines.extend(
            [
                "",
                "| Role | Responsibility | Interest | Influence |",
                "| --- | --- | --- | --- |",
                "| Business Owner | Sponsorship and approvals | High | High |",
            ]
        )
    elif title == "Traceability Matrix":
        top_terms = Counter(word.lower() for chunk in chunks for word in re.findall(r"[A-Za-z]{5,}", chunk))
        common = [word for word, _ in top_terms.most_common(5)]
        lines.extend(["", "| Requirement ID | Source Term |", "| --- | --- |"])
        for index, term in enumerate(common, start=1):
            lines.append(f"| REQ-{index:03d} | {term} |")

    return "\n".join(lines)


def generate_section_content(
    title: str,
    chunks: list[str],
    feedback: str | None = None,
    approved_sections: list[dict] | None = None,
    filename: str | None = None,
    previous_draft: str | None = None,
) -> str:
    if claude_client.is_configured:
        try:
            return claude_client.generate_section(
                section_title=title,
                source_excerpt=_source_excerpt(chunks),
                approved_sections=approved_sections,
                filename=filename,
                feedback=feedback,
                previous_draft=previous_draft,
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Claude generation failed for section %s: %s", title, exc)
            if not chunks:
                raise

    return _generate_section_heuristic(title, chunks, feedback=feedback)


def build_section(title: str, content: str, status: str = "pending", version: int = 1) -> dict:
    return {
        "id": _section_id(title),
        "title": title,
        "content": content,
        "status": status,
        "version": version,
    }
