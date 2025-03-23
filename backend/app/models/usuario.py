from app import db

class Usuario(db.Model):
    __tablename__ = 'usuarios'  # Nombre de la tabla en la BD
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    contraseña = db.Column(db.String(100), nullable=False)
    
    def __init__(self, nombre, correo, contraseña):
        self.nombre = nombre
        self.correo = correo
        self.contraseña = contraseña
        
        
    @classmethod
    def find_by_username_or_email(cls, username, email):
        return cls.query.filter((cls.username == username) | (cls.email == email)).first()
