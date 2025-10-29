# Aplicacion_Web/controladores/diagnostico_controlador.py
from Aplicacion_Web.modelos.diagnostico import Diagnostico
from Aplicacion_Web.modelos.base import db

def guardar_diagnostico(id_paciente, id_imagen, clase_predicha, grado_retinopatia, confianza):
    nuevo_diagnostico = Diagnostico(
        id_paciente=id_paciente,
        id_imagen=id_imagen,
        clase_predicha=clase_predicha,
        grado_retinopatia=grado_retinopatia,
        confianza=confianza
    )
    db.session.add(nuevo_diagnostico)
    db.session.commit()
    return nuevo_diagnostico
