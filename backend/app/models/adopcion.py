from app.extensions import db
from sqlalchemy import Enum as SqlEnum
from .enums import Stage

class Adopcion(db.Model):
    __tablename__ = 'adopciones'  # Nombre de la tabla en la base de datos

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String(255), nullable=False)
    stage = db.Column(SqlEnum(Stage), nullable=False)
    
    #ForeignKey apuntando a mascotas.id
    mascota_id = db.Column( db.Integer, db.ForeignKey('mascotas.id'), nullable=False)
    mascota = db.relationship('Mascota')
    
    dueño_nuevo_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    dueño_nuevo = db.relationship('Usuario', foreign_keys=[dueño_nuevo_id])
    
    dueño_anterior_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    dueño_anterior = db.relationship('Usuario', foreign_keys=[dueño_anterior_id])
    

    def __init__(self, description, stage):
        self.description = description
        self.stage = stage

    def __repr__(self):
        return f"<Adopcion(description='{self.description}', stage='{self.stage}')>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()