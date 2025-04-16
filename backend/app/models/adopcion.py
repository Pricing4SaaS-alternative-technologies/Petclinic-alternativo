from app.extensions import db

class Adopcion(db.Model):
    __tablename__ = 'adopciones'  # Nombre de la tabla en la base de datos

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String(255), nullable=False)
    stage = db.Column(db.String(50), nullable=False)

    def __init__(self, description, stage):
        self.description = description
        self.stage = stage

    def __repr__(self):
        return f"<Adopcion(description='{self.description}', stage='{self.stage}')>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()