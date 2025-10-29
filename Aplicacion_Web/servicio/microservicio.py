# Aplicacion_Web/servicio/microservicio.py
import requests
import logging

def enviar_a_microservicio(ruta_imagen, url_microservicio):
    try:
        with open(ruta_imagen, "rb") as f:
            files = {"file": (ruta_imagen, f, "image/jpeg")}
            response = requests.post(url_microservicio, files=files)
        
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Error en microservicio: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logging.exception("Error al conectar con el microservicio")
        return None
