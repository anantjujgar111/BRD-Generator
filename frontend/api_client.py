import os
from typing import Any

import requests

API_BASE = os.environ.get("BRD_API_BASE", "http://127.0.0.1:8005")
TIMEOUT = 30


class ApiError(Exception):
    pass


def _request(method: str, path: str, **kwargs: Any) -> requests.Response:
    try:
        response = requests.request(method, f"{API_BASE}{path}", timeout=TIMEOUT, **kwargs)
    except requests.RequestException as exc:
        raise ApiError(f"Could not reach backend at {API_BASE}") from exc
    if not response.ok:
        raise ApiError(response.text or f"Request failed with status {response.status_code}")
    return response


def check_health() -> dict[str, Any] | None:
    try:
        return _request("GET", "/health").json()
    except ApiError:
        return None


def upload_document(filename: str, content: bytes, content_type: str | None) -> dict[str, Any]:
    files = {"file": (filename, content, content_type or "application/octet-stream")}
    return _request("POST", "/api/upload", files=files).json()


def get_workflow(workflow_id: str) -> dict[str, Any]:
    return _request("GET", f"/api/workflow/{workflow_id}").json()


def approve_section(workflow_id: str, approved: bool, feedback: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"approved": approved}
    if feedback:
        payload["feedback"] = feedback
    return _request(
        "POST",
        f"/api/workflow/{workflow_id}/approve",
        json=payload,
    ).json()


def download_brd(workflow_id: str) -> bytes:
    return _request("GET", f"/api/workflow/{workflow_id}/download").content
