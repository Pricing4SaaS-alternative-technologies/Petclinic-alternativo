from app.models.enums import TipoUsuarioEnum, EspecialidadEnum
from sqlalchemy.types import JSON

from .usuario import Usuario
from app.extensions import db

class Veterinario(Usuario):
    __tablename__ = 'veterinarios'
    
    id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), primary_key=True)
    
    especialidades = db.Column(JSON, nullable=True)
    ciudad = db.Column(db.String(40))
    
    clinica_id = db.Column(db.Integer, db.ForeignKey('clinicas.id'), nullable=False)
    clinica = db.relationship('Clinica')

    __mapper_args__ = {
        'polymorphic_identity': TipoUsuarioEnum.VETERINARIO,
    }
    def __init__(self, first_name, last_name, username, email, password, especialidades, ciudad):
        super().__init__(first_name, last_name, username, email, password, TipoUsuarioEnum.VETERINARIO)
        self.ciudad = ciudad
        self.set_especialidades(especialidades)
    
    #almacenamos los values del enum en la bbdd, para type se almacena el enum directamente por que es mas comodo
    def set_especialidades(self, especialidades_enum_list):
        self.especialidades = [e.value if isinstance(e, EspecialidadEnum) else EspecialidadEnum(e).value for e in especialidades_enum_list]

    def get_especialidades_enum(self):
        if self.especialidades:
            return [EspecialidadEnum(val) for val in self.especialidades]
        return []
    
    def save(self):
        db.session.add(self)
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()
