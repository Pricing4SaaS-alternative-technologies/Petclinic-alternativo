from enum import Enum as PyEnum
from app.extensions import db

from .enums import TipoMascota


class Mascota(db.Model):
    __tablename__ = 'mascotas'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    cumpleaños = db.Column(db.Date, nullable=False)
    tipo = db.Column(db.Enum(TipoMascota), nullable=False)
    
    dueño_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    dueño = db.relationship('Usuario', foreign_keys=[dueño_id], passive_deletes=True)
    
    #Revisar relacion con visitas y su borrado
    visitas = db.relationship('Visita', back_populates='mascota', cascade='all, delete-orphan', lazy='select')
    
    def __init__(self, nombre, cumpleaños, tipo, dueño_id):
        self.nombre = nombre
        self.cumpleaños = cumpleaños
        self.tipo = tipo
        self.dueño_id = dueño_id
       
    def save(self):
        db.session.add(self)
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()
