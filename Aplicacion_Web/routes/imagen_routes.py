from flask import Blueprint
from Aplicacion_Web.controladores.imagen_controller import registrar_todo_con_imagen

imagen_bp = Blueprint('imagen', __name__)

@imagen_bp.route('/registro_imagen', methods=['POST'])
def guardar_todo():
    return registrar_todo_con_imagen()
