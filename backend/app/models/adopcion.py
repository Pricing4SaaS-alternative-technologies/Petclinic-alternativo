from app.extensions import db
from datetime import datetime

class Adopcion(db.Model):
    __tablename__ = 'adopciones'  # Nombre de la tabla en la base de datos

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descripcion = db.Column(db.String(255), nullable=False)
    adopcion_cerrada = db.Column(db.Boolean, nullable=False, default=False)
    
    fecha_creacion   = db.Column(db.DateTime, nullable=False, default=datetime.now())
    
    # Si se elimina la mascota, se deben borrar las adopciones
    mascota_id = db.Column( db.Integer, db.ForeignKey('mascotas.id',ondelete='CASCADE'), nullable=False)
    mascota = db.relationship('Mascota', passive_deletes=True)
    
    # Los dueños nuevos pueden ser nulos en caso de no estar finalizadas, en caso de finalizarse, si se elimina el dueño, el cascade de mascotas elimianria la acopcion
    dueño_nuevo_id = db.Column(db.Integer, db.ForeignKey('usuarios.id',ondelete='SET NULL'), nullable=True, default=None)
    dueño_nuevo = db.relationship('Usuario', foreign_keys=[dueño_nuevo_id])
    
    #si se elimina el propietario anterior, la adopción se borrara debido al cascade en mascota
    dueño_anterior_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True)
    dueño_anterior = db.relationship('Usuario', foreign_keys=[dueño_anterior_id])
    

    def __init__(self,
                descripcion,
                mascota_id,
                adopcion_cerrada=False):
       self.descripcion       = descripcion
       self.mascota_id        = mascota_id
       self.adopcion_cerrada  = adopcion_cerrada
       self.fecha_creacion    = datetime.now()

    def __repr__(self):
        return f"<Adopcion(descripcion='{self.descripcion}', estado='{self.estado_adopcion}')>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        antiguo = None
        if self.dueño_anterior:
            antiguo = {
                'id':      self.dueño_anterior.id,
                'usuario': self.dueño_anterior.usuario
            }

        nuevo = None
        if self.dueño_nuevo:
            nuevo = {
                'id':      self.dueño_nuevo.id,
                'usuario': self.dueño_nuevo.usuario
            }

        return {
          'id':             self.id,
          'descripcion':    self.descripcion,
          'estado':         self.estado_adopcion.value,
          'fecha_creacion': self.fecha_creacion.isoformat(),
          'mascota':        {'id': self.mascota.id, 'nombre': self.mascota.nombre},
          'dueño_anterior': antiguo,
          'dueño_nuevo':    nuevo
        }