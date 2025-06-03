from app.extensions import db

class Visita(db.Model):
    __tablename__ = 'visitas'  # Nombre de la tabla en la base de datos

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha = db.Column(db.DateTime, nullable=False)
    descripcion = db.Column(db.String(255), nullable=False)

    veterinario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    veterinario = db.relationship('Usuario', foreign_keys=[veterinario_id])

    # Foreign key hacia Mascota
    mascota_id = db.Column(db.Integer, db.ForeignKey('mascotas.id'), nullable=False)
    mascota = db.relationship('Mascota')

    def __init__(self, fecha, descripcion):
        self.fecha = fecha
        self.descripcion = descripcion

    def __repr__(self):
        return f"<Visita(fecha='{self.fecha}', descripcion='{self.descripcion}')>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()