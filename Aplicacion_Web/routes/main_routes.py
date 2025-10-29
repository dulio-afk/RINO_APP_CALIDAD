import base64
from flask import current_app, jsonify, render_template, make_response, url_for
import io
import os
from matplotlib import pyplot as plt
from prompt_toolkit import HTML
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from typing import Counter
from flask import Blueprint, flash, make_response, render_template, send_file
from sqlalchemy import func
from flask import render_template, make_response
from xhtml2pdf import pisa
import spacy
import networkx as nx
from pyvis.network import Network
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from Aplicacion_Web.controladores.decoradores import login_requerido
from Aplicacion_Web.modelos.base import db
from Aplicacion_Web.modelos.examen_clinico import ExamenClinico
from Aplicacion_Web.modelos.paciente import  Paciente
from Aplicacion_Web.modelos.imagen import Imagen
from Aplicacion_Web.modelos.diagnostico import Diagnostico
from Aplicacion_Web.modelos.documento import Documento
from Aplicacion_Web.servicio.pdf_extractor import extraer_texto_por_id_documento
from Aplicacion_Web.servicio.gemini_servicio import generar_recomendacion
from Aplicacion_Web.servicio.analisis_clinico_gemini import analizar_sintomas_con_gemini

main_bp = Blueprint('main', __name__)

@main_bp.route('/dashboard')
@login_requerido
def dashboard():
    # Estadísticas
    pacientes = Paciente.query.all()
    edades = [p.edad for p in pacientes if p.edad is not None]

    sexo_db = db.session.query(Paciente.sexo, func.count(Paciente.id_paciente))\
                   .group_by(Paciente.sexo).all()
    conteo_sexo = {s: c for s, c in sexo_db}

    grados_db = db.session.query(Diagnostico.grado_retinopatia, func.count(Diagnostico.id_diagnostico))\
                     .group_by(Diagnostico.grado_retinopatia).all()
    conteo_grados = {g: c for g, c in grados_db}

    total = sum(conteo_grados.values()) or 1
    categorias = {g: round(c * 100 / total, 2) for g, c in conteo_grados.items()}

    # Análisis clínico
    examenes = ExamenClinico.query.all()
    if examenes:
        res = analizar_sintomas_con_gemini(examenes)
        relaciones = res.get("relaciones", [])
        temas = res.get("temas_observaciones", [])
        sintomas_clas = res.get("sintomas_clasificados", {})
    else:
        relaciones, temas, sintomas_clas = [], [], {}

    # Construir grafo Vis.js
    nodos, aristas = {}, []
    for rel in relaciones:
        a, b = rel.get("sintomas", [None, None])
        fuerza = rel.get("fuerza", "")
        if a and b:
            nodos.setdefault(a, {"id": a, "label": a})
            nodos.setdefault(b, {"id": b, "label": b})
            aristas.append({"from": a, "to": b, "label": fuerza})

    grafo_sintomas = {"nodes": list(nodos.values()), "edges": aristas}

    return render_template(
        'dashboard.html',
        edades=edades,
        conteo_sexo=conteo_sexo,
        conteo_grados=conteo_grados,
        categorias=categorias,
        sintomas_clasificados=sintomas_clas,
        nube_observaciones=temas,
        grafo_sintomas=grafo_sintomas
    )

@main_bp.route('/historial')
def historial():
    # Cargar todos los pacientes con sus diagnósticos más recientes
    pacientes = Paciente.query.all()

    historial_data = []
    for paciente in pacientes:
        for examen in paciente.examenes:
            diagnostico = Diagnostico.query.filter_by(id_paciente=paciente.id_paciente).join(Imagen).filter(Imagen.id_examen == examen.id_examen).order_by(Diagnostico.fecha_diagnostico.desc()).first()
            if diagnostico:
                historial_data.append({
                    'paciente': paciente,
                    'examen': examen,
                    'imagen': diagnostico.imagen,
                    'diagnostico': diagnostico,
                })

    return render_template('historial.html', historial=historial_data)

