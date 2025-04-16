from app.models.enums import TipoUsuarioEnum, EspecialidadEnum
from sqlalchemy.types import JSON

from .usuario import Usuario
from app.extensions import db

class Vet(Usuario):
    __tablename__ = 'vets'

    especialidades = db.Column(JSON, nullable=True)
    
    ciudad = db.Column(db.String(40))

    __mapper_args__ = {
        'polymorphic_identity': TipoUsuarioEnum.DUENO.value,
    }
    def __init__(self, first_name, last_name, username, email, password, especialidades, ciudad):
        super().__init__(first_name, last_name, username, email, password, TipoUsuarioEnum.VET)
        self.ciudad = ciudad
        self.set_especialidades(especialidades)
    
    def set_especialidades(self, especialidades_enum_list):
        self.especialidades = [e.value if isinstance(e, EspecialidadEnum) else EspecialidadEnum(e).value for e in especialidades_enum_list]

    def get_especialidades_enum(self):
        if self.especialidades:
            return [EspecialidadEnum(val) for val in self.especialidades]
        return []