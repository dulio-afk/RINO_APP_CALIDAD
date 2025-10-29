from flask import Blueprint, render_template, session, redirect, url_for, flash
from Aplicacion_Web.modelos.diagnostico import Diagnostico
from Aplicacion_Web.modelos.base import db

historial_bp = Blueprint('historial', __name__)

@historial_bp.route('/historial')
def historial():
    id_paciente = session.get('id_paciente')

    if not id_paciente:
        flash("Debes iniciar sesión para ver tu historial.", "warning")
        return redirect(url_for('auth.login'))  # o la ruta correcta a tu login

    diagnosticos = Diagnostico.query.filter_by(id_paciente=id_paciente).order_by(Diagnostico.fecha.desc()).all()

    return render_template('historial.html', diagnosticos=diagnosticos)


@historial_bp.route('/diagnostico/<int:id>/ver')
def ver_detalle(id):
    diagnostico = Diagnostico.query.get_or_404(id)
    return render_template('detalle_diagnostico.html', diagnostico=diagnostico)
