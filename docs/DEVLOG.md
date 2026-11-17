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
