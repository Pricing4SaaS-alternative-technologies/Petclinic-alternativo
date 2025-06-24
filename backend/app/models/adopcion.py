from app.extensions import db
from .enums import EstadoAdopcion
from datetime import datetime

class Adopcion(db.Model):
    __tablename__ = 'adopciones'  # Nombre de la tabla en la base de datos

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descripcion = db.Column(db.String(255), nullable=False)
    estado_adopcion = db.Column(db.Enum(EstadoAdopcion), nullable=False)
    
    fecha_creacion   = db.Column(db.DateTime, default=datetime)
    #ForeignKey apuntando a mascotas.id
    mascota_id = db.Column( db.Integer, db.ForeignKey('mascotas.id',ondelete='CASCADE'), nullable=False)
    mascota = db.relationship('Mascota', passive_deletes=True)
    
    dueño_nuevo_id = db.Column(db.Integer, db.ForeignKey('usuarios.id',ondelete='SET NULL'), nullable=True)
    dueño_nuevo = db.relationship('Usuario', foreign_keys=[dueño_nuevo_id])
    
    dueño_anterior_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True)
    dueño_anterior = db.relationship('Usuario', foreign_keys=[dueño_anterior_id])
    

    def __init__(self, desc, estado):
        self.descripcion = desc
        self.estado_adopcion = estado

    def __repr__(self):
        return f"<Adopcion(descripcion='{self.descripcion}', estado='{self.estado_adopcion}')>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        return {
          'id':             self.id,
          'descripcion':    self.descripcion,
          'estado':         self.estado_adopcion.value,
          'fecha_creacion': self.fecha_creacion.isoformat(),
          'mascota':        {'id': self.mascota.id, 'nombre': self.mascota.nombre},
          'dueño_anterior': {'id': self.dueño_anterior.id, 'usuario': self.dueño_anterior.usuario},
          'dueño_nuevo':    {'id': self.dueño_nuevo.id,    'usuario': self.dueño_nuevo.usuario}
        }