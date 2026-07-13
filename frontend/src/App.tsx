import { useEffect, useMemo, useState } from "react";
import {
  approveSection,
  checkHealth,
  downloadUrl,
  getWorkflow,
  uploadDocument,
  type WorkflowResponse,
} from "./api";

const POLL_INTERVAL_MS = 1500;

export default function App() {
  const [health, setHealth] = useState<string>("checking");
  const [workflowId, setWorkflowId] = useState<string | null>(null);
  const [workflow, setWorkflow] = useState<WorkflowResponse | null>(null);
  const [feedback, setFeedback] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    checkHealth()
      .then((result) => setHealth(result.status))
      .catch(() => setHealth("offline"));
  }, []);

  useEffect(() => {
    if (!workflowId) {
      return;
    }

    let active = true;
    const poll = async () => {
      try {
        const next = await getWorkflow(workflowId);
        if (active) {
          setWorkflow(next);
          setError(null);
        }
      } catch (pollError) {
        if (active) {
          setError(pollError instanceof Error ? pollError.message : "Polling failed");
        }
      }
    };

    poll();
    const timer = window.setInterval(poll, POLL_INTERVAL_MS);
    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, [workflowId]);

  const progress = useMemo(() => {
    if (!workflow) {
      return 0;
    }
    const approved = workflow.sections.filter((section) => section.status === "approved").length;
    return Math.round((approved / workflow.total_sections) * 100);
  }, [workflow]);

  const handleUpload = async (file: File | undefined) => {
    if (!file) {
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const response = await uploadDocument(file);
      setWorkflowId(response.workflow_id);
      const initial = await getWorkflow(response.workflow_id);
      setWorkflow(initial);
    } catch (uploadError) {
      setError(uploadError instanceof Error ? uploadError.message : "Upload failed");
    } finally {
      setBusy(false);
    }
  };

  const handleApproval = async (approved: boolean) => {
    if (!workflowId) {
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const next = await approveSection(workflowId, approved, feedback || undefined);
      setWorkflow(next);
      setFeedback("");
    } catch (approvalError) {
      setError(approvalError instanceof Error ? approvalError.message : "Approval failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="app">
      <header className="hero">
        <h1>BRD Generator</h1>
        <p>
          LangGraph workflow with document parsing, chunking, human-in-the-loop section approval, and
          final BRD export.
        </p>
      </header>

      <section className="card">
        <h2>Environment</h2>
        <p>
          Backend health:{" "}
          <span className={`status-pill ${health === "ok" ? "ok" : "warn"}`}>{health}</span>
        </p>
      </section>

      <section className="card">
        <h2>1. Upload Source Document</h2>
        <p className="muted">Supported formats: PDF, DOCX, TXT</p>
        <div className="upload-row">
          <label className={`file-label ${busy ? "disabled" : ""}`}>
            Choose file
            <input
              type="file"
              accept=".pdf,.docx,.txt"
              disabled={busy}
              onChange={(event) => handleUpload(event.target.files?.[0])}
            />
          </label>
          {workflow && <span className="muted">Current file: {workflow.filename}</span>}
        </div>
        {error && <p className="error">{error}</p>}
      </section>

      {workflow && (
        <>
          <section className="card">
            <h2>2. Workflow Progress</h2>
            <p>
              Status: <span className="status-pill">{workflow.status}</span>
            </p>
            <p className="muted">
              Parsed chunks: {workflow.chunk_count} | Section {Math.min(workflow.current_section_index + 1, workflow.total_sections)} of{" "}
              {workflow.total_sections}
            </p>
            <div className="progress">
              <span style={{ width: `${progress}%` }} />
            </div>
            {workflow.parsed_preview && (
              <>
                <h3>Parsed Preview</h3>
                <div className="section-content">{workflow.parsed_preview}</div>
              </>
            )}
          </section>

          {workflow.pending_section && workflow.status === "awaiting_approval" && (
            <section className="card">
              <h2>3. Human-in-the-Loop Review</h2>
              <p>
                Review section: <strong>{workflow.pending_section.title}</strong> (v
                {workflow.pending_section.version})
              </p>
              <div className="section-content">{workflow.pending_section.content}</div>
              <p className="muted">Optional feedback for revisions</p>
              <textarea
                value={feedback}
                onChange={(event) => setFeedback(event.target.value)}
                placeholder="Add revision notes if rejecting..."
              />
              <div className="actions">
                <button disabled={busy} onClick={() => handleApproval(true)}>
                  Approve Section
                </button>
                <button className="danger" disabled={busy} onClick={() => handleApproval(false)}>
                  Reject & Regenerate
                </button>
              </div>
            </section>
          )}

          <section className="card">
            <h2>4. Generated Sections</h2>
            <div className="section-list">
              {workflow.sections.map((section) => (
                <div className="section-item" key={`${section.id}-${section.version}`}>
                  <span>{section.title}</span>
                  <span className={`status-pill ${section.status === "approved" ? "done" : "warn"}`}>
                    {section.status}
                  </span>
                </div>
              ))}
            </div>
          </section>

          {workflow.status === "completed" && (
            <section className="card">
              <h2>5. Download BRD</h2>
              <p>All sections are approved. The final BRD document is ready.</p>
              <a href={downloadUrl(workflow.workflow_id)}>
                <button>Download BRD (.docx)</button>
              </a>
            </section>
          )}
        </>
      )}
    </div>
  );
}
