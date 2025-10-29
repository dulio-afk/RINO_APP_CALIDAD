from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from Aplicacion_Web.controladores.controlador_usuario import autenticar_usuario
from Aplicacion_Web.modelos.base import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        contrasena = request.form['contrasena']
        usuario = autenticar_usuario(correo, contrasena)

        if usuario:
            session['usuario_id'] = usuario.id
            session['usuario_nombre'] = usuario.nombre
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('main.dashboard'))  # Ajusta al nombre de tu vista principal
        else:
            flash('Correo o contraseña incorrectos', 'danger')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada exitosamente', 'info')
    return redirect(url_for('auth.login'))
