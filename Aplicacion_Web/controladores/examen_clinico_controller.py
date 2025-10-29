from flask import request, redirect, url_for, flash
from Aplicacion_Web.modelos.paciente import  Paciente
from Aplicacion_Web.modelos.examen_clinico import ExamenClinico
from datetime import datetime
from Aplicacion_Web.modelos.base import db

def registrar_paciente_y_examen():
    if request.method == 'POST':
        # Captura datos del paciente
        nombre = request.form['nombre']
        apellido_paterno = request.form['apellido_paterno']
        apellido_materno = request.form['apellido_materno']
        edad = int(request.form['edad'])
        sexo = request.form['sexo']
        dni = request.form.get('dni')

        # Crea paciente
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

        # Captura datos clínicos
        nivel_glucosa = request.form.get('glucosa')
        presion = request.form.get('presion')
        sintomas = request.form.get('sintomas')
        observaciones = request.form.get('observaciones')

        # Crea examen clínico con el id del paciente recién creado
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

        flash('Paciente y examen clínico registrados correctamente', 'success')
        return redirect(url_for('main.sandbox'))

    flash('Error al registrar datos', 'danger')
    return redirect(url_for('main.sandbox'))
