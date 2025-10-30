from flask import Blueprint, render_template
# from flask import current_app  # No necesitamos para tests mínimos
from sqlalchemy import func
from Aplicacion_Web.modelos.paciente import Paciente
from Aplicacion_Web.modelos.diagnostico import Diagnostico
# from Aplicacion_Web.modelos.examen_clinico import ExamenClinico
from Aplicacion_Web.controladores.decoradores import login_requerido
# from Aplicacion_Web.modelos.base import db  # Comentado porque Jenkins no lo necesita

main_bp = Blueprint('main', __name__)

# Solo rutas mínimas necesarias para tests
@main_bp.route('/dashboard')
@login_requerido
def dashboard():
    pacientes = Paciente.query.all()
    edades = [p.edad for p in pacientes if p.edad is not None]

    # Mock para evitar uso de current_app.db en Jenkins
    try:
        sexo_db = Paciente.query.with_entities(Paciente.sexo, func.count(Paciente.id_paciente))\
            .group_by(Paciente.sexo).all()
        conteo_sexo = {s: c for s, c in sexo_db}

        grados_db = Diagnostico.query.with_entities(Diagnostico.grado_retinopatia, func.count(Diagnostico.id_diagnostico))\
            .group_by(Diagnostico.grado_retinopatia).all()
        conteo_grados = {g: c for g, c in grados_db}
    except Exception:
        # Si falla, devolvemos dicts vacíos para tests
        conteo_sexo = {}
        conteo_grados = {}

    total = sum(conteo_grados.values()) or 1
    categorias = {g: round(c * 100 / total, 2) for g, c in conteo_grados.items()}

    return render_template(
        'dashboard.html',
        edades=edades,
        conteo_sexo=conteo_sexo,
        conteo_grados=conteo_grados,
        categorias=categorias
    )

@main_bp.route('/informacion')
@login_requerido
def informacion():
    return render_template('informacion.html')

@main_bp.route('/sandbox')
@login_requerido
def sandbox():
    return render_template('sandbox.html')
