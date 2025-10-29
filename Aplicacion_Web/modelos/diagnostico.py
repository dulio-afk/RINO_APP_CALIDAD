from Aplicacion_Web.modelos.base import db
from datetime import datetime

class Diagnostico(db.Model):
    __tablename__ = 'diagnostico'

    id_diagnostico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_imagen = db.Column(db.Integer, db.ForeignKey('imagenes.id_imagen'), nullable=True)
    id_paciente = db.Column(db.Integer, db.ForeignKey('paciente.id_paciente'), nullable=False)
    clase_predicha = db.Column(db.Integer)
    grado_retinopatia = db.Column(db.String(50))
    confianza = db.Column(db.Float)
    fecha_diagnostico = db.Column(db.DateTime, default=datetime.utcnow)

    imagen = db.relationship('Imagen', backref='diagnostico')

    def __repr__(self):
        return f'<Diagnostico {self.id_diagnostico} - Imagen {self.id_imagen}>'
