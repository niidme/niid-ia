# routes/utility_routes.py

from fastapi import APIRouter, Body, HTTPException
from fastapi import UploadFile, File, status
from fastapi.responses import JSONResponse

import logging

from services.speech2txt import AudioTranscription
from routes.service_routes import service_instances
from routes.service_routes import get_service_assistant
from services.data_extractor import ExtractorDeInformacionAsync

# Crea un objeto logger para este archivo de rutas
logger = logging.getLogger("niid_ai")

utility_router = APIRouter()

# Endpoint para transcripción de audio
@utility_router.post("/api/v1/audio-transcription", 
                                tags=["🔮 AI Tools & Utilities"],
                                response_description="Transcribe con éxito el archivo de audio y retorna la transcripción en formato texto.",
                                response_model=dict)
async def transcribe_endpoint(
        file: UploadFile = File(..., description="Archivo de audio a transcribir. Debe estar en uno de los formatos soportados: mp3, wav, flac, m4a, etc."), 
        session_id: str = Body(..., description="ID único para la sesión, utilizado para tracking y logueo.")
    ):
    """
    🎤 **Endpoint de Transcripción de Audio**

    Este endpoint facilita la transcripción de archivos de audio a texto, permitiendo así una fácil conversión de contenido hablado a escrito. Además, el archivo de audio original se convierte a formato MP3 y se registra con un timestamp y el ID de la sesión para futuras referencias.

    ### Parámetros
    - **file**: El archivo de audio que deseas transcribir. Asegúrate de que esté en un formato soportado.
    - **session_id**: Un identificador único para esta sesión de transcripción, ayudando en el seguimiento y registro de la operación.

    ### Respuesta
    - **transcription**: El texto resultante de la transcripción del archivo de audio.

    ### Ejemplo
    ```json
    {
      "file": "(binary file data)",
      "session_id": "12345-abcde-67890-fghij"
    }
    ```

    Utiliza este endpoint para transformar contenido de audio en texto de forma eficiente y rápida.
    """
    try:
        # Agrega mensajes de registro
        logger.info(f"Transcribiendo audio para la sesión {session_id}...")
        
        text_response = await AudioTranscription(file)
        raw_text = text_response['transcription']
        
        # Agrega mensajes de registro
        logger.info(f"Transcripción completada para la sesión {session_id} - Texto: {raw_text}")

        return JSONResponse(status_code=status.HTTP_200_OK, content={"transcription": raw_text})
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    


@utility_router.get("/api/v1/get-conversation/{service}/{service_type}/{user_id}", tags=["🔮 AI Tools & Utilities"])
async def get_conversation(service: str, service_type: str, user_id: str):
    """
    Endpoint para obtener la conversación completa para un usuario, servicio y tipo de servicio específicos.

    ### Parámetros:
    - **service**: El servicio asociado a la conversación.
    - **service_type**: El tipo de servicio asociado a la conversación.
    - **user_id**: El ID único del usuario cuya conversación se desea recuperar.

    ### Respuesta:
    Una lista que contiene todos los mensajes intercambiados en la conversación.
    """
    key = f"{service}_{service_type}"  # Construir la clave de la misma manera que en service_routes.py
    assistant = service_instances.get(key)
    if assistant is None:
        raise HTTPException(status_code=404, detail=f"Asistente para el servicio '{service}' y tipo '{service_type}' no encontrado")

    conversation = assistant.conversaciones.get(user_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail=f"Conversación para el usuario '{user_id}' no encontrada")

    # Filtrar y excluir mensajes donde el role es 'system'
    filtered_conversation = [message for message in conversation if message['role'] != 'system']

    return filtered_conversation



@utility_router.post("/api/v1/extract-information", 
                     tags=["🔮 AI Tools & Utilities"],
                     response_description="Extrae información estructurada de la conversación del usuario y la devuelve en formato JSON.")
async def extract_information_endpoint(
        service: str = Body(..., description="El servicio asociado a la conversación."),
        service_type: str = Body(..., description="Tipo de servicio que determinará el contexto de la extracción de información."),
        user_id: str = Body(..., description="ID único del usuario cuya conversación se utilizará para la extracción de información.")
    ):
    """
    💡 **Endpoint de Extracción de Información**

    Este endpoint procesa la conversación completa de un usuario, excluyendo los mensajes del sistema, utilizando un modelo de IA configurado para devolver información estructurada en formato JSON, basado en el tipo de servicio especificado.
    """
    try:
        # Utilizamos get_service_assistant para obtener la instancia del asistente
        assistant = get_service_assistant(service, service_type)
        # SI SERVICIO NO SE HA ESPECIFICADO POR DEFECTO profesional
        if assistant is None:
            assistant = get_service_assistant("profesional", service_type)
        # Verificar si existe una conversación para el usuario
        conversation = assistant.conversaciones.get(user_id)
        if conversation is None:
            raise HTTPException(status_code=404, detail=f"Conversación para el usuario '{user_id}' no encontrada")

        # Filtrar y excluir mensajes donde el rol es 'system'
        filtered_conversation = " ".join([message['content'] for message in conversation if message['role'] != 'system'])

        # Log de inicio de extracción
        logger.info(f"Extrayendo información para el servicio {service}, tipo {service_type} y el usuario {user_id}...")

        # Inicialización y uso del extractor de información
        extractor = ExtractorDeInformacionAsync(service)
        # añadir service_type al texto
        filtered_conversation = f"{service_type} {filtered_conversation}"
        extracted_information = await extractor.obtener_informacion(filtered_conversation)
        # Log de información extraída
        logger.info(f"Información extraída para el servicio {service}, tipo {service_type} y el usuario {user_id} - Información: {extracted_information}")

        return JSONResponse(status_code=200, content={"data": extracted_information})
    
    except Exception as e:
        # Log de error
        logger.error(f"Error al extraer información: {e}")
        raise HTTPException(status_code=500, detail=str(e))