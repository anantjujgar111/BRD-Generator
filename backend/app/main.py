import shutil
import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .config import settings
from .models import (
    HealthResponse,
    SectionApproval,
    UploadResponse,
    WorkflowListResponse,
    WorkflowResponse,
    WorkflowSection,
    WorkflowStatus,
)
from .workflow.graph import build_workflow_graph
from .workflow.sections import BRD_SECTIONS

app = FastAPI(title="BRD Generator API", version="0.1.0")
workflow_graph = build_workflow_graph()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _thread_config(workflow_id: str) -> dict:
    return {"configurable": {"thread_id": workflow_id}}


def _serialize_state(workflow_id: str, state: dict) -> WorkflowResponse:
    sections = [WorkflowSection(**section) for section in state.get("sections", [])]
    index = state.get("current_section_index", 0)
    status_value = state.get("status", "pending")
    try:
        status = WorkflowStatus(status_value)
    except ValueError:
        status = WorkflowStatus.GENERATING

    if status_value == "awaiting_approval":
        status = WorkflowStatus.AWAITING_APPROVAL
    elif status_value == "completed":
        status = WorkflowStatus.COMPLETED
    elif status_value == "failed":
        status = WorkflowStatus.FAILED
    elif status_value in {"parsed", "chunked", "generating", "regenerate", "sections_complete"}:
        status = WorkflowStatus.GENERATING

    pending = None
    if status == WorkflowStatus.AWAITING_APPROVAL and index < len(BRD_SECTIONS):
        section_id = BRD_SECTIONS[index].lower().replace(" ", "-")
        pending = next((section for section in sections if section.id == section_id), None)

    preview = state.get("raw_text", "")
    if preview:
        preview = preview[:500]

    return WorkflowResponse(
        workflow_id=workflow_id,
        status=status,
        filename=state.get("filename", ""),
        current_section_index=index,
        total_sections=len(BRD_SECTIONS),
        sections=sections,
        pending_section=pending,
        output_path=state.get("output_path"),
        error=state.get("error"),
        parsed_preview=preview,
        chunk_count=len(state.get("chunks", [])),
    )


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="brd-generator-backend")


@app.post("/api/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)) -> UploadResponse:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".pdf", ".docx", ".txt"}:
        raise HTTPException(status_code=400, detail="Supported formats: PDF, DOCX, TXT")

    workflow_id = str(uuid.uuid4())
    destination = settings.upload_dir / f"{workflow_id}{suffix}"
    with destination.open("wb") as handle:
        shutil.copyfileobj(file.file, handle)

    initial_state = {
        "workflow_id": workflow_id,
        "filename": file.filename or destination.name,
        "file_path": str(destination),
        "status": "pending",
        "sections": [],
        "current_section_index": 0,
    }
    workflow_graph.invoke(initial_state, _thread_config(workflow_id))

    return UploadResponse(
        workflow_id=workflow_id,
        filename=file.filename or destination.name,
        message="Document uploaded and workflow started",
    )


@app.get("/api/workflows", response_model=WorkflowListResponse)
def list_workflows() -> WorkflowListResponse:
    # MemorySaver does not expose enumeration; return empty list for now.
    return WorkflowListResponse(workflows=[])


@app.get("/api/workflow/{workflow_id}", response_model=WorkflowResponse)
def get_workflow(workflow_id: str) -> WorkflowResponse:
    snapshot = workflow_graph.get_state(_thread_config(workflow_id))
    if not snapshot or not snapshot.values:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return _serialize_state(workflow_id, snapshot.values)


@app.post("/api/workflow/{workflow_id}/approve", response_model=WorkflowResponse)
def approve_section(workflow_id: str, approval: SectionApproval) -> WorkflowResponse:
    snapshot = workflow_graph.get_state(_thread_config(workflow_id))
    if not snapshot or not snapshot.values:
        raise HTTPException(status_code=404, detail="Workflow not found")

    decision = "approve" if approval.approved else "reject"
    workflow_graph.update_state(
        _thread_config(workflow_id),
        {"approval_decision": decision, "approval_feedback": approval.feedback},
    )
    workflow_graph.invoke(None, _thread_config(workflow_id))

    updated = workflow_graph.get_state(_thread_config(workflow_id))
    return _serialize_state(workflow_id, updated.values)


@app.get("/api/workflow/{workflow_id}/download")
def download_brd(workflow_id: str):
    snapshot = workflow_graph.get_state(_thread_config(workflow_id))
    if not snapshot or not snapshot.values:
        raise HTTPException(status_code=404, detail="Workflow not found")

    output_path = snapshot.values.get("output_path")
    if not output_path or not Path(output_path).exists():
        raise HTTPException(status_code=400, detail="BRD is not ready for download")

    return FileResponse(
        path=output_path,
        filename=f"BRD-{workflow_id}.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
