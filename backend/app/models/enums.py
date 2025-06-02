import enum

class TipoUsuarioEnum(enum.Enum):
    USUARIO = "usuario"
    PROP_MASCOTA = "prop_mascota"
    PROP_CLINICA = "prop_clinica"
    VETERINARIO = "veterinario"
    ADMIN = "admin"
    
class EspecialidadEnum(enum.Enum):
    DERMATOLOGIA = "dermatologia"
    CIRUGIA = "cirugia"
    OFTALMOLOGIA = "oftalmologia"
    MEDICINA_INTERNA = "medicina_interna"
    REHABILITACION = "rehabilitacion"
    
class Stage(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"