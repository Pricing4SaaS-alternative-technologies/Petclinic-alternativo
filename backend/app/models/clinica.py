from enum import Enum as PyEnum
from app.extensions import db

class Plan(PyEnum):
    BASIC = "BASIC"
    GOLD = "GOLD"
    PREMIUM = "PREMIUM"


class Clinica(db.Model):
    __tablename__ = 'clinicas'  ## Nombre de la tabla en la BD
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(100), unique=True, nullable=False)
    telephone = db.Column(db.String(9), unique=True, nullable=False)
    plan = db.Column(db.Enum(Plan), nullable=False, default=Plan.BASIC)
    
        # relación inversa: una clínica → muchas habitaciones
    habitaciones = db.relationship(
        'HabitacionHotel',
        back_populates='clinica',
        cascade='all, delete-orphan',
        lazy='select'
    )

    
    
    def __init__(self, name, address, telephone, plan=Plan.BASIC):
        self.name = name
        self.address = address
        self.telephone = telephone
        self.plan = plan
        
    
    def save(self):
        db.session.add(self)
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()
