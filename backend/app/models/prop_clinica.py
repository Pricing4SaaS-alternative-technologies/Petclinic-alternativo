from .enums import TipoUsuarioEnum

from .usuario import Usuario
from app.extensions import db

class Prop_clinica(Usuario):
    __tablename__ = 'props_clinicas'

    id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), primary_key=True)
    telefono = db.Column(db.String(20),nullable=False)
    
    __mapper_args__ = {
        'polymorphic_identity': TipoUsuarioEnum.PROP_CLINICA,
    }

    def __init__(self, first_name, last_name, username, email, password, telefono):
        super().__init__(first_name, last_name, username, email, password, TipoUsuarioEnum.PROP_CLINICA)
        self.telefono = telefono
        
    def save(self):
        db.session.add(self)
        db.session.commit()
        
    def delete(self):
        usuario = Usuario.query.get(self.id)
        if usuario:
            db.session.delete(usuario)
            db.session.commit()