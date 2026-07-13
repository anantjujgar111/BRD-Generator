# BRD Generator

LangGraph-based Business Requirements Document (BRD) generator with a FastAPI backend and React frontend.

## Features

- Upload source documents in **PDF**, **DOCX**, or **TXT** format
- Automatic document parsing and chunking
- LangGraph workflow with nodes and edges
- Human-in-the-loop (HITL) approval for each generated BRD section
- Compile and download the final BRD as a Word document

## Prerequisites

- Python 3.11+
- Node.js 20+

## Quick Start

```bash
chmod +x scripts/setup.sh scripts/dev.sh
./scripts/setup.sh
./scripts/dev.sh
```

- Frontend: http://127.0.0.1:5173
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

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Workflow

1. Upload a source document.
2. The backend parses and chunks the content via LangGraph nodes.
3. Each BRD section is generated and paused for human approval.
4. Approve or reject sections with optional feedback.
5. After all sections are approved, download the compiled BRD `.docx`.

## Project Structure

```
backend/     FastAPI + LangGraph workflow
frontend/    React + Vite UI
scripts/     setup and development helpers
```

## Environment Variables

| Variable | Default | Description |
| --- | --- | --- |
| `BRD_UPLOAD_DIR` | `data/uploads` | Uploaded source documents |
| `BRD_OUTPUT_DIR` | `data/outputs` | Generated BRD files |
| `BRD_CORS_ORIGINS` | `http://localhost:5173` | Allowed frontend origins |
