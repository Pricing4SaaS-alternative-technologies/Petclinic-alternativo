
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Enum as SqlEnum

from .enums import TipoUsuarioEnum

from app.extensions import db


class Usuario(db.Model):
    __tablename__ = 'usuarios'  ## Nombre de la tabla en la BD
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)
    type = db.Column(SqlEnum(TipoUsuarioEnum), nullable=False)
    
    __mapper_args__ = {
        'polymorphic_identity': TipoUsuarioEnum.USUARIO.value,
        'polymorphic_on': type
    }
    
    def __init__(self, first_name, last_name, username, email, password, type):
        if type == TipoUsuarioEnum.USUARIO:
            raise ValueError("No se puede crear una instancia directa del tipo 'USUARIO'")
        
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)
        self.type = type
    
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
