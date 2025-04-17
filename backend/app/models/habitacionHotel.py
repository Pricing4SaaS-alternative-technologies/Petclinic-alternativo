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


class HabitacionHotel(db.Model):
    __tablename__ = 'habitaciones_hotel'  ## Nombre de la tabla en la BD
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    size = db.Column(db.Integer, nullable=False, default=0)
    type = db.Column(db.Enum(PetType), nullable=False) # NO SE SI AL SER NULLABLE FALSE HAY QUE PONER DEFAULT
    
    # 1) foreign key a clinicas.id
    clinica_id = db.Column(db.Integer, db.ForeignKey('clinicas.id'), nullable=False)
    # 2) relación hacia Clinica
    clinica = db.relationship('Clinica', back_populates='habitaciones')
    
        # relación nueva: una habitación → muchas reservas
    reservas = db.relationship(
        'Reserva',
        back_populates='habitacion',
        cascade='all, delete-orphan',
        lazy='select'
    )

    
    def __init__(self, size, type):
        self.size = size
        self.type = type
        
    
    def save(self):
        db.session.add(self)
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()
