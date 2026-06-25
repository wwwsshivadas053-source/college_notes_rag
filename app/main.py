from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user

from .extensions import db
from .models import Feedback

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    return render_template("home.html")


@main_bp.route("/about")
def about():
    return render_template("about.html")


@main_bp.route("/feedback", methods=["POST"])
def feedback():
    rating = request.form.get("rating", type=int)
    message = request.form.get("message", "").strip()
    if not rating or rating < 1 or rating > 5:
        flash("Please provide a rating between 1 and 5.", "danger")
        return redirect(url_for("main.home"))

    item = Feedback(
        user_id=current_user.id if current_user.is_authenticated else None,
        rating=rating,
        message=message,
    )
    db.session.add(item)
    db.session.commit()
    flash("Feedback submitted.", "success")
    return redirect(url_for("main.home"))
