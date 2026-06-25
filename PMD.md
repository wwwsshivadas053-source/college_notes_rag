# PMD: College Notes RAG Chatbot

## Objective

Build a web-based chatbot that lets students upload college notes as PDFs and ask questions against those notes. The system uses retrieval-augmented generation so answers are grounded in uploaded material rather than only general model knowledge.

## Scope

The delivered app includes:

- Student-facing home, about, authentication, chat/analyzer, upload, and feedback pages.
- Admin dashboard for managing users, uploaded notes, feedback, and chat logs.
- PDF extraction using PyMuPDF.
- Chunking and metadata storage using SQLAlchemy models.
- Per-user retrieval index with optional Gemini embeddings and FAISS.
- Local TF-IDF fallback for cross-platform operation.
- Gemini answer generation when `GEMINI_API_KEY` is available.

## Architecture

```text
Browser
  |
  | HTML + TailwindCSS + Alpine.js
  v
Flask App
  |
  | Blueprints: main, auth, chat, admin
  v
Services
  |
  | pdf_service.py -> text extraction and chunking
  | rag_service.py -> retrieval, indexing, answer generation
  v
Persistence
  |
  | SQLite/PostgreSQL -> users, notes, chunks, feedback, chat logs
  | instance/uploads -> uploaded PDFs
  | instance/vector_store -> FAISS/TF-IDF indexes
```

## Data Models

- `User`: account identity, password hash, role (`user` or `admin`).
- `Note`: uploaded PDF metadata, status, chunk count, owner.
- `NoteChunk`: extracted page chunks used for retrieval.
- `ChatLog`: user question, generated answer, source metadata.
- `Feedback`: rating and optional comments for platform or answer quality.

## User Roles

- `User`: upload PDFs, ask questions, submit answer/platform feedback.
- `Admin`: manage users, change roles, delete users, delete notes, delete feedback, inspect recent chat logs.

## Main Flow

1. User uploads a PDF from the chat page.
2. Flask stores the PDF under `instance/uploads`.
3. PyMuPDF extracts selectable text by page.
4. Text is normalized and split into overlapping chunks.
5. Chunks are saved in the database.
6. `RAGService` rebuilds the user's retrieval index.
7. User submits a question.
8. Retrieval selects the most relevant chunks.
9. Gemini receives the retrieved context and question when configured.
10. The answer, sources, and chat log are returned to the browser.
11. User can submit feedback.

## Retrieval Strategy

Primary path:

- Gemini embedding model creates dense vectors.
- FAISS stores and searches vectors using inner-product similarity.

Fallback path:

- TF-IDF vectorizer indexes chunks locally.
- Cosine similarity retrieves relevant chunks.

The fallback is intentionally included because FAISS installation can vary across operating systems and environments. This keeps the app runnable on Windows, macOS, and Linux.

## Security Considerations

- Passwords are hashed with Werkzeug.
- Uploads are restricted to PDF extensions.
- Flask-Login protects chat and admin routes.
- `admin_required` blocks non-admin dashboard access.
- Production deployments must change `SECRET_KEY` and the default admin password.
- For production, use HTTPS, a real mail/password reset flow, stricter file validation, and virus scanning for uploads.

## Deliverables Mapping

- Backend Flask app with modular Blueprints: implemented in `app/auth.py`, `app/chat.py`, `app/admin.py`, and `app/main.py`.
- Frontend Tailwind templates: implemented in `app/templates`.
- Database models: implemented in `app/models.py`.
- Vector store integration: implemented in `app/rag_service.py` with optional FAISS and TF-IDF fallback.
- AI integration: Gemini embeddings and generation in `app/rag_service.py`.
- Authentication: Flask-Login in `app/__init__.py` and `app/auth.py`.
- Admin CRUD: implemented in `app/admin.py`.
- PMD document: this file.

## Future Enhancements

- Add Pinecone as a configurable remote vector backend.
- Add OCR for scanned PDFs.
- Add per-note filtering in chat.
- Add password reset and email verification.
- Add streaming Gemini responses.
- Add automated tests for routes and services.
