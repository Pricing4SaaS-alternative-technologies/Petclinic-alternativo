from app.extensions import db

class Clinica(db.Model):
    __tablename__ = 'clinicas'  ## Nombre de la tabla en la BD
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    direccion = db.Column(db.String(100), unique=True, nullable=False)
    telefono = db.Column(db.String(9), unique=True, nullable=False)
    
    propietario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    propietario = db.relationship('Usuario', foreign_keys=[propietario_id])

    
    def __init__(self, nombre, direccion, telefono, propietario_id):
        self.nombre = nombre
        self.direccion = direccion
        self.telefono = telefono
        self.propietario_id = propietario_id
    
    def save(self):
        db.session.add(self)
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()
