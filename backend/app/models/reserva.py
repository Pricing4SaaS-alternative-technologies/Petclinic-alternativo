from app.extensions import db

class Reserva(db.Model):
    __tablename__ = 'reservas'  # Nombre de la tabla en la base de datos

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    
    # Si se eliminan las habitaciones, se eliminan en cascada las reservas asociadas
    habitacion_id = db.Column( db.Integer, db.ForeignKey('habitaciones_hotel.id',ondelete='CASCADE'), nullable=False)
    habitacion = db.relationship('Habitacion_hotel', passive_deletes=True)

    # Si se borran las mascotas, se eliminan en cascada las reservas asociadas
    mascota_id = db.Column(db.Integer, db.ForeignKey('mascotas.id', ondelete='CASCADE'), nullable=False)
    mascota = db.relationship('Mascota', passive_deletes=True)

    def __init__(self, fecha_inicio, fecha_fin, habitacion_id, mascota_id):
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.habitacion_id = habitacion_id
        self.mascota_id = mascota_id

    def __repr__(self):
        return f"<Reserva(fecha_inicio='{self.fecha_inicio}', fecha_fin='{self.fecha_fin}')>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()