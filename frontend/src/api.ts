export type WorkflowStatus =
  | "pending"
  | "parsing"
  | "generating"
  | "awaiting_approval"
  | "completed"
  | "failed";

export interface WorkflowSection {
  id: string;
  title: string;
  content: string;
  status: string;
  version: number;
}

export interface WorkflowResponse {
  workflow_id: string;
  status: WorkflowStatus;
  filename: string;
  current_section_index: number;
  total_sections: number;
  sections: WorkflowSection[];
  pending_section: WorkflowSection | null;
  output_path: string | null;
  error: string | null;
  parsed_preview: string | null;
  chunk_count: number;
}

export interface UploadResponse {
  workflow_id: string;
  filename: string;
  message: string;
}

const API_BASE = "";

export async function checkHealth(): Promise<{ status: string; service: string }> {
  const response = await fetch(`${API_BASE}/health`);
  if (!response.ok) {
    throw new Error("Backend health check failed");
  }
  return response.json();
}

export async function uploadDocument(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch(`${API_BASE}/api/upload`, {
    method: "POST",
    body: formData,
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || "Upload failed");
  }
  return response.json();
}

export async function getWorkflow(workflowId: string): Promise<WorkflowResponse> {
  const response = await fetch(`${API_BASE}/api/workflow/${workflowId}`);
  if (!response.ok) {
    throw new Error("Failed to load workflow");
  }
  return response.json();
}

export async function approveSection(
  workflowId: string,
  approved: boolean,
  feedback?: string,
): Promise<WorkflowResponse> {
  const response = await fetch(`${API_BASE}/api/workflow/${workflowId}/approve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ approved, feedback }),
  });
  if (!response.ok) {
    throw new Error("Approval request failed");
  }
  return response.json();
}

export function downloadUrl(workflowId: string): string {
  return `${API_BASE}/api/workflow/${workflowId}/download`;
}
