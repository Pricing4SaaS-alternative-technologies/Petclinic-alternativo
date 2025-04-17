from app.extensions import db

class Reserva(db.Model):
    __tablename__ = 'reservas'  # Nombre de la tabla en la base de datos

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    
    # 1) foreign key a la tabla de habitaciones
    habitacion_id = db.Column(
        db.Integer,
        db.ForeignKey('habitaciones_hotel.id'),
        nullable=False
    )
    # 2) relación hacia HabitacionHotel
    habitacion = db.relationship(
        'HabitacionHotel',
        back_populates='reservas'
    )

    # Foreign key hacia Mascota
    mascota_id = db.Column(db.Integer, db.ForeignKey('mascotas.id'), nullable=False)

    # Relación con Mascota
    mascota = db.relationship('Mascota', back_populates='reservas')


    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def __repr__(self):
        return f"<Reserva(start_date='{self.start_date}', end_date='{self.end_date}')>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()