from enum import Enum as PyEnum
from app.extensions import db
from .enums import TipoMascota


class Habitacion_hotel(db.Model):
    __tablename__ = 'habitaciones_hotel'  ## Nombre de la tabla en la BD
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tamaño = db.Column(db.Integer, nullable=False, default=0)
    tipo = db.Column(db.Enum(TipoMascota), nullable=False) # NO SE SI AL SER NULLABLE FALSE HAY QUE PONER DEFAULT
    
    # Foreign key a clinicas.id
    clinica_id = db.Column(db.Integer, db.ForeignKey('clinicas.id', ondelete='CASCADE'), nullable=False)
    # Relación hacia Clinica
    clinica = db.relationship('Clinica',passive_deletes=True)

    
    def __init__(self, tamaño, tipo):
        self.tamaño = tamaño
        self.tipo = tipo
        
    
    def save(self):
        db.session.add(self)
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()
