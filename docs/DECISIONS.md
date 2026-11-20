# Decisions

Short records of why we chose one option over another.

## D1: uv instead of pip and venv
One tool installs Python, manages the virtual environment and locks exact versions in `uv.lock`, so anyone can rebuild the same setup with `uv sync`.

## D2: Synthetic invoices instead of real ones
Real invoices with correct answers are hard to get and often private. Synthetic ones give exact labels and let us plant problems on purpose. Trade-off: real invoices are messier, so our scores will be optimistic.

## D3: Groq as the main model, Ollama as the local option
Groq is free, fast and runs large models. Ollama runs a small model on the laptop with no internet and no data leaving the machine. One setting, `LLM_PROVIDER`, switches between them.

## D4: Structured output with a Pydantic schema
The model must return exactly the `Invoice` fields with the right types. Bad output fails loudly as a validation error instead of silently producing wrong data.

## D5: The LLM copies values; it never calculates or fixes them
If an invoice has a wrong total, the model must copy the wrong total so the Python rules (Phase 3) can catch it. An LLM that fixes errors would hide fraud.