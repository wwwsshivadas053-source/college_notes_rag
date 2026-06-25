# College Notes RAG Chatbot

A Flask web app where students upload PDF notes and ask questions using Retrieval-Augmented Generation. The app supports user login, admin CRUD, PDF text extraction, local vector retrieval, optional FAISS indexing, Gemini answer generation, and feedback capture.

## Features

- Upload lecture notes, textbooks, and study PDFs.
- Extract PDF text with PyMuPDF.
- Chunk notes and build a per-user retrieval index.
- Use Gemini embeddings plus FAISS when available.
- Fall back to local TF-IDF retrieval when Gemini embeddings or FAISS are unavailable.
- Generate answers with Gemini when `GEMINI_API_KEY` is configured.
- Fall back to the strongest retrieved excerpt when Gemini generation is not configured.
- Register/login with Flask-Login and role-based admin access.
- Admin dashboard for users, notes, feedback, and recent chat logs.

## Cross-Platform Setup

These commands work on Windows PowerShell, macOS, and Linux shells with small syntax differences for activating the virtual environment.

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install the core dependencies:

```bash
pip install -r requirements.txt
```

Optional FAISS support:

```bash
pip install -r requirements-faiss.txt
```

Copy `.env.example` to `.env` for local development, then fill in your own values if you want Gemini embeddings and generated answers. `.env` is ignored by Git, so keep real secrets there only for local runs.

Windows PowerShell local run:

```powershell
$env:GEMINI_API_KEY="your_google_ai_studio_key"
$env:GEMINI_MODEL="gemini-2.0-flash"
$env:GEMINI_EMBEDDING_MODEL="gemini-embedding-001"
python run.py
```

macOS/Linux local run:

```bash
export GEMINI_API_KEY="your_google_ai_studio_key"
export GEMINI_MODEL="gemini-2.0-flash"
export GEMINI_EMBEDDING_MODEL="gemini-embedding-001"
python run.py
```

Without `GEMINI_API_KEY`, the app still runs using TF-IDF retrieval and excerpt answers. If you see `Gemini answer generation is disabled`, the upload/retrieval flow is working but the AI generation step is not configured.

## Secret Safety

- Never commit API keys to GitHub or any public repository.
- Keep real keys only in OS environment variables, Render environment variables, or a production secret manager.
- If a key is exposed publicly, revoke/delete it immediately and create a new key.
- After rotating a key, restart the Flask app so the new environment value is loaded.

## Render Deployment

Create a new Web Service on Render from your GitHub repository.

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
gunicorn run:app
```

Add these in Render Dashboard > Environment:

```text
SECRET_KEY=<generate-a-long-random-value>
GEMINI_API_KEY=<your-new-gemini-api-key>
GEMINI_MODEL=gemini-2.0-flash
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
DATABASE_URL=<optional-postgres-url>
```

Do not add these values to code before pushing to GitHub.

For reliable production data on Render, use Render PostgreSQL and set `DATABASE_URL`. Uploaded PDFs and local vector indexes also need a Render persistent disk; otherwise they may be lost when the service restarts or redeploys.

Run the app:

```bash
python run.py
```

Open `http://127.0.0.1:5000`.

## Default Admin

The first startup creates a default admin if no admin exists:

- Email: `admin@example.com`
- Password: `admin123`

Change this account before production use.

## Project Structure

```text
app/
  admin.py          Admin CRUD routes
  auth.py           Register, login, logout
  chat.py           Upload, ask, feedback routes
  main.py           Home, about, public feedback
  models.py         User, Note, NoteChunk, Feedback, ChatLog
  pdf_service.py    PDF extraction and chunking
  rag_service.py    Retrieval, vector indexing, Gemini integration
  templates/        Tailwind/Alpine pages
  static/js/        Chat browser behavior
config.py           Environment-backed configuration
run.py              Local development entry point
PMD.md              Product/Project Management Document
```

## Notes

- Uploaded PDFs, SQLite database files, and vector indexes are stored under Flask's `instance/` directory.
- The app uses `pathlib` for OS-independent file paths.
- SQLite is the default database. Set `DATABASE_URL` to a PostgreSQL SQLAlchemy URL for production.
