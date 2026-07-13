from __future__ import annotations

from anthropic import Anthropic

from ..config import settings

SECTION_GUIDANCE: dict[str, str] = {
    "Executive Summary": (
        "Write Purpose, Scope, and Business Objectives subsections derived from the source material."
    ),
    "Business Goals": (
        "List numbered business goals (BG-001, BG-002, ...) with description, priority, and source reference when available."
    ),
    "Functional Requirements": (
        "List functional requirements (FR-001, FR-002, ...) with description, priority, and source reference."
    ),
    "Non-Functional Requirements": (
        "List non-functional requirements (NFR-001, ...) covering quality attributes like scalability, security, and reliability."
    ),
    "Constraints": (
        "List project constraints (CON-001, ...) that limit design or implementation choices."
    ),
    "Assumptions": (
        "List assumptions (ASM-001, ...) or state clearly if none are identified in the source."
    ),
    "Acceptance Criteria": (
        "List acceptance criteria (AC-001, ...) that define when the solution is complete."
    ),
    "Technical Specifications": (
        "Describe architecture, integrations, data stores, and technical constraints inferred from the source."
    ),
    "Implementation Plan": (
        "Provide phases, timeline guidance, and required resources for delivery."
    ),
    "Risk Assessment": (
        "Provide a markdown table with columns: Risk, Impact, Probability, Mitigation."
    ),
    "Stakeholder Analysis": (
        "Provide a markdown table with columns: Role, Responsibility, Interest, Influence."
    ),
    "Traceability Matrix": (
        "Provide a markdown table mapping requirement IDs to source references from the uploaded document."
    ),
}


def _build_prompt(
    section_title: str,
    source_excerpt: str,
    approved_sections: list[dict],
    filename: str | None,
    feedback: str | None,
    previous_draft: str | None,
) -> str:
    approved_context = ""
    if approved_sections:
        snippets = []
        for section in approved_sections[-4:]:
            snippets.append(f"### {section['title']}\n{section['content'][:1200]}")
        approved_context = "\n\n".join(snippets)

    revision_notes = ""
    if feedback:
        revision_notes = f"\nHuman revision feedback (address this):\n{feedback}\n"
    if previous_draft:
        revision_notes += f"\nPrevious draft to improve:\n{previous_draft}\n"

    guidance = SECTION_GUIDANCE.get(section_title, "Write a clear, professional BRD section.")

    return f"""You are a senior business analyst drafting a Business Requirements Document (BRD).

Source document: {filename or "uploaded document"}

Source excerpts:
{source_excerpt}

Already approved BRD sections:
{approved_context or "None yet."}

Task: Draft only the "{section_title}" section.
{revision_notes}
Section requirements:
{guidance}

Rules:
- Use only information supported by the source excerpts and approved sections.
- Do not invent specific systems, dates, or compliance claims unless present in the source.
- Use professional markdown.
- Start with a level-3 heading: ### {section_title}
- Be specific and structured; avoid generic filler.
- Do not include sections other than "{section_title}".
"""


class ClaudeClient:
    def __init__(self) -> None:
        api_key = settings.resolved_anthropic_api_key
        self._client = Anthropic(api_key=api_key) if api_key else None
        self._model = settings.claude_model
        self._max_tokens = settings.claude_max_tokens

    @property
    def is_configured(self) -> bool:
        return self._client is not None

    def generate_section(
        self,
        section_title: str,
        source_excerpt: str,
        approved_sections: list[dict] | None = None,
        filename: str | None = None,
        feedback: str | None = None,
        previous_draft: str | None = None,
    ) -> str:
        if not self._client:
            raise RuntimeError("Anthropic API key is not configured")

        prompt = _build_prompt(
            section_title=section_title,
            source_excerpt=source_excerpt,
            approved_sections=approved_sections or [],
            filename=filename,
            feedback=feedback,
            previous_draft=previous_draft,
        )

        response = self._client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            system=(
                "You produce precise BRD content for enterprise software projects. "
                "Output markdown only."
            ),
            messages=[{"role": "user", "content": prompt}],
        )

        text_parts = [block.text for block in response.content if block.type == "text"]
        content = "\n".join(part.strip() for part in text_parts if part.strip()).strip()
        if not content:
            raise RuntimeError("Claude returned an empty section")
        return content


claude_client = ClaudeClient()
