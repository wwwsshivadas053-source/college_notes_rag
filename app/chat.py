import uuid
from pathlib import Path

from flask import Blueprint, current_app, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from .extensions import db
from .models import Feedback, Note, NoteChunk
from .pdf_service import chunk_pages, extract_pdf_pages
from .rag_service import RAGService

chat_bp = Blueprint("chat", __name__, url_prefix="/chat")


@chat_bp.route("/")
@login_required
def chat():
    notes = Note.query.filter_by(user_id=current_user.id).order_by(Note.created_at.desc()).all()
    return render_template("chat.html", notes=notes)


@chat_bp.route("/upload", methods=["POST"])
@login_required
def upload():
    file = request.files.get("pdf")
    if not file or file.filename == "":
        flash("Choose a PDF file to upload.", "danger")
        return redirect(url_for("chat.chat"))
    if not _allowed_file(file.filename):
        flash("Only PDF files are supported.", "danger")
        return redirect(url_for("chat.chat"))

    original_name = secure_filename(file.filename)
    stored_name = f"{uuid.uuid4().hex}_{original_name}"
    upload_dir = Path(current_app.instance_path, current_app.config["UPLOAD_FOLDER"])
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / stored_name
    file.save(file_path)

    note = Note(user_id=current_user.id, filename=original_name, stored_filename=stored_name)
    db.session.add(note)
    db.session.commit()

    try:
        pages = extract_pdf_pages(file_path)
        chunks = chunk_pages(pages)
        for index, chunk in enumerate(chunks):
            db.session.add(
                NoteChunk(
                    note_id=note.id,
                    user_id=current_user.id,
                    page_number=chunk["page"],
                    chunk_index=index,
                    content=chunk["content"],
                )
            )
        note.chunk_count = len(chunks)
        note.status = "ready" if chunks else "empty"
        if not chunks:
            note.error_message = "No selectable text was found in this PDF."
        db.session.commit()
        RAGService(current_user.id).rebuild_index()
        flash(f"Uploaded and indexed {original_name}.", "success")
    except Exception as exc:
        note.status = "failed"
        note.error_message = str(exc)
        db.session.commit()
        flash("PDF upload failed while extracting or indexing text.", "danger")

    return redirect(url_for("chat.chat"))


@chat_bp.route("/ask", methods=["POST"])
@login_required
def ask():
    payload = request.get_json(silent=True) or {}
    question = (payload.get("question") or "").strip()
    if not question:
        return jsonify({"error": "Question is required."}), 400

    answer, sources, chat_log_id = RAGService(current_user.id).answer(question)
    return jsonify({"answer": answer, "sources": sources, "chat_log_id": chat_log_id})


@chat_bp.route("/feedback", methods=["POST"])
@login_required
def feedback():
    payload = request.get_json(silent=True) or {}
    rating = int(payload.get("rating") or 0)
    if rating < 1 or rating > 5:
        return jsonify({"error": "Rating must be between 1 and 5."}), 400

    item = Feedback(
        user_id=current_user.id,
        chat_log_id=payload.get("chat_log_id"),
        rating=rating,
        message=(payload.get("message") or "").strip(),
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({"status": "ok"})


def _allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]
