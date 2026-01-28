from datetime import datetime
from app.extensions import db
from .enums import EstadoPeticion


class Peticion_adopcion(db.Model):
    __tablename__ = 'peticiones_adopcion'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    razon_adopcion = db.Column(db.String(255), nullable=False)
    fecha_solicitud = db.Column(db.DateTime, nullable=False, default=datetime.now())
    estado_peticion = db.Column(db.Enum(EstadoPeticion), nullable=False)

    # si se borra la adopción, sus peticiones deberian ser borradas
    adopcion_id = db.Column(db.Integer, db.ForeignKey('adopciones.id', ondelete='CASCADE'), nullable=False)
    adopcion = db.relationship('Adopcion', passive_deletes=True)
    
    #si se borra el solicitante deberia borrarse las peticiones que tuviera
    solicitante_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    solicitante = db.relationship('Usuario', foreign_keys=[solicitante_id], passive_deletes=True)

    def __init__(self, razon_adopcion, solicitante_id, adopcion_id, estado_petición=EstadoPeticion.PENDIENTE):
        self.razon_adopcion = razon_adopcion
        self.fecha_solicitud = datetime.now()
        self.solicitante_id = solicitante_id
        self.adopcion_id = adopcion_id
        self.estado_petición = estado_petición

    def __repr__(self):
        return f"<Peticion_adopcion(fecha_solicitud='{self.fecha_solicitud}', estado='{self.estado_petición}')>"
    
    def save(self):
        db.session.add(self)
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()
