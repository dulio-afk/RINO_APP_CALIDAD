from datetime import datetime
from Aplicacion_Web.modelos.base import db


class Paciente(db.Model):
    __tablename__ = 'paciente'
    
    id_paciente = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido_paterno = db.Column(db.String(100), nullable=False)
    apellido_materno = db.Column(db.String(100), nullable=False)
    edad = db.Column(db.Integer, nullable=False)
    sexo = db.Column(db.String(20), nullable=False)
    dni = db.Column(db.String(15), nullable=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Paciente {self.nombre} {self.apellido_paterno}>'