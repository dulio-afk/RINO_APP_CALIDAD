from flask import Blueprint
from Aplicacion_Web.controladores.paciente_controller import registrar_paciente

paciente_bp = Blueprint('paciente', __name__)

@paciente_bp.route('/registro_paciente', methods=['POST'])
def registrar():
    return registrar_paciente()
