from flask import Blueprint, jsonify, render_template, request, flash, redirect, url_for
from Aplicacion_Web.modelos.paciente import db, Paciente
from Aplicacion_Web.modelos.diagnostico import Diagnostico
from Aplicacion_Web.modelos.documento import Documento
from Aplicacion_Web.modelos.imagen import Imagen
from Aplicacion_Web.modelos.examen_clinico import ExamenClinico
from Aplicacion_Web.configuracion import Configuracion
from Aplicacion_Web.servicio.microservicio import enviar_a_microservicio

import os
from datetime import datetime
from werkzeug.utils import secure_filename

sandbox_bp = Blueprint('sandbox', __name__)

UPLOAD_FOLDER_IMAGENES = 'Aplicacion_Web/static/uploads/retinas'
UPLOAD_FOLDER_DOCUMENTOS = 'Aplicacion_Web/static/uploads/documentos'

@sandbox_bp.route('/sandbox', methods=['GET', 'POST'])
def sandbox():
    if request.method == 'POST':
        try:
            # Paso 1: Datos del paciente
            nombre = request.form.get('nombre').strip()
            apellido_paterno = request.form.get('apellido_paterno').strip()
            apellido_materno = request.form.get('apellido_materno').strip()
            edad = int(request.form.get('edad'))
            sexo = request.form.get('sexo').strip()
            dni = request.form.get('dni', '').strip()

            # Verificar si el paciente ya existe
            paciente = Paciente.query.filter_by(dni=dni).first()

            # Si no existe, lo creamos
            if not paciente:
                paciente = Paciente(
                    nombre=nombre,
                    apellido_paterno=apellido_paterno,
                    apellido_materno=apellido_materno,
                    edad=edad,
                    sexo=sexo,
                    dni=dni if dni else None,
                    fecha_registro=datetime.utcnow()
                )
                db.session.add(paciente)
                db.session.commit()

            # Paso 2: Examen clínico
            nivel_glucosa = float(request.form.get('nivel_glucosa', 0))
            presion = request.form.get('presion', '')
            sintomas = request.form.get('sintomas', '')
            observaciones = request.form.get('observaciones', '')

            examen = ExamenClinico(
                id_paciente=paciente.id_paciente,
                nivel_glucosa=nivel_glucosa,
                presion=presion,
                sintomas=sintomas,
                observaciones=observaciones,
                fecha_examen=datetime.utcnow()
            )
            db.session.add(examen)
            db.session.commit()

            # Paso 3: Subida de imagen
            imagen_file = request.files.get('imagen')
            if not imagen_file or imagen_file.filename == '':
                flash("Debes subir una imagen de retina.", "danger")
                return redirect(request.url)

            if not Configuracion.extension_valida(imagen_file.filename):
                flash("Formato de archivo no permitido.", "danger")
                return redirect(request.url)

            filename = secure_filename(imagen_file.filename)
            ruta = os.path.join(UPLOAD_FOLDER_IMAGENES, filename)
            imagen_file.save(ruta)

            imagen = Imagen(
                id_examen=examen.id_examen,
                ruta_imagen=ruta,
                fecha_subida=datetime.utcnow()
            )
            db.session.add(imagen)
            db.session.commit()

            # Paso 4: Enviar imagen al microservicio para diagnóstico
            resultado = enviar_a_microservicio(ruta, Configuracion.IA_MICROSERVICE_URL)

            if resultado:
                diagnostico = Diagnostico(
                    id_paciente=paciente.id_paciente,
                    id_imagen=imagen.id_imagen,
                    clase_predicha=resultado['clase_predicha'],
                    grado_retinopatia=resultado['grado_retinopatia'],
                    confianza=resultado['confianza'],
                    fecha_diagnostico=datetime.utcnow()
                )
                db.session.add(diagnostico)
                flash(f"✅ Diagnóstico: {resultado['grado_retinopatia']} (Confianza: {resultado['confianza']*100:.2f}%)", "success")
            else:
                flash("❌ Error en la predicción. Intenta nuevamente.", "danger")

            # Paso 5: Documentos adicionales
            documentos = request.files.getlist('otros_archivos[]')
            for doc in documentos:
                if doc and doc.filename != '':
                    doc_filename = secure_filename(doc.filename)
                    doc_ruta = os.path.join(UPLOAD_FOLDER_DOCUMENTOS, doc_filename)
                    doc.save(doc_ruta)

                    documento = Documento(
                        id_examen=examen.id_examen,
                        ruta_documento=doc_ruta,
                        fecha_subida=datetime.utcnow()
                    )
                    db.session.add(documento)

            db.session.commit()
            flash('✅ Todo el diagnóstico fue procesado y guardado exitosamente.', 'success')
            return redirect(url_for('main.historial'))

        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error al procesar el diagnóstico: {e}', 'danger')
            return redirect(url_for('sandbox.sandbox'))

    return render_template('sandbox.html')

@sandbox_bp.route('/buscar_paciente', methods=['GET'])
def buscar_paciente():
    dni = request.args.get('dni', '').strip()
    if not dni:
        return jsonify([])

    pacientes = Paciente.query.filter(Paciente.dni.like(f'{dni}%')).all()
    resultado = [{
        'id': p.id_paciente,
        'dni': p.dni,
        'nombre': p.nombre,
        'apellido_paterno': p.apellido_paterno,
        'apellido_materno': p.apellido_materno,
        'edad': p.edad,
        'sexo': p.sexo
    } for p in pacientes]
    return jsonify(resultado)