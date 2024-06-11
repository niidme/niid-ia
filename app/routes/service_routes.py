# routes/service_routes.py

import json
import logging
from fastapi import APIRouter, Path, HTTPException, Body, Depends
from models.templates import UserPrompt
from services.service_manager import AsistenteDeServicioAsync
from services.data_extractor import ExtractorDeInformacionAsync
from fastapi.responses import JSONResponse
import asyncio

service_router = APIRouter()

service_instances = {}

def get_service_assistant(service: str, service_type: str) -> AsistenteDeServicioAsync:
    key = f"{service}_{service_type}"
    if key in service_instances:
        return service_instances[key]
    else:
        assistant = AsistenteDeServicioAsync(service=service, service_type=service_type)
        service_instances[key] = assistant
        return assistant

@service_router.post("/api/v1/request-service/{service}/{service_type}", tags=["✨ AI Service Requests"])
async def handle_service_request(service: str = Path(..., description="Categoría del servicio requerido"), service_type: str = Path(..., description="Tipo de servicio requerido"), user_prompt: UserPrompt = Body(...), asistente: AsistenteDeServicioAsync = Depends(get_service_assistant)):
    """
    🛎️ **Endpoint de Solicitud de Servicio**
    
    Este endpoint permite a los usuarios solicitar diferentes tipos de servicios clasificados por categoría y tipo. Utiliza un modelo de lenguaje entrenado y directrices específicas para proporcionar respuestas personalizadas y eficaces.
    
    ### Parámetros:
    - **service**: La categoría del servicio que el usuario desea solicitar. Ejemplos: 'travel', 'catering'.
    - **service_type**: El tipo de servicio dentro de la categoría, puede ser 'profesional' o 'personal'.
    - **user_prompt**: Un objeto que contiene el ID del usuario y su entrada de texto, representando la solicitud de servicio.
    
    ### Respuesta:
    - **response**: Un objeto JSON con la respuesta generada por el asistente de servicio, adaptada al tipo y categoría de solicitud.
    """
    max_retries = 3  # Número máximo de intentos
    retry_delay = 2  # Segundos de espera entre intentos

    for attempt in range(max_retries):
        try:
            respuesta_obj = await asistente.enviar_peticion(user_prompt.user_id, user_prompt.user_input)
            logging.info(f"Respuesta recibida: {respuesta_obj}")
            if 'error' in respuesta_obj:
                raise Exception(respuesta_obj['error'])
            return JSONResponse(content=respuesta_obj)  # Retorna la respuesta si tiene éxito
        except json.JSONDecodeError as e:
            logging.error(f'Error de decodificación JSON en intento {attempt + 1}: {str(e)}')
            if attempt < max_retries - 1:  # Verifica si no es el último intento
                await asyncio.sleep(retry_delay)  # Espera antes del próximo intento
            else:
                raise HTTPException(status_code=500, detail=f'Error de decodificación JSON: {str(e)}')
        except Exception as e:
            logging.error(f'Intento {attempt + 1} fallido: {str(e)}')
            if attempt < max_retries - 1:  # Verifica si no es el último intento
                await asyncio.sleep(retry_delay)  # Espera antes del próximo intento
            else:
                raise HTTPException(status_code=500, detail=str(e))  # Lanza error después del último intento
