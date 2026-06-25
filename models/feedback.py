from app import db

class Feedback(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    rating = db.Column(
        db.Integer
    )

    message = db.Column(
        db.Text
    )

    user_id = db.Column(
        db.Integer
    )