#!/usr/bin/env bash
set -euo pipefail

API="http://127.0.0.1:8005"
DOC="${1:-/home/ubuntu/.cursor/projects/workspace/uploads/BRD-DRAFT-d4def99f_4c98.docx}"

echo "==> Health check"
curl -s "$API/health" | python3 -m json.tool

echo "==> Uploading document: $DOC"
UPLOAD_JSON=$(curl -s -X POST "$API/api/upload" -F "file=@${DOC}")
echo "$UPLOAD_JSON" | python3 -m json.tool
WORKFLOW_ID=$(echo "$UPLOAD_JSON" | python3 -c 'import sys, json; print(json.load(sys.stdin)["workflow_id"])')

approve_current_section() {
  local workflow_id="$1"
  curl -s -X POST "$API/api/workflow/${workflow_id}/approve" \
    -H 'Content-Type: application/json' \
    -d '{"approved": true}' \
    | python3 -c 'import sys, json; data=json.load(sys.stdin); pending=(data.get("pending_section") or {}); print(data["status"], pending.get("title", "done"))'
}

echo "==> Approving all sections for workflow $WORKFLOW_ID"
for i in $(seq 1 12); do
  echo -n "Section $i: "
  approve_current_section "$WORKFLOW_ID"
done

echo "==> Final workflow state"
FINAL_JSON=$(curl -s "$API/api/workflow/$WORKFLOW_ID")
echo "$FINAL_JSON" | python3 -m json.tool | head -40

OUTPUT_PATH=$(echo "$FINAL_JSON" | python3 -c 'import sys, json; print(json.load(sys.stdin).get("output_path") or "")')
if [ -n "$OUTPUT_PATH" ] && [ -f "$OUTPUT_PATH" ]; then
  echo "==> Generated BRD: $OUTPUT_PATH ($(wc -c < "$OUTPUT_PATH") bytes)"
else
  echo "BRD output not found" >&2
  exit 1
fi

echo "==> Demo completed successfully"
