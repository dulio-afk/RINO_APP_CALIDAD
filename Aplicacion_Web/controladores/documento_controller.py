import os
from werkzeug.utils import secure_filename
from flask import request, flash, redirect, url_for, current_app
from Aplicacion_Web.modelos.paciente import db, Paciente
from Aplicacion_Web.modelos.examen_clinico import ExamenClinico
from Aplicacion_Web.modelos.imagen import Imagen
from Aplicacion_Web.modelos.documento import Documento
from datetime import datetime

def registrar_todo_con_archivos():
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

        # ===== 3. Guardar imagen =====
        imagen_archivo = request.files.get('imagen')
        if imagen_archivo and imagen_archivo.filename != '':
            filename = secure_filename(imagen_archivo.filename)
            retina_folder = current_app.config['RETINAS_FOLDER']
            os.makedirs(retina_folder, exist_ok=True)
            ruta_absoluta = os.path.join(retina_folder, filename)
            ruta_relativa = f'static/uploads/retinas/{filename}'
            imagen_archivo.save(ruta_absoluta)

            imagen = Imagen(
                id_examen=examen.id_examen,
                ruta_imagen=ruta_relativa
            )
            db.session.add(imagen)
            db.session.commit()

        # ===== 4. Guardar documento =====
        documento_archivo = request.files.get('documento')
        if documento_archivo and documento_archivo.filename != '':
            filename = secure_filename(documento_archivo.filename)
            documento_folder = current_app.config['DOCUMENTOS_FOLDER']
            os.makedirs(documento_folder, exist_ok=True)
            ruta_absoluta = os.path.join(documento_folder, filename)
            ruta_relativa = f'static/uploads/documentos/{filename}'
            documento_archivo.save(ruta_absoluta)

            documento = Documento(
                id_examen=examen.id_examen,
                ruta_documento=ruta_relativa
            )
            db.session.add(documento)
            db.session.commit()

        flash('Todos los datos han sido guardados correctamente', 'success')
        return redirect(url_for('main.sandbox'))

    flash('Error al guardar los datos', 'danger')
    return redirect(url_for('main.sandbox'))
