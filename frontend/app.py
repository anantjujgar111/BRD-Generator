import time

import streamlit as st

from api_client import API_BASE, ApiError, approve_section, check_health, download_brd, get_workflow, upload_document

st.set_page_config(page_title="BRD Generator", page_icon="📄", layout="wide")

st.title("BRD Generator")
st.caption(
    "LangGraph workflow with document parsing, chunking, human-in-the-loop section approval, "
    "and final BRD export."
)

if "workflow_id" not in st.session_state:
    st.session_state.workflow_id = None
if "workflow" not in st.session_state:
    st.session_state.workflow = None
if "feedback" not in st.session_state:
    st.session_state.feedback = ""


def refresh_workflow() -> None:
    if not st.session_state.workflow_id:
        return
    try:
        st.session_state.workflow = get_workflow(st.session_state.workflow_id)
    except ApiError as exc:
        st.error(str(exc))


with st.sidebar:
    st.subheader("Environment")
    health = check_health()
    if health and health.get("status") == "ok":
        st.success(f"Backend: {health.get('service', 'online')}")
        if health.get("llm_enabled"):
            st.success(f"Claude: {health.get('llm_model', 'enabled')}")
        else:
            st.warning("Claude API key not set — using fallback generator")
            st.caption(f"Backend URL: {API_BASE}")
            st.caption("Add ANTHROPIC_API_KEY to backend/.env and restart backend.")
    else:
        st.error("Backend offline")
        st.stop()

    if st.session_state.workflow_id:
        st.divider()
        st.text(f"Workflow: {st.session_state.workflow_id[:8]}...")
        if st.button("Refresh status", use_container_width=True):
            refresh_workflow()
            st.rerun()

col_upload, col_status = st.columns([1, 1])

with col_upload:
    st.subheader("1. Upload source document")
    st.markdown("Supported formats: **PDF**, **DOCX**, **TXT**")
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "txt"], label_visibility="collapsed")

    if uploaded_file and st.button("Start BRD generation", type="primary", use_container_width=True):
        with st.spinner("Uploading and starting workflow..."):
            try:
                result = upload_document(
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    uploaded_file.type,
                )
                st.session_state.workflow_id = result["workflow_id"]
                st.session_state.workflow = get_workflow(result["workflow_id"])
                st.session_state.feedback = ""
                st.success(result.get("message", "Workflow started"))
                time.sleep(0.5)
                st.rerun()
            except ApiError as exc:
                st.error(str(exc))

workflow = st.session_state.workflow

if workflow:
    approved_count = sum(1 for section in workflow.get("sections", []) if section.get("status") == "approved")
    total_sections = workflow.get("total_sections", 12)
    progress_value = approved_count / total_sections if total_sections else 0

    with col_status:
        st.subheader("2. Workflow progress")
        st.metric("Status", workflow.get("status", "unknown").replace("_", " ").title())
        st.progress(progress_value, text=f"{approved_count} of {total_sections} sections approved")
        st.caption(
            f"File: {workflow.get('filename', '')} | "
            f"Chunks: {workflow.get('chunk_count', 0)} | "
            f"Section {min(workflow.get('current_section_index', 0) + 1, total_sections)} of {total_sections}"
        )

    if workflow.get("parsed_preview"):
        with st.expander("Parsed preview", expanded=False):
            st.text(workflow["parsed_preview"])

    pending = workflow.get("pending_section")
    if pending and workflow.get("status") == "awaiting_approval":
        st.subheader("3. Human-in-the-loop review")
        st.markdown(f"**Section:** {pending['title']} (v{pending['version']})")
        st.markdown(pending["content"])

        st.session_state.feedback = st.text_area(
            "Optional feedback for revisions",
            value=st.session_state.feedback,
            placeholder="Add revision notes if rejecting...",
        )

        approve_col, reject_col = st.columns(2)
        with approve_col:
            if st.button("Approve section", type="primary", use_container_width=True):
                with st.spinner("Approving section..."):
                    try:
                        st.session_state.workflow = approve_section(
                            st.session_state.workflow_id,
                            approved=True,
                        )
                        st.session_state.feedback = ""
                        st.rerun()
                    except ApiError as exc:
                        st.error(str(exc))

        with reject_col:
            if st.button("Reject and regenerate", use_container_width=True):
                with st.spinner("Requesting regeneration..."):
                    try:
                        st.session_state.workflow = approve_section(
                            st.session_state.workflow_id,
                            approved=False,
                            feedback=st.session_state.feedback or None,
                        )
                        st.session_state.feedback = ""
                        st.rerun()
                    except ApiError as exc:
                        st.error(str(exc))

    st.subheader("4. Generated sections")
    if workflow.get("sections"):
        for section in workflow["sections"]:
            status = section.get("status", "pending")
            icon = "✅" if status == "approved" else "⏳"
            st.markdown(f"{icon} **{section['title']}** — {status} (v{section.get('version', 1)})")
    else:
        st.info("No sections generated yet.")

    if workflow.get("status") == "completed":
        st.subheader("5. Download BRD")
        st.success("All sections are approved. The final BRD document is ready.")
        try:
            brd_bytes = download_brd(st.session_state.workflow_id)
            st.download_button(
                label="Download BRD (.docx)",
                data=brd_bytes,
                file_name=f"BRD-{st.session_state.workflow_id}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary",
                use_container_width=True,
            )
        except ApiError as exc:
            st.error(str(exc))

    if workflow.get("status") == "awaiting_approval":
        time.sleep(2)
        refresh_workflow()
        st.rerun()
