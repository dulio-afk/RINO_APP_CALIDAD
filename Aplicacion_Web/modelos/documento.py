from flask_sqlalchemy import SQLAlchemy
from Aplicacion_Web.modelos.base import db
from datetime import datetime

class Documento(db.Model):
    __tablename__ = 'documentos'

    id_documento = db.Column(db.Integer, primary_key=True)
    id_examen = db.Column(db.Integer, db.ForeignKey('examenes_clinicos.id_examen'), nullable=False)
    ruta_documento = db.Column(db.String(255), nullable=False)
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow)

    examen = db.relationship('ExamenClinico', backref='documentos')

    def __repr__(self):
        return f'<Documento {self.id_documento} - Examen {self.id_examen}>'
