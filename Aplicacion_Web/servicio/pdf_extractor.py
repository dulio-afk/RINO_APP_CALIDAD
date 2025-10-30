"""
import fitz  # PyMuPDF
from google.generativeai import GenerativeModel, configure
from Aplicacion_Web.modelos.documento import Documento

# Configurar Gemini
configure(api_key="AIzaSyAVvi2N0McSfzmBiBryYI24gfsjgU1EpYc")  # <-- Reemplaza con tu clave segura
modelo_gemini = GenerativeModel("gemini-2.5-flash")


def extraer_texto_pdf(ruta_pdf: str) -> str:
    """
    Extrae el texto de un archivo PDF utilizando PyMuPDF.
    """
    texto_pdf = ""
    try:
        with fitz.open(ruta_pdf) as doc:
            for pagina in doc:
                texto_pdf += pagina.get_text()
        return texto_pdf.strip()
    except Exception as e:
        return f"Error al leer PDF: {str(e)}"


def generar_analisis_clinico(texto_pdf: str, nombre_documento: str) -> str:
    """
    Genera un análisis del contenido del PDF con Gemini.
    """
    prompt = f"""
Eres un experto en medicina que analiza informes clínicos.

Analiza el siguiente informe titulado **"{nombre_documento}"**. Tu tarea es:

1. Detectar diagnósticos previos mencionados.
2. Identificar síntomas relevantes.
3. Señalar tratamientos o medicamentos descritos.
4. Extraer fechas importantes del documento.
5. Generar una lista de palabras clave clínicas.
6. Redactar un resumen clínico técnico.

Texto del documento:
{texto_pdf}
""".strip()

    try:
        respuesta = modelo_gemini.generate_content(prompt)
        return respuesta.text.strip()
    except Exception as e:
        return f"Error al generar análisis con Gemini: {str(e)}"


def extraer_texto_por_id_documento(id_documento: int) -> str:
    """
    Extrae el texto de un documento usando su ID, lo analiza con Gemini y devuelve la anotación.
    """
    documento = Documento.query.get(id_documento)
    if not documento:
        return "❌ Documento no encontrado en la base de datos."

    ruta_estandarizada = documento.ruta_documento.replace("\\", "/")
    texto = extraer_texto_pdf(ruta_estandarizada)

    if texto.lower().startswith("error"):
        return texto

    analisis = generar_analisis_clinico(texto, nombre_documento=ruta_estandarizada.split("/")[-1])
    return analisis
"""