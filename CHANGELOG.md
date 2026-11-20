# Changelog

## v0.3 (2026-11-20)

- 10 plain-Python validation rules with reject and review severities
- SQLite store to catch duplicate invoices
- 27 pytest tests, including all 100 dataset invoices
- Command: `uv run docsentinel validate <pdf>`
- GitHub Actions CI: lint, format check and tests on every push and PR
- Fix: duplicate invoices now copy only clean invoices

## v0.2 (2026-11-20)

- Extract invoice fields from PDFs with an LLM into a Pydantic `Invoice` model
- Switch between Groq (cloud) and Ollama (local) with `LLM_PROVIDER` in `.env`
- Command: `uv run docsentinel extract <pdf>`
- Architecture and decisions docs

## v0.1 (2026-11-17)

- GSTIN helper with checksum validation (`src/docsentinel/gstin.py`)
- Synthetic GST invoice generator (`scripts/generate_invoices.py`)
- Dataset: 100 invoices, 9 planted problem types, vendor master, labels