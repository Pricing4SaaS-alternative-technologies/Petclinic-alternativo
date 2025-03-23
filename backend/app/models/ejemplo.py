# backend/app/models.py
from app.extensions import db

class Ejemplo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<Message {self.text}>"
