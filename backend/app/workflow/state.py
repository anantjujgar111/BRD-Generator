from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


def merge_sections(existing: list[dict], updates: list[dict]) -> list[dict]:
    if not updates:
        return existing
    merged = list(existing)
    index_by_id = {section["id"]: idx for idx, section in enumerate(merged)}
    for section in updates:
        section_id = section["id"]
        if section_id in index_by_id:
            merged[index_by_id[section_id]] = section
        else:
            merged.append(section)
    return merged


class WorkflowState(TypedDict, total=False):
    workflow_id: str
    filename: str
    file_path: str
    raw_text: str
    chunks: list[str]
    sections: Annotated[list[dict], merge_sections]
    section_titles: list[str]
    current_section_index: int
    status: str
    approval_decision: str | None
    approval_feedback: str | None
    output_path: str | None
    error: str | None
    messages: Annotated[list, add_messages]
