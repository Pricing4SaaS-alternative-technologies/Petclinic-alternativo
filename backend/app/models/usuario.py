
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Enum as SqlEnum

from .enums import TipoUsuarioEnum

from app.extensions import db


class Usuario(db.Model):
    __tablename__ = 'usuarios'  ## Nombre de la tabla en la BD
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    usuario = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    contraseña = db.Column(db.String(500), nullable=False)
    tipo_usuario = db.Column(SqlEnum(TipoUsuarioEnum), nullable=False)
    
    __mapper_args__ = {
        'polymorphic_identity': TipoUsuarioEnum.USUARIO,
        'polymorphic_on': tipo_usuario
    }
    
    def __init__(self, nombre, apellidos, usuario, email, contraseña, type):
        
        if type == TipoUsuarioEnum.USUARIO:
            raise ValueError("No se puede crear una instancia directa del tipo 'USUARIO'")
        
        self.nombre = nombre
        self.apellidos = apellidos
        self.usuario = usuario
        self.email = email
        self.contraseña = generate_password_hash(contraseña)
        self.tipo_usuario = type
    
    def check_password(self, contraseña):
        return check_password_hash(self.contraseña, contraseña)
        
    @classmethod
    def find_by_usuario_or_email(cls, usuario, email):
        return cls.query.filter((cls.usuario == usuario) | (cls.email == email)).first()
    
    def save(self):
        db.session.add(self)
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()
