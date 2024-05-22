import os
import aiohttp
import asyncio
from datetime import datetime
from dotenv import load_dotenv

from models.roles import SYSTEM_ROLES  # Importar roles del sistema

# Cargar variables de entorno
load_dotenv()

# Variables configurables
API_KEY = os.getenv('AZURE_API_KEY_FRANCE')
API_BASE = os.getenv('AZURE_ENDPOINT_FRANCE')
API_VERSION = os.getenv('AZURE_API_VERSION_FRANCE')
DEPLOYMENT_NAME = os.getenv('AZURE_AI_MODEL_FRANCE')

MODEL_URL = f'{API_BASE}/openai/deployments/{DEPLOYMENT_NAME}/chat/completions?api-version={API_VERSION}'

class AsistenteDeServicioAsync:
    def __init__(self, service, service_type):
        if service_type not in ['profesional', 'personal']:
            raise ValueError("service_type debe ser 'profesional' o 'personal'")
        self.service_type = service_type

        self.headers = {
            'api-key': API_KEY,
            'Content-Type': 'application/json'
        }
        self.conversaciones = {}  # Diccionario para mantener las conversaciones
        self.system_role = SYSTEM_ROLES.get(service)
        if not self.system_role:
            raise ValueError(f"Servicio '{service}' no soportado")

    async def agregar_mensaje(self, user_id, mensaje):
        if user_id not in self.conversaciones:
            self.conversaciones[user_id] = []
        self.conversaciones[user_id].append(mensaje)

    async def crear_mensajes(self, user_id, user_input):
        # Obtener la fecha actual y formatearla estilo wednesday, 24th of June 2024
        fecha_actual = datetime.now().strftime('%A, %dth of %B %Y')
        if user_id not in self.conversaciones:
            self.conversaciones[user_id] = [
                {
                    'role': 'system',
                    'content': self.system_role
                },
                {
                    'role': 'system',
                    'content': f"Fecha actual: {fecha_actual}"  # Mensaje de sistema con la fecha
                }
            ]
        await self.agregar_mensaje(user_id, {
            'role': 'user',
            'content': user_input
        })
        return self.conversaciones[user_id]

    async def enviar_peticion(self, user_id, user_input):
        messages = await self.crear_mensajes(user_id, user_input)
        body = {
            'response_format': {'type': 'json_object'},
            'messages': messages,
            'temperature': 0.2,
        }
        url = MODEL_URL

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, headers=self.headers, json=body, timeout=120) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        message_content = response_data['choices'][0]['message']['content']
                        await self.agregar_mensaje(user_id, {
                            'role': 'assistant',
                            'content': message_content
                        })
                        print(message_content)
                        return message_content
                    else:
                        return f'Error: {response.status} - {await response.text()}'
            except asyncio.TimeoutError:
                return 'La petición ha superado el tiempo máximo de espera.'
