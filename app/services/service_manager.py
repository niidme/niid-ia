# services/service_manager.py

import aiohttp
import asyncio
from datetime import datetime
import logging
import json
from dotenv import load_dotenv
import os

load_dotenv()

from models.roles import SYSTEM_ROLES  # Importar roles del sistema

# Variables configurables hardcodeadas //TODO: Cambiar a variables de entorno
API_KEY = 'e495c745c0e8440684691813da4fd312'
API_BASE = 'https://niid-ai-east-us.openai.azure.com'
API_VERSION = '2024-04-01-preview'
DEPLOYMENT_NAME = 'niid-gpt-4o'

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
        # Obtener la fecha actual y formatearla estilo Wednesday, 24th of June 2024
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
                },
                {
                    'role': 'system',
                    'content': f"IMPORTANTE: El usuario ha indicado que el tipo de servicio es: {self.service_type}"
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
            'messages': messages,
            'temperature': 0.2,  # Temperatura de muestreo de 0.0 a 1.0
            'max_tokens': 1000,  # Ajustar la cantidad de tokens si es necesario
            'response_format': { "type": "json_object" }  # Especificar el formato de respuesta JSON
        }
        url = MODEL_URL

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, headers=self.headers, json=body, timeout=120) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        #logging.info(f'Respuesta de la API: {response_data}')
                        
                        # Directamente usar el contenido de la respuesta como JSON
                        message_content = response_data['choices'][0]['message']['content']
                        structured_response = json.loads(message_content)
                        
                        await self.agregar_mensaje(user_id, {
                            'role': 'assistant',
                            'content': structured_response.get("assistant_response")
                        })
                        
                        return structured_response  # Devolver el JSON estructurado
                    else:
                        error_text = await response.text()
                        logging.error(f'Error en la respuesta de la API: {response.status} - {error_text}')
                        return {'error': f'Error: {response.status} - {error_text}'}
            except asyncio.TimeoutError:
                logging.error('La petición ha superado el tiempo máximo de espera.')
                return {'error': 'La petición ha superado el tiempo máximo de espera.'}
            except Exception as e:
                logging.error(f'Error inesperado: {str(e)}')
                return {'error': f'Error inesperado: {str(e)}'}
