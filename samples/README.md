# Sample files for BRD Generator testing

Use these files to verify the app is working correctly with Claude.

## Input file (upload this)

| File | Description |
|------|-------------|
| `input/HHOBI-Migration-Requirements.docx` | **Recommended** — Word version of raw requirements |
| `input/HHOBI-Migration-Requirements.txt` | Plain text version (same content) |

This is **raw project requirements**, not a finished BRD.  
Do **not** upload `BRD-DRAFT` or an existing BRD as input — that causes repeated headers and poor output.

## Expected output (compare your download to this)

| File | Description |
|------|-------------|
| `expected/Expected-BRD-Output-HHOBI.docx` | Example of a **good** structured BRD |

Your generated BRD should be **similar in structure** (12 sections, IDs like FR-001, tables for risks/stakeholders).  
Wording may differ because Claude generates fresh text.

## How to test

1. Start backend on port **8005** and Streamlit on **8503**
2. Confirm sidebar shows **Claude** green
3. Upload `input/HHOBI-Migration-Requirements.docx`
4. Click **Start BRD generation**
5. Approve all 12 sections
6. Download your BRD and compare with `expected/Expected-BRD-Output-HHOBI.docx`

## Good output signs

- Section-specific content (not repeated TABLE OF CONTENTS)
- Requirements IDs: BG-001, FR-001, NFR-001, etc.
- Risk and stakeholder tables
- References to HHOBI, FDL, IA_PRODUCTS, IA_CUSTOMERS

## Bad output signs (fallback or wrong input)

- Same header repeated in every section
- `Generated: July 10, 2026 TABLE OF CONTENTS` in BG-001 / FR-001
- Generic filler with no project-specific terms
