from enum import Enum as PyEnum
from app.extensions import db
from .enums import EstadoConsulta
from datetime import datetime

class Consulta(db.Model):
    __tablename__ = 'consultas'  ## Nombre de la tabla en la BD
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(500), nullable=False)
    comentario_clinica = db.Column(db.Boolean, nullable=False, default=False)
    estado_consulta = db.Column(db.Enum(EstadoConsulta), nullable=False, default=EstadoConsulta.PENDIENTE)
    fecha_creacion   = db.Column(db.DateTime, nullable=False, default=datetime.now())
    
    # ref a dueño de la mascota
    dueño_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    dueño = db.relationship('Usuario', foreign_keys=[dueño_id], passive_deletes=True)

    # Foreign key a veterinarios
    vet_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True)
    vet = db.relationship('Usuario', foreign_keys=[vet_id])
    
    # Foreign key a mascotas.id
    mascota_id = db.Column(db.Integer, db.ForeignKey('mascotas.id', ondelete='CASCADE'), nullable=False)
    mascota = db.relationship('Mascota', passive_deletes=True)
    
    # Foreign key a clinicas.id
    clinica_id = db.Column(db.Integer, db.ForeignKey('clinicas.id', ondelete='SET NULL'), nullable=True)
    clinica = db.relationship('Clinica', foreign_keys=[clinica_id])

    
    def __init__(self, titulo, coment_clinica, estado=EstadoConsulta.PENDIENTE):
        self.titulo = titulo
        self.comentario_clinica = coment_clinica
        self.estado_consulta = estado
        self.fecha_creacion    = datetime.now()
        
    def save(self):
        db.session.add(self)
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()
