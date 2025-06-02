from enum import Enum as PyEnum
from app.extensions import db

from sqlalchemy import Enum as SqlEnum
from .enums import Stage

class PetType(PyEnum):
    CAT = "CAT"
    DOG = "DOG"
    LIZARD = "LIZARD"
    SNAKE = "SNAKE"
    BIRD = "BIRD"
    HAMSTER = "HAMSTER"
    TURTLE = "TURTLE"


class Mascota(db.Model):
    __tablename__ = 'mascotas'  ## Nombre de la tabla en la BD
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    birthDate = db.Column(db.Date, nullable=False)
    type = db.Column(db.Enum(PetType), nullable=False) # NO SE SI AL SER NULLABLE FALSE HAY QUE PONER DEFAULT
    
    dueño_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    dueño = db.relationship('Usuario', foreign_keys=[dueño_id])


    def __init__(self, name, birthDate, adopted, type):
        self.name = name
        self.birthDate = birthDate
        self.adopted = adopted
        self.type = type
        
    
    def save(self):
        db.session.add(self)
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()
