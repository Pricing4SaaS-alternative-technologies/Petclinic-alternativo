from enum import Enum as PyEnum
from app.extensions import db
from .enums import EstadoConsulta
from datetime import datetime

class Consulta(db.Model):
    __tablename__ = 'consultas'  ## Nombre de la tabla en la BD
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(500), nullable=False)
    estado_consulta = db.Column(db.Enum(EstadoConsulta), nullable=False, default=EstadoConsulta.PENDIENTE)
    fecha_creacion   = db.Column(db.DateTime, nullable=False, default=datetime.now())
    
    # si se elimina el dueño de la mascota se eliminan las consultas(revisar logica de borrado, el cascade de mascotas ya borra lo otro)
    dueño_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    dueño = db.relationship('Usuario', foreign_keys=[dueño_id], passive_deletes=True)

    # Al ser opcional, en caso de eliminarse el vet, la consulta mantendra el vet_id a null
    vet_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True)
    vet = db.relationship('Usuario', foreign_keys=[vet_id])
    
    # Si se elimina la mascota, se eliminan las consultas
    mascota_id = db.Column(db.Integer, db.ForeignKey('mascotas.id', ondelete='CASCADE'), nullable=False)
    mascota = db.relationship('Mascota', passive_deletes=True)
    
    # Relación con las respuestas de consulta
    respuestas = db.relationship('Respuesta_consulta', back_populates='consulta', cascade='all, delete-orphan', lazy='select')

    def __init__(self, titulo, descripcion, dueño_id, mascota_id, vet_id=None, estado=EstadoConsulta.PENDIENTE):
        self.titulo = titulo
        self.descripcion = descripcion
        self.dueño_id = dueño_id
        self.mascota_id = mascota_id
        self.vet_id = vet_id
        self.estado_consulta = estado
        self.fecha_creacion = datetime.now()
        
    def save(self):
        db.session.add(self)
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()
