from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from Aplicacion_Web.modelos.base import db

class ExamenClinico(db.Model):
    __tablename__ = 'examenes_clinicos'

    id_examen = db.Column(db.Integer, primary_key=True)
    id_paciente = db.Column(db.Integer, db.ForeignKey('paciente.id_paciente'), nullable=False)
    nivel_glucosa = db.Column(db.Float)
    presion = db.Column(db.String(20))
    sintomas = db.Column(db.Text)
    observaciones = db.Column(db.Text)
    fecha_examen = db.Column(db.DateTime, default=datetime.utcnow)

    paciente = db.relationship('Paciente', backref='examenes')

    def __repr__(self):
        return f'<ExamenClinico {self.id_examen} - Paciente {self.id_paciente}>'
