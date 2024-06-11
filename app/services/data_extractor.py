import aiohttp
import json
from datetime import datetime

# Importa o define los roles del sistema para cada servicio
from models.roles import (
    EXTRACTOR_SYSTEM_ROLE_TRAVEL,
    EXTRACTOR_SYSTEM_ROLE_CATERING,
    EXTRACTOR_SYSTEM_ROLE_RESTAURANT,
    EXTRACTOR_SYSTEM_ROLE_EVENTS
)

# Variables configurables hardcodeadas // TODO: Cambiar a variables de entorno
API_KEY = 'e495c745c0e8440684691813da4fd312'
API_BASE = 'https://niid-ai-east-us.openai.azure.com'
API_VERSION = '2024-04-01-preview'
DEPLOYMENT_NAME = 'niid-gpt-4o'
TEMPERATURE_MODEL = '0.2'

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

    async def obtener_informacion(self, texto, travel_type):
        # Obtener la fecha actual en el formato requerido por el modelo
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        # Construir el cuerpo de la petición, incluyendo la instrucción para generar JSON
        body = {
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
            ],
            'temperature': 0.2,
            'max_tokens': 1000,
            'response_format': { "type": "json_object" }  # Especificar el formato de respuesta JSON
        }

        # Construir la URL para la petición
        url = f"{self.api_base}/openai/deployments/{self.deployment_name}/chat/completions?api-version={self.api_version}"

        # Realizar la petición asincrónica
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.headers, json=body) as response:
                if response.status == 200:
                    data = await response.json()
                    # Imprimir la respuesta completa para depuración
                    try:
                        # Directamente parsear el contenido como JSON
                        content = data['choices'][0]['message']['content']
                        response_data = json.loads(content)
                        # Asegurar que el travel_type es el especificado en la llamada de extracción
                        response_data['travel_type'] = travel_type
                        return response_data
                    except json.JSONDecodeError as e:
                        return {'error': f'Error de decodificación JSON: {e}', 'response_content': data['choices'][0]['message']['content']}
                else:
                    error_text = await response.text()
                    # Imprimir el texto de error para depuración
                    return {'error': f'Error en la petición: {response.status}', 'response_text': error_text}
