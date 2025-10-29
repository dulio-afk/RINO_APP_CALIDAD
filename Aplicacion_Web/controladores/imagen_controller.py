import os
from werkzeug.utils import secure_filename
from flask import request, flash, redirect, url_for, current_app
from Aplicacion_Web.modelos.base import db
from Aplicacion_Web.modelos.paciente import  Paciente
from Aplicacion_Web.modelos.examen_clinico import ExamenClinico
from Aplicacion_Web.modelos.imagen import Imagen
from datetime import datetime

def registrar_todo_con_imagen():
    if request.method == 'POST':
        # ===== 1. Guardar paciente =====
        nombre = request.form['nombre']
        apellido_paterno = request.form['apellido_paterno']
        apellido_materno = request.form['apellido_materno']
        edad = int(request.form['edad'])
        sexo = request.form['sexo']
        dni = request.form.get('dni')

        nuevo_paciente = Paciente(
            nombre=nombre,
            apellido_paterno=apellido_paterno,
            apellido_materno=apellido_materno,
            edad=edad,
            sexo=sexo,
            dni=dni,
            fecha_registro=datetime.utcnow()
        )
        db.session.add(nuevo_paciente)
        db.session.commit()

        # ===== 2. Guardar examen =====
        nivel_glucosa = request.form.get('glucosa')
        presion = request.form.get('presion')
        sintomas = request.form.get('sintomas')
        observaciones = request.form.get('observaciones')

        examen = ExamenClinico(
            id_paciente=nuevo_paciente.id_paciente,
            nivel_glucosa=nivel_glucosa,
            presion=presion,
            sintomas=sintomas,
            observaciones=observaciones,
            fecha_examen=datetime.utcnow()
        )
        db.session.add(examen)
        db.session.commit()

        # ===== 3. Guardar imagen si existe =====
        imagen_archivo = request.files.get('imagen')
        if imagen_archivo and imagen_archivo.filename != '':
            filename = secure_filename(imagen_archivo.filename)
            retina_folder = current_app.config['RETINAS_FOLDER']

            # Asegúrate que exista la carpeta
            os.makedirs(retina_folder, exist_ok=True)

            ruta_absoluta = os.path.join(retina_folder, filename)
            ruta_relativa = f'static/uploads/retinas/{filename}'

            # Guardar imagen físicamente
            imagen_archivo.save(ruta_absoluta)

            # Guardar en BD
            imagen = Imagen(
                id_examen=examen.id_examen,
                ruta_imagen=ruta_relativa,
                fecha_subida=datetime.utcnow()
            )
            db.session.add(imagen)
            db.session.commit()

        flash('Paciente, examen clínico e imagen registrados con éxito', 'success')
        return redirect(url_for('main.sandbox'))

    flash('Error al guardar datos', 'danger')
    return redirect(url_for('main.sandbox'))
