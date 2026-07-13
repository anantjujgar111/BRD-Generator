# BRD Generator

LangGraph-based Business Requirements Document (BRD) generator with a FastAPI backend, **Anthropic Claude** section generation, and a Streamlit frontend.

## Features

- Upload source documents in **PDF**, **DOCX**, or **TXT** format
- Automatic document parsing and chunking
- **Claude LLM** drafting for each BRD section
- LangGraph workflow with nodes and edges
- Human-in-the-loop (HITL) approval for each generated BRD section
- Compile and download the final BRD as a Word document

## Prerequisites

- Python 3.11+
- Anthropic API key ([console.anthropic.com](https://console.anthropic.com/))

## Quick Start

```bash
cp .env.example backend/.env
# Edit backend/.env and set ANTHROPIC_API_KEY

chmod +x scripts/setup.sh scripts/dev.sh
./scripts/setup.sh
./scripts/dev.sh
```

- Streamlit UI: http://127.0.0.1:8503
- Backend API: http://127.0.0.1:8005
- Health check: http://127.0.0.1:8005/health

## VS Code setup

1. Open the repo folder in VS Code
2. Copy `.env.example` to `backend/.env`
3. Set your Claude key:
   ```env
   ANTHROPIC_API_KEY=sk-ant-...
   ```
4. Terminal 1 (backend):
   ```bash
   cd backend
   source .venv/bin/activate   # Windows: .\.venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8005
   ```
5. Terminal 2 (Streamlit):
   ```bash
   source backend/.venv/bin/activate
   pip install -r frontend/requirements.txt
   cd frontend
   streamlit run app.py --server.address 127.0.0.1 --server.port 8503
   ```
6. Open http://127.0.0.1:8503

## Workflow

1. Upload a source document in the Streamlit UI.
2. The backend parses and chunks the content via LangGraph nodes.
3. Claude drafts each BRD section and the workflow pauses for human approval.
4. Approve or reject sections with optional feedback (Claude revises on reject).
5. After all sections are approved, download the compiled BRD `.docx`.

## Project Structure

```
backend/     FastAPI + LangGraph + Claude integration
frontend/    Streamlit UI (app.py)
scripts/     setup and development helpers
```

## Environment Variables

| Variable | Default | Description |
| --- | --- | --- |
| `ANTHROPIC_API_KEY` | — | **Required** for Claude generation |
| `BRD_CLAUDE_MODEL` | `claude-sonnet-4-20250514` | Claude model name |
| `BRD_CLAUDE_MAX_TOKENS` | `4096` | Max tokens per section |
| `BRD_UPLOAD_DIR` | `data/uploads` | Uploaded source documents |
| `BRD_OUTPUT_DIR` | `data/outputs` | Generated BRD files |
| `BRD_API_BASE` | `http://127.0.0.1:8005` | Backend URL used by Streamlit |

If `ANTHROPIC_API_KEY` is missing, the app falls back to a basic template generator.
