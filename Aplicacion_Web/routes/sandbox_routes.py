from flask import Blueprint, render_template
from Aplicacion_Web.controladores.decoradores import login_requerido

sandbox_bp = Blueprint('sandbox', __name__)

# 👇 Rutas mínimas para que los tests funcionen
@sandbox_bp.route('/sandbox')
@login_requerido
def sandbox():
    return render_template('sandbox.html')

# Comentamos cualquier código que requiera microservicio
# from Aplicacion_Web.servicio.microservicio import enviar_a_microservicio
# def funcion_que_usa_microservicio():
#     return enviar_a_microservicio(...)
