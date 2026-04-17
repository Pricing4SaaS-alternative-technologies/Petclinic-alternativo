from enum import Enum as PyEnum
from app.extensions import db
from .enums import TipoMascota, TamañoHabitacion


class Habitacion_hotel(db.Model):
    __tablename__ = 'habitaciones_hotel'  ## Nombre de la tabla en la BD
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    descripcion = db.Column(db.String(255), nullable=True)
    reservable = db.Column(db.Boolean, nullable=False, default=True)
    url_imagen = db.Column(db.String(255), nullable=True)
    tamaño = db.Column(db.Enum(TamañoHabitacion), nullable=False, default=TamañoHabitacion.MEDIANO)
    tipo = db.Column(db.Enum(TipoMascota), nullable=False) # NO SE SI AL SER NULLABLE FALSE HAY QUE PONER DEFAULT
    
    # Si se borran las clinicas, se borran las habitaciones
    clinica_id = db.Column(db.Integer, db.ForeignKey('clinicas.id', ondelete='CASCADE'), nullable=False)
    clinica = db.relationship('Clinica',passive_deletes=True)

    
    def __init__(self,nombre, reservable, tamaño, tipo, clinica_id):
        self.nombre = nombre
        self.reservable = reservable
        self.tamaño = tamaño
        self.tipo = tipo
        self.clinica_id = clinica_id
        
    
    def save(self):
        db.session.add(self)
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()
