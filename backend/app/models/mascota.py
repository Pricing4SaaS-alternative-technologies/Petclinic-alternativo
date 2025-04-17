from enum import Enum as PyEnum
from app.extensions import db

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
    adopted = db.Column(db.Boolean, nullable=False, default=False)
    type = db.Column(db.Enum(PetType), nullable=False) # NO SE SI AL SER NULLABLE FALSE HAY QUE PONER DEFAULT

    # Relación con Reserva
    reservas = db.relationship('Reserva', back_populates='mascota', cascade='all, delete-orphan', lazy='select')

    # Relación con Visita
    visitas = db.relationship('Visita', back_populates='mascota', cascade='all, delete-orphan', lazy='select')

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
