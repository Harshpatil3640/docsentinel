# Dev log

## 2026-11-17 · Phase 0

- Did: installed uv, Python 3.12 and Ollama; created the project; pushed it to GitHub with an MIT license and topics
- Error I hit: 'uv' not recognized in VS Code; the Ollama winget install failed; the model saved to C: instead of D:
- How I fixed it: restarted VS Code; installed Ollama by hand; moved the models to D: and set OLLAMA_MODELS
- What I learned:
  - Git: a commit is a saved snapshot on my machine; nothing reaches GitHub until I push. Small commits with clear messages make the history easy to read and undo.
  - uv: one tool replaces pip, venv and pyenv. `uv.lock` pins exact versions so anyone can rebuild the same environment with `uv sync`.
  - Ollama: runs LLMs locally with no API cost. Models are big, so `OLLAMA_MODELS` controls where they're stored (I put them on D: to save space on C:).
- Next: Phase 1, the synthetic GST invoice dataset

## 2026-11-17 · Phase 1

- Did: built a GSTIN checksum helper; wrote a generator for 100 synthetic GST invoices with 9 planted problem types; added a dataset card and changelog
- Error I hit: my counts didn't match the expected output
- How I fixed it: found and fixed a mistake in the PROBLEMS list; same seed gives the same data
- What I learned: CGST+SGST for same-state sales and IGST for other states; how a GSTIN checksum catches typos; why a fixed seed makes data reproducible
- Next: Phase 2, extracting invoice fields with an LLM

## 2026-11-20 · Phase 2

- Did: Groq API key in .env (ignored by Git); PDF to text with pdfplumber; LLM extraction into a Pydantic model; Groq and Ollama both work
- Error I hit: a stray file named BaseChatModel got committed
- How I fixed it: pasting code into CMD made `>` create a file; removed it with git rm
- What I learned: structured output forces a fixed JSON shape; the LLM must copy values, not fix them; secrets go in .env, never in code
- Next: Phase 3, validation rules, tests and CI

## 2026-11-20 · Phase 3

- Did: 10 validation rules, SQLite duplicate check, 27 tests, validate command, CI on GitHub Actions
- Error I hit: the dataset test failed on INV-0034 (two problems instead of one); test_rules.py was missing
- How I fixed it: the generator copied a broken invoice as a duplicate, so duplicates now copy only clean ones; created the missing test file
- What I learned: tests catch bugs in data, not only code; rules give exact, repeatable decisions; CI runs every test on every push
- Next: Phase 4, measure extraction accuracy on all 100 invoices
