from flask import request, redirect, url_for, flash
from Aplicacion_Web.modelos.paciente import db, Paciente
from datetime import datetime

def registrar_paciente():
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre = request.form.get('nombre', '').strip()
            apellido_paterno = request.form.get('apellido_paterno', '').strip()
            apellido_materno = request.form.get('apellido_materno', '').strip()
            edad = int(request.form.get('edad', 0))
            sexo = request.form.get('sexo', '').strip()
            dni = request.form.get('dni', '').strip()

            # Validaciones mínimas
            if not all([nombre, apellido_paterno, apellido_materno, edad > 0, sexo]):
                flash('Todos los campos obligatorios deben estar completos.', 'warning')
                return redirect(url_for('sandbox.sandbox'))

            # Crear objeto Paciente
            nuevo_paciente = Paciente(
                nombre=nombre,
                apellido_paterno=apellido_paterno,
                apellido_materno=apellido_materno,
                edad=edad,
                sexo=sexo,
                dni=dni if dni else None,
                fecha_registro=datetime.utcnow()
            )

            # Guardar en la base de datos
            db.session.add(nuevo_paciente)
            db.session.commit()

            flash('Paciente registrado correctamente', 'success')
            return redirect(url_for('sandbox.sandbox'))

        except ValueError:
            flash('Edad no válida. Por favor ingresa un número entero.', 'danger')
            return redirect(url_for('sandbox.sandbox'))

        except Exception as e:
            db.session.rollback()
            flash(f'Ocurrió un error al registrar el paciente: {str(e)}', 'danger')
            return redirect(url_for('sandbox.sandbox'))

    # Si no es POST
    flash('Método no permitido', 'danger')
    return redirect(url_for('sandbox.sandbox'))
