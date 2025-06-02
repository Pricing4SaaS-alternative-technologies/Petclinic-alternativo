from .enums import TipoUsuarioEnum
from .usuario import Usuario

from app.extensions import db

class Prop_mascota(Usuario):
    __tablename__ = 'props_mascotas'

    id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), primary_key=True)
    direccion = db.Column(db.String(100),nullable=False)
    telefono = db.Column(db.String(20),nullable=False)
    
    clinica_id = db.Column(db.Integer, db.ForeignKey('clinicas.id'), nullable=False)
    clinica = db.relationship('Clinica', foreign_keys=[clinica_id])

    __mapper_args__ = {
        'polymorphic_identity': TipoUsuarioEnum.PROP_MASCOTA,
    }
    
    
    def __init__(self, first_name, last_name, username, email, password, direccion, telefono, clinica_id):
        super().__init__(first_name, last_name, username, email, password, TipoUsuarioEnum.PROP_MASCOTA)
        self.direccion = direccion
        self.telefono = telefono
        self.clinica_id = clinica_id
        
    def save(self):
        db.session.add(self)
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()