@main_bp.route('/detalle_historial/<int:id_diagnostico>')
def detalle_historial(id_diagnostico):
    diagnostico = Diagnostico.query.get_or_404(id_diagnostico)
    paciente = Paciente.query.get(diagnostico.id_paciente)
    imagen = Imagen.query.get(diagnostico.id_imagen)
    examen = ExamenClinico.query.filter_by(id_paciente=paciente.id_paciente).order_by(ExamenClinico.fecha_examen.desc()).first()
    documentos = Documento.query.join(ExamenClinico).filter(ExamenClinico.id_paciente == paciente.id_paciente).all()

    return render_template('detalle_diagnostico.html', diagnostico=diagnostico, paciente=paciente, imagen=imagen, examen=examen, documentos=documentos)

@main_bp.route('/analizar-documento/<int:id_documento>')
def analizar_documento(id_documento):
    analisis = extraer_texto_por_id_documento(id_documento)
    documento = Documento.query.get(id_documento)

    # Obtener el examen clínico relacionado
    examen = ExamenClinico.query.get(documento.id_examen)

    # Obtener el paciente desde el examen
    paciente = Paciente.query.get(examen.id_paciente) if examen else None

    return render_template(
        "analisis_documento.html",
        analisis=analisis,
        paciente=paciente,
        documento=documento
    )


@main_bp.route('/informacion_gemini/<int:id_diagnostico>')
def informacion_gemini(id_diagnostico):
    # Obtener el diagnóstico
    diagnostico = Diagnostico.query.get_or_404(id_diagnostico)

    # Obtener el paciente
    paciente = Paciente.query.get_or_404(diagnostico.id_paciente)

    # Obtener el examen más reciente del paciente
    examen = ExamenClinico.query.filter_by(id_paciente=paciente.id_paciente)\
                                 .order_by(ExamenClinico.fecha_examen.desc())\
                                 .first()

    # Obtener todos los documentos relacionados con los exámenes del paciente
    from Aplicacion_Web.modelos.documento import Documento  # Asegúrate de importar correctamente
    documentos = Documento.query.join(ExamenClinico)\
        .filter(ExamenClinico.id_paciente == paciente.id_paciente).all()

    # Extraer texto de los documentos
    informes_pdf = []
    for doc in documentos:
        contenido = extraer_texto_por_id_documento(doc.id_documento)
        informes_pdf.append({
            "nombre": os.path.basename(doc.ruta_documento),  # Obtén solo el nombre del archivo
            "contenido": contenido
        })

    # Consolidar datos clínicos del paciente para enviar a Gemini
    datos_paciente = {
        "nombre": paciente.nombre,
        "apellido_paterno": paciente.apellido_paterno,
        "apellido_materno": paciente.apellido_materno,
        "edad": paciente.edad,
        "sexo": paciente.sexo,
        "glucosa": examen.nivel_glucosa if examen else "No disponible",
        "presion": examen.presion if examen else "No disponible",
        "sintomas": examen.sintomas if examen else "No registrados",
        "observaciones_examen": examen.observaciones if examen else "No registradas",
        "grado_retinopatia": diagnostico.grado_retinopatia,
        "confianza": diagnostico.confianza,
        "fecha_diagnostico": diagnostico.fecha_diagnostico.strftime("%Y-%m-%d") if diagnostico.fecha_diagnostico else "No registrada"
    }

    # Generar recomendación usando IA (modelo Gemini)
    recomendacion = generar_recomendacion(datos_paciente, informes_pdf)

    # Renderizar la plantilla
    return render_template(
        "recomendacion_paciente.html",
        recomendacion=recomendacion,
        paciente=paciente,
        diagnostico=diagnostico,
        examen=examen,
    )

from datetime import datetime

@main_bp.route('/historial_paciente/<int:id_paciente>')
@login_requerido
def historial_paciente(id_paciente):
    paciente = Paciente.query.get_or_404(id_paciente)

    examenes = ExamenClinico.query.filter_by(id_paciente=id_paciente).order_by(ExamenClinico.fecha_examen.desc()).all()

    historial_data = []
    fechas = []
    grados = []
    confianzas = []

    for examen in examenes:
        diagnosticos = Diagnostico.query.join(Imagen).filter(
            Imagen.id_examen == examen.id_examen,
            Diagnostico.id_paciente == id_paciente
        ).order_by(Diagnostico.fecha_diagnostico.desc()).all()

        for diagnostico in diagnosticos:
            historial_data.append({
                'paciente': paciente,
                'examen': examen,
                'diagnostico': diagnostico,
                'imagen': diagnostico.imagen
            })

            fechas.append(diagnostico.fecha_diagnostico.strftime('%d/%m/%Y'))
            grados.append(diagnostico.grado_retinopatia)
            confianzas.append(diagnostico.confianza)
            conteo_grados = dict(Counter(grados)) if grados else {}

    return render_template('historial_paciente.html',
                           historial=historial_data,
                           paciente=paciente,
                           fechas=fechas,
                           grados=grados,
                           confianzas=confianzas,
                           conteo_grados=conteo_grados)


