from app.extensions import db

class Visita(db.Model):
    __tablename__ = 'visitas'  # Nombre de la tabla en la base de datos

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date_time = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.String(255), nullable=False)

    # Foreign key hacia Mascota
    mascota_id = db.Column(db.Integer, db.ForeignKey('mascotas.id'), nullable=False)

    # Relación con Mascota
    mascota = db.relationship('Mascota', back_populates='visitas')

    def __init__(self, date_time, description):
        self.date_time = date_time
        self.description = description

    def __repr__(self):
        return f"<Visita(date_time='{self.date_time}', description='{self.description}')>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()