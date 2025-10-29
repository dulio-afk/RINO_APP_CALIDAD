import json
import re
from google.generativeai import GenerativeModel, configure

# Configurar Gemini (solo una vez)
configure(api_key="AIzaSyAVvi2N0McSfzmBiBryYI24gfsjgU1EpYc")
modelo_gemini = GenerativeModel("gemini-2.5-flash")

def generar_prompt_analisis(examenes: list) -> str:
    texto = ""
    for i, ex in enumerate(examenes, 1):
        sintomas = ex.sintomas or "No registrados"
        observaciones = ex.observaciones or "No registradas"
        texto += f"Examen {i}:\n- Síntomas: {sintomas}\n- Observaciones: {observaciones}\n\n"

    prompt = f"""
Eres un médico especialista en análisis de datos clínicos. Se te entregarán registros de síntomas y observaciones extraídos de varios exámenes médicos de pacientes con retinopatía diabética.

🩺 Tu tarea es:

1. Clasificar los síntomas detectados en las siguientes categorías:
   - Leves
   - Moderados
   - Graves
   - Oftalmológicos

2. Detectar relaciones o asociaciones comunes entre los síntomas (por ejemplo, "visión borrosa suele aparecer junto con dolor ocular").

3. Detectar temas frecuentes en las observaciones clínicas.

4. Devuelve tu respuesta en el siguiente formato JSON:

```json
{{
  "sintomas_clasificados": {{
    "leves": [],
    "moderados": [],
    "graves": [],
    "oftalmologicos": []
  }},
  "relaciones": [
    {{"sintomas": ["s1", "s2"], "fuerza": "alta"}}
  ],
  "temas_observaciones": []
}}

Registros clínicos a analizar:
{texto if texto else "No hay datos disponibles."}

Responde solo con el JSON.
""".strip()

    return prompt


def limpiar_respuesta_json(texto: str) -> str:
    """Extrae el JSON puro de la respuesta de Gemini."""
    match = re.search(r"```json(.*?)```", texto, re.DOTALL)
    if match:
        texto_limpio = match.group(1)
    else:
        texto_limpio = texto

    texto_limpio = re.sub(r"```+", "", texto_limpio)
    texto_limpio = re.sub(r"//.*", "", texto_limpio)
    texto_limpio = texto_limpio.strip()

    return texto_limpio


def analizar_sintomas_con_gemini(examenes: list) -> dict:
    """
    Usa Gemini para analizar síntomas y observaciones de múltiples exámenes clínicos.

    Retorna un diccionario con:
    - síntomas clasificados por nivel y tipo
    - relaciones sintomáticas
    - temas comunes en observaciones
    """
    prompt = generar_prompt_analisis(examenes)

    try:
        respuesta = modelo_gemini.generate_content(prompt)
        texto_crudo = respuesta.text.strip()
        texto_json = limpiar_respuesta_json(texto_crudo)
        resultado = json.loads(texto_json)
        return resultado

    except json.JSONDecodeError as e:
        return {
            "error": "❌ Error al interpretar JSON desde Gemini.",
            "detalle": str(e),
            "respuesta_cruda": texto_crudo
        }

    except Exception as e:
        return {
            "error": "⚠️ Error general al usar Gemini.",
            "detalle": str(e)
        }