@main_bp.route('/informacion')
@login_requerido
def informacion():
    return render_template('informacion.html')

@main_bp.route('/sandbox')
@login_requerido
def sandbox():
    return render_template('sandbox.html')

@main_bp.route('/exportar_diagnostico_pdf/<int:id_diagnostico>')
def exportar_diagnostico_pdf(id_diagnostico):
    diagnostico = Diagnostico.query.get_or_404(id_diagnostico)
    paciente = Paciente.query.get(diagnostico.id_paciente)
    imagen = Imagen.query.get(diagnostico.id_imagen)
    examen = ExamenClinico.query.filter_by(id_paciente=paciente.id_paciente).order_by(ExamenClinico.fecha_examen.desc()).first()
    documentos = Documento.query.join(ExamenClinico).filter(ExamenClinico.id_paciente == paciente.id_paciente).all()

    # 👇 Ruta absoluta al archivo de imagen (necesario para que xhtml2pdf la procese)
    imagen_path = None
    if imagen and imagen.ruta_imagen:
        imagen_rel_path = imagen.ruta_imagen.replace("\\", "/").split("static/")[-1]
        imagen_path = os.path.join(current_app.root_path, "static", imagen_rel_path)

    # Renderizar HTML con ruta absoluta de imagen
    html = render_template('pdf/plantilla_pdf_diagnostico.html',
                           diagnostico=diagnostico,
                           paciente=paciente,
                           imagen=imagen,
                           imagen_path=imagen_path,
                           examen=examen,
                           documentos=documentos)

    resultado = io.BytesIO()
    pisa_status = pisa.CreatePDF(io.StringIO(html), dest=resultado, link_callback=resolve_resource)

    if pisa_status.err:
        return "Error al generar el PDF", 500

    response = make_response(resultado.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=diagnostico_{id_diagnostico}.pdf'
    return response

# 👇 Función necesaria para que xhtml2pdf pueda cargar recursos (imágenes locales)
def resolve_resource(uri, rel):
    path = os.path.join(current_app.root_path, uri.strip("/"))
    return path


@main_bp.route('/descargar_pdf/<int:id_paciente>')
def descargar_pdf(id_paciente):
    paciente = Paciente.query.get_or_404(id_paciente)
    diagnosticos = Diagnostico.query.filter_by(id_paciente=id_paciente).order_by(Diagnostico.fecha_diagnostico).all()
    examenes = ExamenClinico.query.filter_by(id_paciente=id_paciente).all()
    documentos = Documento.query.join(ExamenClinico).filter(ExamenClinico.id_paciente == id_paciente).all()

    # Crear gráficos
    fechas = [d.fecha_diagnostico.strftime("%d/%m/%Y") for d in diagnosticos]
    grados = [d.grado_retinopatia for d in diagnosticos]
    confianzas = [d.confianza for d in diagnosticos]

    def crear_grafico(datos, titulo, etiqueta_y, color):
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.plot(fechas, datos, marker='o', color=color)
        ax.set_title(titulo)
        ax.set_xlabel("Fecha")
        ax.set_ylabel(etiqueta_y)
        ax.grid(True)
        buffer = io.BytesIO()
        plt.tight_layout()
        fig.savefig(buffer, format='png')
        buffer.seek(0)
        grafico_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close()
        return grafico_base64

    grafico_grado = crear_grafico(grados, "Evolución del Grado", "Grado", "blue")
    grafico_confianza = crear_grafico(confianzas, "Confianza del Modelo", "Confianza", "green")

    # Render HTML
    html = render_template("pdf/paciente_historial.html", paciente=paciente,
                           diagnosticos=diagnosticos,
                           examenes=examenes,
                           documentos=documentos,
                           grafico_grado=grafico_grado,
                           grafico_confianza=grafico_confianza,
                           fecha_generacion=datetime.now())

    # Generar PDF
    pdf_buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)
    pdf_buffer.seek(0)

    response = make_response(pdf_buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=Historial_{paciente.nombre}.pdf'
    return response