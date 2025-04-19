from enum import Enum as PyEnum
from app.extensions import db

class ConsultationStatus(PyEnum):
    PENDING = "PENDING"
    ANSWERED = "ANSWERED"
    CLOSED = "CLOSED"


class Consulta(db.Model):
    __tablename__ = 'consultas'  ## Nombre de la tabla en la BD
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(50), nullable=False)
    isClinicComment = db.Column(db.Boolean, nullable=False, default=False)
    status = db.Column(db.Enum(ConsultationStatus), nullable=False, default=ConsultationStatus.PENDING)
    
    # Foreign key a mascotas.id
    mascota_id = db.Column(db.Integer, db.ForeignKey('mascotas.id'), nullable=False)
    mascota = db.relationship('Mascota')

    
    def __init__(self, title, isClinicComment, status=ConsultationStatus.PENDING):
        self.title = title
        self.isClinicComment = isClinicComment
        self.status = status
        
    
    def save(self):
        db.session.add(self)
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()
