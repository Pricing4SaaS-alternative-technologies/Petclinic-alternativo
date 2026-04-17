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
    
class EstadoPeticion(enum.Enum):
    PENDIENTE = "pendiente"
    APROBADA = "aprobada"
    RECHAZADA = "rechazada"

class EstadoConsulta(enum.Enum):
    PENDIENTE = "pendiente"
    RESUELTA = "resuelta"
    
class TipoMascota(enum.Enum):
    GATO = "gato"
    PERRO = "perro"
    REPTIL = "reptil"
    PAJARO = "pajaro"
    HAMSTER = "hamster"
    TORTUGA = "tortuga"

class TamañoHabitacion(enum.Enum):
    ACOGEDOR = "acogedor"   
    MEDIANO = "mediano"
    KING_SIZE = "king_size"