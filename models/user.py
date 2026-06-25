from app import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(150),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        default="user"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    notes = db.relationship(
        "Note",
        backref="user",
        lazy=True,
        cascade="all, delete"
    )

    feedbacks = db.relationship(
        "Feedback",
        backref="user",
        lazy=True,
        cascade="all, delete"
    )