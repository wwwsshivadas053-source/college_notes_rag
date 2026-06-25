from pathlib import Path

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import login_required

from .decorators import admin_required
from .extensions import db
from .models import ChatLog, Feedback, Note, User
from .rag_service import RAGService

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    users = User.query.order_by(User.created_at.desc()).all()
    notes = Note.query.order_by(Note.created_at.desc()).all()
    feedback = Feedback.query.order_by(Feedback.created_at.desc()).all()
    logs = ChatLog.query.order_by(ChatLog.created_at.desc()).limit(50).all()
    return render_template("admin.html", users=users, notes=notes, feedback=feedback, logs=logs)


@admin_bp.route("/users/<int:user_id>/role", methods=["POST"])
@login_required
@admin_required
def update_user_role(user_id):
    user = db.session.get(User, user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("admin.dashboard"))
    role = request.form.get("role")
    if role not in {"user", "admin"}:
        flash("Invalid role.", "danger")
        return redirect(url_for("admin.dashboard"))
    user.role = role
    db.session.commit()
    flash("User role updated.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("admin.dashboard"))
    if user.is_admin and User.query.filter_by(role="admin").count() <= 1:
        flash("Cannot delete the only admin.", "danger")
        return redirect(url_for("admin.dashboard"))

    upload_dir = Path(current_app.instance_path, current_app.config["UPLOAD_FOLDER"])
    uploaded_files = [upload_dir / note.stored_filename for note in user.notes]
    db.session.delete(user)
    db.session.commit()
    for file_path in uploaded_files:
        if file_path.exists():
            file_path.unlink()
    RAGService(user_id).rebuild_index()
    flash("User deleted.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/notes/<int:note_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_note(note_id):
    note = db.session.get(Note, note_id)
    if not note:
        flash("Note not found.", "danger")
        return redirect(url_for("admin.dashboard"))
    user_id = note.user_id
    file_path = Path(current_app.instance_path, current_app.config["UPLOAD_FOLDER"], note.stored_filename)
    db.session.delete(note)
    db.session.commit()
    if file_path.exists():
        file_path.unlink()
    RAGService(user_id).rebuild_index()
    flash("Note deleted and index rebuilt.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/feedback/<int:feedback_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_feedback(feedback_id):
    feedback = db.session.get(Feedback, feedback_id)
    if feedback:
        db.session.delete(feedback)
        db.session.commit()
        flash("Feedback deleted.", "success")
    return redirect(url_for("admin.dashboard"))
