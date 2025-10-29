from fastapi import FastAPI, File, UploadFile, HTTPException 
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from PIL import Image, UnidentifiedImageError
import torch
import io
import logging

from util.preprocessing import preprocess_image
from torchvision import models

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ajusta en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar logging
logging.basicConfig(level=logging.INFO)

# Diccionario para traducir clase a nombre
GRADOS_RETINOPATIA = {
    0: "No DR",
    1: "Leve",
    2: "Moderada",
    3: "Severa",
    4: "Proliferativa"
}

def load_model(path="model/best_model.pth"):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = models.resnet50(pretrained=False)
    model.fc = torch.nn.Linear(model.fc.in_features, 5)  # 5 clases
    model.load_state_dict(torch.load(path, map_location=device))
    model.to(device)
    model.eval()
    logging.info(f"Modelo cargado en {device}")
    return model, device

model, device = load_model()

@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Formato de imagen inválido")

    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="No se pudo leer la imagen")

    try:
        input_tensor = preprocess_image(image).unsqueeze(0).to(device)
        with torch.no_grad():
            outputs = model(input_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            pred_class = torch.argmax(probabilities, dim=1).item()
            confidence = probabilities[0][pred_class].item()
            grado = GRADOS_RETINOPATIA[pred_class]
    except Exception as e:
        logging.error(f"Error en predicción: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "clase_predicha": pred_class,
        "grado_retinopatia": grado,
        "confianza": round(confidence, 4)
    }
