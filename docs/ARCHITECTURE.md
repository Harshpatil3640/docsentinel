# Architecture

## Current (v0.3): extraction and validation

```mermaid
flowchart LR
    A[Invoice PDF] --> B[parsing.py<br/>PDF to text]
    B --> C[extraction.py<br/>prompt + schema]
    C <--> D[llm.py<br/>Groq or Ollama]
    C --> E[Invoice fields]
    E --> F[rules.py<br/>10 Python checks]
    G[(vendors.csv)] --> F
    H[(docsentinel.db<br/>past invoices)] --> F
    F --> I{decide}
    I --> J[approve]
    I --> K[review]
    I --> L[reject]
```

| File | Job |
| --- | --- |
| `src/docsentinel/parsing.py` | Reads the PDF and returns plain text |
| `src/docsentinel/schemas.py` | Defines the `Invoice` and `LineItem` fields (Pydantic) |
| `src/docsentinel/llm.py` | Returns a Groq or Ollama chat model based on `LLM_PROVIDER` |
| `src/docsentinel/extraction.py` | Sends the text to the model and forces the answer into `Invoice` |
| `src/docsentinel/rules.py` | Plain-Python checks: GSTIN, tax type, tax math, totals, dates, duplicates, vendor, bank account |
| `src/docsentinel/db.py` | SQLite file that remembers processed invoices, to catch duplicates |
| `src/docsentinel/gstin.py` | GSTIN checksum helpers |
| `src/docsentinel/__init__.py` | Command line: `extract` and `validate` |

The LLM only reads. Every approve, review or reject decision comes from Python rules.

## Planned

LangGraph agent with human review and vendor memory (Phase 5), prompt-injection defenses (Phase 6), MCP server (Phase 7). See [ROADMAP.md](ROADMAP.md).