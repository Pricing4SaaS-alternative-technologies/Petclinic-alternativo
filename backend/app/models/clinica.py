from app.extensions import db
from .enums import Plan

class Clinica(db.Model):
    __tablename__ = 'clinicas'  ## Nombre de la tabla en la BD
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    direccion = db.Column(db.String(100), unique=True, nullable=False)
    telefono = db.Column(db.String(9), unique=True, nullable=False)
    plan = db.Column(db.Enum(Plan), nullable=False, default=Plan.BASIC)
    
    propietario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    propietario = db.relationship('Usuario', foreign_keys=[propietario_id])

    
    def __init__(self, nombre, dir, tlf, plan=Plan.BASIC):
        self.nombre = nombre
        self.direccion = dir
        self.telefono = tlf
        self.plan = plan
        
    
    def save(self):
        db.session.add(self)
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()
