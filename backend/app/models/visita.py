from app.extensions import db
from sqlalchemy.ext.hybrid import hybrid_property

class Visita(db.Model):
    __tablename__ = 'visitas'  # Nombre de la tabla en la base de datos

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha = db.Column(db.DateTime, nullable=False)
    descripcion = db.Column(db.String(255), nullable=False)

    veterinario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True)
    veterinario = db.relationship('Usuario', foreign_keys=[veterinario_id])

    # Foreign key hacia Mascota
    mascota_id = db.Column(db.Integer, db.ForeignKey('mascotas.id', ondelete='CASCADE'), nullable=False)
    mascota = db.relationship('Mascota', back_populates='visitas', passive_deletes=True)

    def __init__(self, fecha, descripcion, mascota_id):
        self.fecha = fecha
        self.descripcion = descripcion
        self.mascota_id = mascota_id

    def __repr__(self):
        return f"<Visita(fecha='{self.fecha}', descripcion='{self.descripcion}')>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    @hybrid_property
    def date_time(self):
        return self.fecha

    @date_time.setter
    def date_time(self, val):
        self.fecha = val

    @hybrid_property
    def description(self):
        return self.descripcion

    @description.setter
    def description(self, val):
        self.descripcion = val

    @hybrid_property
    def dueno_id(self):
        """Devuelve el id del dueño de la mascota asociada."""
        return self.mascota.dueño_id if self.mascota else None

    @hybrid_property
    def clinica_id(self):
        """Devuelve el id de la clínica del dueño de la mascota."""
        # asumiendo que Cliente→Prop_mascota tiene clinica_id
        return getattr(self.mascota.dueño, 'clinica_id', None)