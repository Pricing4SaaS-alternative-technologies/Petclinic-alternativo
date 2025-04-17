from .enums import TipoUsuarioEnum

from .usuario import Usuario
from app.extensions import db

class Prop_clinica(Usuario):
    __tablename__ = 'props_clinicas'

    id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': TipoUsuarioEnum.PROP_CLINICA,
    }
    
    def __init__(self, first_name, last_name, username, email, password):
        super().__init__(first_name, last_name, username, email, password, TipoUsuarioEnum.PROP_CLINICA)
        # No hay atributos adicionales específicos para Prop_clinica en este caso
        
    def save(self):
        db.session.add(self)
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()
