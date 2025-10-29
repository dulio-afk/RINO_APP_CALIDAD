from flask import Blueprint
from Aplicacion_Web.controladores.documento_controller import registrar_todo_con_archivos

documento_bp = Blueprint('documento', __name__)

@documento_bp.route('/registro_documento', methods=['POST'])
def guardar_todo():
    return registrar_todo_con_archivos()
