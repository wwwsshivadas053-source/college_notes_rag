from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request
)

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from forms import (
    RegisterForm,
    LoginForm
)

from models.user import User

from app import db

import os

from werkzeug.utils import secure_filename

from models.note import Note

def register_routes(app):

    @app.route("/")
    def home():
        return render_template("home.html")

    @app.route("/about")
    def about():
        return render_template("about.html")

    @app.route(
        "/register",
        methods=["GET","POST"]
    )
    def register():

        form = RegisterForm()

        if form.validate_on_submit():

            existing = User.query.filter_by(
                email=form.email.data
            ).first()

            if existing:

                flash(
                    "Email already exists",
                    "danger"
                )

                return redirect(
                    url_for("register")
                )

            user = User(
                username=form.username.data,
                email=form.email.data,
                password=generate_password_hash(
                    form.password.data
                )
            )

            db.session.add(user)

            db.session.commit()

            flash(
                "Registration successful",
                "success"
            )

            return redirect(
                url_for("login")
            )

        return render_template(
            "register.html",
            form=form
        )

    @app.route(
        "/login",
        methods=["GET","POST"]
    )
    def login():

        form = LoginForm()

        if form.validate_on_submit():

            user = User.query.filter_by(
                email=form.email.data
            ).first()

            if user and check_password_hash(
                user.password,
                form.password.data
            ):

                login_user(user)

                flash(
                    "Login Successful",
                    "success"
                )

                return redirect(
                    url_for("dashboard")
                )

            flash(
                "Invalid Credentials",
                "danger"
            )

        return render_template(
            "login.html",
            form=form
        )

    @app.route("/logout")
    @login_required
    def logout():

        logout_user()

        flash(
            "Logged Out",
            "info"
        )

        return redirect(
            url_for("home")
        )

    @app.route("/dashboard")
    @login_required
    def dashboard():

        return render_template(
            "dashboard.html",
            total_notes=total_notes
        )

    ALLOWED_EXTENSIONS = {"pdf"}

    def allowed_file(filename):

        return (
                "." in filename and
                filename.rsplit(".", 1)[1].lower()
                in ALLOWED_EXTENSIONS
        )
        total_notes = Note.query.filter_by(
            user_id=current_user.id
        ).count()

    @app.route(
        "/upload-note",
        methods=["POST"]
    )
    @login_required
    def upload_note():

        if "pdf" not in request.files:
            flash("No file selected", "danger")

            return redirect(
                url_for("dashboard")
            )

        file = request.files["pdf"]

        if file.filename == "":
            flash("No file selected", "danger")

            return redirect(
                url_for("dashboard")
            )

        if file and allowed_file(file.filename):
            filename = secure_filename(
                file.filename
            )

            unique_name = (
                    str(current_user.id)
                    + "_"
                    + filename
            )

            path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                unique_name
            )

            file.save(path)

            note = Note(
                filename=unique_name,
                original_name=filename,
                user_id=current_user.id
            )

            db.session.add(note)

            db.session.commit()

            flash(
                "PDF uploaded successfully",
                "success"
            )

        return redirect(
            url_for("dashboard")
        )

    @app.route(
        "/delete-note/<int:id>"
    )
    @login_required
    def delete_note(id):

        note = Note.query.get_or_404(id)

        if note.user_id != current_user.id:
            flash("Unauthorized", "danger")

            return redirect(
                url_for("dashboard")
            )

        file_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            note.filename
        )

        if os.path.exists(file_path):
            os.remove(file_path)

        db.session.delete(note)

        db.session.commit()

        flash(
            "Note deleted",
            "success"
        )

        return redirect(
            url_for("my_notes")
        )

