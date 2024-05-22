# services/data_extractor.py

import os
import aiohttp
import json
from datetime import datetime
from dotenv import load_dotenv

# Importa o define los roles del sistema para cada servicio
from models.roles import (
    EXTRACTOR_SYSTEM_ROLE_TRAVEL,
    EXTRACTOR_SYSTEM_ROLE_CATERING,
    EXTRACTOR_SYSTEM_ROLE_RESTAURANT,
    EXTRACTOR_SYSTEM_ROLE_EVENTS
)

# Cargar variables de entorno
load_dotenv()

# Variables configurables
API_KEY = os.getenv('AZURE_API_KEY_FRANCE')
API_BASE = os.getenv('AZURE_ENDPOINT_FRANCE')
API_VERSION = os.getenv('AZURE_API_VERSION_FRANCE')
DEPLOYMENT_NAME = os.getenv('AZURE_AI_MODEL_FRANCE')
TEMPERATURE_MODEL = os.getenv('TEMPERATURE_MODEL')

class ExtractorDeInformacionAsync:
    def __init__(self, service):
        self.api_key = API_KEY
        self.api_base = API_BASE
        self.api_version = API_VERSION
        self.deployment_name = DEPLOYMENT_NAME

        # Configurar los headers para la petición HTTP
        self.headers = {
            'api-key': self.api_key,
            'Content-Type': 'application/json'
        }

        # Seleccionar el contenido del rol del sistema basado en el servicio
        system_roles = {
            'travel': EXTRACTOR_SYSTEM_ROLE_TRAVEL,
            'catering': EXTRACTOR_SYSTEM_ROLE_CATERING,
            'restaurant': EXTRACTOR_SYSTEM_ROLE_RESTAURANT,
            'events': EXTRACTOR_SYSTEM_ROLE_EVENTS
        }
        self.system_role_content = system_roles.get(service)
        if not self.system_role_content:
            raise ValueError(f"Servicio '{service}' no soportado")

    async def obtener_informacion(self, texto):
        # Obtener la fecha actual en el formato requerido por el modelo
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        # Construir el cuerpo de la petición, incluyendo la instrucción para generar JSON
        body = {
            'response_format': {'type': 'json_object'},
            'messages': [
                {
                    'role': 'system',
                    'content': self.system_role_content
                },
                {
                    'role': 'system',
                    'content': f"Fecha actual: {fecha_actual}"
                },
                {
                    'role': 'user',
                    'content': texto
                }
            ]
        }

        # Construir la URL para la petición
        url = f"{self.api_base}/openai/deployments/{self.deployment_name}/chat/completions?api-version={self.api_version}"

        # Realizar la petición asincrónica
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.headers, json=body) as response:
                if response.status == 200:
                    data = await response.json()
                    return json.loads(data['choices'][0]['message']['content'])
                else:
                    return {'error': f'Error en la petición: {response.status}'}
