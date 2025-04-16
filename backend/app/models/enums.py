import enum

class TipoUsuarioEnum(enum.Enum):
    USUARIO = "usuario"
    PROP_MASCOTA = "prop_mascota"
    PROP_CLINICA = "prop_clinica"
    VET = "vet"
    ADMIN = "admin"
    
class EspecialidadEnum(enum.Enum):
    DERMATOLOGIA = "dermatologia"
    CIRUGIA = "cirugia"
    OFTALMOLOGIA = "oftalmologia"
    MEDICINA_INTERNA = "medicina_interna"
    REHABILITACION = "rehabilitacion"