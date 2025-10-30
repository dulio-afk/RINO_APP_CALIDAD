
# from google.generativeai import GenerativeModel, configure

# Configura Gemini solo una vez
configure(api_key="AIzaSyAVvi2N0McSfzmBiBryYI24gfsjgU1EpYc")
modelo_gemini = GenerativeModel("gemini-2.5-flash")

def generar_prompt(datos_paciente: dict, informes_pdf: list) -> str:
    texto_informes = "\n\n".join(
        [f"Informe '{inf['nombre']}':\n{inf['contenido']}" for inf in informes_pdf]
    )

    prompt = f"""
Eres un médico oftalmólogo con experiencia en diagnóstico y tratamiento de la retinopatía diabética. Tu tarea es analizar cuidadosamente la siguiente información clínica y redactar una **recomendación profesional, empática y personalizada para el paciente**.

🧑 Datos del paciente:
- Nombre completo: {datos_paciente.get('nombre', '')} {datos_paciente.get('apellido_paterno', '')} {datos_paciente.get('apellido_materno', '')}
- Edad: {datos_paciente.get('edad', '')} años
- Sexo: {datos_paciente.get('sexo', '')}

🩺 Parámetros clínicos más recientes:
- Nivel de glucosa en sangre: {datos_paciente.get('glucosa', 'No disponible')}
- Presión arterial: {datos_paciente.get('presion', 'No disponible')}
- Síntomas reportados: {datos_paciente.get('sintomas', 'No registrados')}
- Observaciones médicas: {datos_paciente.get('observaciones_examen', 'No registradas')}

🔬 Diagnóstico por IA:
- Grado de retinopatía diabética: {datos_paciente.get('grado_retinopatia', '')}
- Confianza del modelo: {datos_paciente.get('confianza', 0)}%
- Fecha del diagnóstico: {datos_paciente.get('fecha_diagnostico', 'No disponible')}

📄 Informes clínicos adicionales extraídos de documentos PDF:
{texto_informes if texto_informes else "No se encontraron documentos adicionales."}

🔎 Tareas que debes realizar:
1. Explica brevemente al paciente en qué consiste el diagnóstico encontrado.
2. Ofrece recomendaciones claras y específicas sobre:
   - Visitas al oftalmólogo o retinólogo.
   - Controles de glucosa y presión arterial.
   - Cambios en el estilo de vida.
   - Cualquier medida preventiva para evitar el avance de la retinopatía.
3. Si se detecta un grado avanzado o síntomas graves, **recomienda acudir a un especialista con urgencia**.
4. Usa un lenguaje comprensible para un paciente, evita términos técnicos sin explicación.

Sé claro, directo, pero también empático. Este mensaje será mostrado al paciente como orientación inicial.

Gracias.
""".strip()

    return prompt


def generar_recomendacion(datos_paciente: dict, informes_pdf: list) -> str:
    """
    Llama a Gemini para generar una recomendación médica personalizada.

    Parámetros:
        datos_paciente (dict): Datos clínicos del paciente.
        informes_pdf (list): Lista de informes PDF extraídos.

    Retorna:
        str: Recomendación generada por Gemini.
    """
    prompt = generar_prompt(datos_paciente, informes_pdf)
    try:
        respuesta = modelo_gemini.generate_content(prompt)
        return respuesta.text.strip()
    except Exception as e:
        return f"⚠️ Error al generar recomendación: {str(e)}"
