from app.extensions import db

class Respuesta_consulta(db.Model):
    __tablename__ = 'respuesta_consulta'  ## Nombre de la tabla en la BD
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(100), unique=True, nullable=False)
    fecha_creacion   = db.Column(db.DateTime, nullable=False)

    # Si se eliminan las consultas, se eliminan en cascada las respuestas asociadas
    consulta_id = db.Column(db.Integer, db.ForeignKey('consultas.id'), nullable=False, unique=True)
    consulta = db.relationship('Consulta', foreign_keys=[consulta_id])



    def __init__(self, titulo, descripcion, fecha_creacion, consulta_id):
        self.titulo = titulo
        self.descripcion = descripcion
        self.fecha_creacion = fecha_creacion
        self.consulta_id = consulta_id
    
    def save(self):
        db.session.add(self)
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()
