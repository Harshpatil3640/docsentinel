# DocSentinel

An AI agent that checks Indian GST invoices. It extracts the fields, validates tax and business rules, flags fraud signals, asks a human when unsure, and resists prompt-injection attacks. Every claim is measured.

**Status:** work in progress. See the [roadmap](docs/ROADMAP.md).

## What it will do

- Extract invoice fields from PDFs with an LLM
- Check GST rules (GSTIN, tax math, totals, duplicates) in plain Python
- Approve, reject or send to a human, using each vendor's history
- Defend against prompt injection hidden inside documents
- Share read-only tools through an MCP server
- Publish evaluation results for accuracy, cost and security

## Tech stack (all free)

Python 3.12 · uv · LangGraph · Groq and Ollama · pdfplumber · SQLite · pytest · Arize Phoenix · MCP · Streamlit · GitHub Actions

## Results

Coming in v0.4.

## License

MIT
