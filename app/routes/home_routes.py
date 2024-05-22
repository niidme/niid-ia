# routes/home_routes.py

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import os
import logging

from dotenv import load_dotenv
load_dotenv()

API_VERSION = os.getenv("API_VERSION")

logger = logging.getLogger("niid_ai")

home_router = APIRouter()

# Endpoint para registrar los clics en los botones
@home_router.get("/log-click", include_in_schema=False)
def log_click(button_id: str):
    logger.info(f"Click registrado en el botón: {button_id}")
    return {"message": "Click registrado"}

# Home route para mostrar HTML de bienvenida
@home_router.get("/", include_in_schema=False, response_class=HTMLResponse)
def main():
    logger.info("Mostrando HTML de bienvenida")
    return """
    <html>
        <head>
            <title>Niid AI - API Home</title>
            <link rel="icon" type="image/png" href="https://niid.me/wp-content/uploads/2023/02/favicon-150x150.png"/>
            <style>
                body {
                    font-family: "Open Sans", sans-serif;
                    background-color: #151A43;
                    color: #BDBDBD;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                }

                .container {
                    text-align: center;
                    max-width: 800px;
                    padding: 20px;
                }

                img {
                    width: 200px;
                    margin-bottom: 20px;
                }

                .button {
                    background-color: #EB358A;
                    border: none;
                    color: white;
                    padding: 15px 32px;
                    text-align: center;
                    text-decoration: none;
                    display: inline-block;
                    font-size: 16px;
                    margin: 10px;
                    cursor: pointer;
                    border-radius: 5px;
                    transition: background-color 0.3s ease;
                }

                .button:hover {
                    background-color: #72CDDD;
                }

                a {
                    text-decoration: none;
                }

                .description {
                    color: #BDBDBD;
                    font-size: 20px;
                    margin-top: 20px;
                    line-height: 1.4em;
                    padding: 0 30px;
                    width: 100%;
                }

                .description p {
                    margin-bottom: 1.5em;
                }

                b {
                    font-size: 12px;
                    margin-top: 20px;
                    display: block;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <img src="https://niid.me/wp-content/uploads/elementor/thumbs/logo-niid-q2mpkm3ba5uk130ssbjpucvf8q2znbd8f14lkqkef4.png" alt="Niid AI Logo">
                <div class="description">
                    <p>Niid AI es una API avanzada diseñada para enriquecer la experiencia del usuario.</p>
                </div>
                <script>
                function logButtonClick(event) {
                    const buttonId = event.target.id;
                    fetch(`/log-click?button_id=${buttonId}`)
                        .then(response => console.log('Click logged'))
                        .catch(error => console.error('Error logging click:', error));
                }
                </script>
                <a href="/docs"><button id="docsButton" class="button" onClick="logButtonClick(event)">Documentación API</button></a>
                <a href="/redoc"><button id="redocButton" class="button" onClick="logButtonClick(event)">ReDoc</button></a>
                <a href="https://niid.test.macaqueconsulting.com/" target="_blank"><button id="testButton" class="button" onClick="logButtonClick(event)">Zona de Pruebas</button></a>
                <b>Versión actual: """ + API_VERSION + """</b>
            </div>
        </body>
    </html>
    """
