# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.service_routes import service_router
from routes.home_routes import home_router
from routes.utility_routes import utility_router
import logging
from dotenv import load_dotenv
import os

load_dotenv()

API_VERSION = os.getenv("API_VERSION")

# Configura el nivel de registro
logging.basicConfig(level=logging.INFO)

# Crea un objeto logger para tu aplicación
logger = logging.getLogger("niid_ai")

app = FastAPI(
    title="Niid AI",
    description=f"""
   Niid AI es una plataforma avanzada que impulsa interacciones inteligentes y personalizadas, diseñada para enriquecer la experiencia del usuario en diversas aplicaciones y servicios. Utilizando tecnologías de inteligencia artificial de vanguardia, Niid AI ofrece una suite integral de herramientas y servicios que facilitan desde la transcripción de audio y el análisis de texto hasta la gestión de solicitudes de servicio personalizadas.
   Versión actual: {API_VERSION} - Estamos trabajando arduamente para incorporar nuevas características y mejorar la plataforma. ¡Tu feedback es bienvenido!
    """,
    version=API_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(home_router)
app.include_router(service_router)
app.include_router(utility_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)