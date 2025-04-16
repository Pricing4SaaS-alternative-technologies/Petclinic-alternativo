from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db


class Usuario(db.Model):
    __tablename__ = 'usuarios'  ## Nombre de la tabla en la BD
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)
    
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
        
    def hash_password(self):
        self.password = generate_password_hash(self.password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
        
    @classmethod
    def find_by_username_or_email(cls, username, email):
        return cls.query.filter((cls.username == username) | (cls.email == email)).first()
    
    def save(self):
        db.session.add(self)
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()
