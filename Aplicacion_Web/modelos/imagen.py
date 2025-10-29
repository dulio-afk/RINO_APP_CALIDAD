from flask_sqlalchemy import SQLAlchemy
from Aplicacion_Web.modelos.base import db
from datetime import datetime

class Imagen(db.Model):
    __tablename__ = 'imagenes'

    id_imagen = db.Column(db.Integer, primary_key=True)
    id_examen = db.Column(db.Integer, db.ForeignKey('examenes_clinicos.id_examen'), nullable=False)
    ruta_imagen = db.Column(db.String(255), nullable=False)
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow)

    examen = db.relationship('ExamenClinico', backref='imagenes')

    def __repr__(self):
        return f'<Imagen {self.id_imagen} - Examen {self.id_examen}>'
