# BRD Generator

LangGraph-based Business Requirements Document (BRD) generator with a FastAPI backend and Streamlit frontend.

## Features

- Upload source documents in **PDF**, **DOCX**, or **TXT** format
- Automatic document parsing and chunking
- LangGraph workflow with nodes and edges
- Human-in-the-loop (HITL) approval for each generated BRD section
- Compile and download the final BRD as a Word document

## Prerequisites

- Python 3.11+

## Quick Start

```bash
chmod +x scripts/setup.sh scripts/dev.sh
./scripts/setup.sh
./scripts/dev.sh
```

- Streamlit UI: http://127.0.0.1:8501
- Backend API: http://127.0.0.1:8000
- Health check: http://127.0.0.1:8000/health

## Manual Start

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend (Streamlit)

```bash
source backend/.venv/bin/activate
pip install -r frontend/requirements.txt
cd frontend
streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

## Workflow

1. Upload a source document in the Streamlit UI.
2. The backend parses and chunks the content via LangGraph nodes.
3. Each BRD section is generated and paused for human approval.
4. Approve or reject sections with optional feedback.
5. After all sections are approved, download the compiled BRD `.docx`.

## Project Structure

```
backend/     FastAPI + LangGraph workflow
frontend/    Streamlit UI (app.py)
scripts/     setup and development helpers
```

## Environment Variables

| Variable | Default | Description |
| --- | --- | --- |
| `BRD_UPLOAD_DIR` | `data/uploads` | Uploaded source documents |
| `BRD_OUTPUT_DIR` | `data/outputs` | Generated BRD files |
| `BRD_CORS_ORIGINS` | `http://localhost:8501` | Allowed frontend origins |
| `BRD_API_BASE` | `http://127.0.0.1:8000` | Backend URL used by Streamlit |
