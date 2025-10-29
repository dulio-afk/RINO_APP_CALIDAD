from flask import Blueprint
from Aplicacion_Web.controladores.examen_clinico_controller import registrar_paciente_y_examen

examen_clinico_bp = Blueprint('examen', __name__)

@examen_clinico_bp.route('/registro_examen', methods=['POST'])
def registrar_todo():
    return registrar_paciente_y_examen()
