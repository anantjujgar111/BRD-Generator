from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from .nodes import (
    await_approval_node,
    chunk_document_node,
    compile_brd_node,
    generate_section_node,
    parse_document_node,
    process_approval_node,
)
from .state import WorkflowState


def _route_after_approval(state: WorkflowState) -> str:
    status = state.get("status")
    if status == "regenerate":
        return "generate_section"
    if status == "sections_complete":
        return "compile_brd"
    return "generate_section"


def build_workflow_graph():
    graph = StateGraph(WorkflowState)

    graph.add_node("parse_document", parse_document_node)
    graph.add_node("chunk_document", chunk_document_node)
    graph.add_node("generate_section", generate_section_node)
    graph.add_node("await_approval", await_approval_node)
    graph.add_node("process_approval", process_approval_node)
    graph.add_node("compile_brd", compile_brd_node)

    graph.add_edge(START, "parse_document")
    graph.add_edge("parse_document", "chunk_document")
    graph.add_edge("chunk_document", "generate_section")
    graph.add_edge("generate_section", "await_approval")
    graph.add_edge("await_approval", "process_approval")
    graph.add_conditional_edges("process_approval", _route_after_approval)
    graph.add_edge("compile_brd", END)

    memory = MemorySaver()
    return graph.compile(checkpointer=memory, interrupt_before=["await_approval"])
