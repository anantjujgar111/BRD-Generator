from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class WorkflowStatus(str, Enum):
    PENDING = "pending"
    PARSING = "parsing"
    GENERATING = "generating"
    AWAITING_APPROVAL = "awaiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"


class SectionApproval(BaseModel):
    approved: bool
    feedback: str | None = None


class WorkflowSection(BaseModel):
    id: str
    title: str
    content: str
    status: str = "pending"
    version: int = 1


class WorkflowResponse(BaseModel):
    workflow_id: str
    status: WorkflowStatus
    filename: str
    current_section_index: int
    total_sections: int
    sections: list[WorkflowSection]
    pending_section: WorkflowSection | None = None
    output_path: str | None = None
    error: str | None = None
    parsed_preview: str | None = None
    chunk_count: int = 0


class UploadResponse(BaseModel):
    workflow_id: str
    filename: str
    message: str


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str = "0.1.0"


class WorkflowListItem(BaseModel):
    workflow_id: str
    filename: str
    status: WorkflowStatus


class WorkflowListResponse(BaseModel):
    workflows: list[WorkflowListItem]
