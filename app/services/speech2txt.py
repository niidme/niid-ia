# services/speech2txt.py

import asyncio
from fastapi import HTTPException, UploadFile
import httpx
from pydub import AudioSegment
import io
from dotenv import load_dotenv
import os

load_dotenv()

# Importar las variables de configuración del modelo
AZURE_API_KEY_EUROPE = os.getenv("AZURE_API_KEY_EUROPE")
AZURE_ENDPOINT_EUROPE = os.getenv("AZURE_ENDPOINT_EUROPE")
AZURE_SPEECH2TXT_MODEL_EUROPE = os.getenv("AZURE_SPEECH2TXT_MODEL_EUROPE")
AZURE_API_VERSION_EUROPE = os.getenv("AZURE_API_VERSION_EUROPE")


async def AudioTranscription(file: UploadFile):
    # Número de intentos antes de fallar
    max_retries = 3

    # Leer el archivo de audio y convertirlo en bytes
    audio_bytes = await file.read()

    # Calcular la duración del audio en segundos (opcional, dependiendo de si necesitas esta información)
    audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
    duracion_en_segundos = len(audio) / 1000

    # Preparar los encabezados para la API de OpenAI
    headers = {
        'api-key': AZURE_API_KEY_EUROPE,
    }

    # Preparar los datos para la carga multipart
    files = {
        "file": ("audio", audio_bytes, file.content_type),
    }

    # URL completa incluyendo el nombre del despliegue y la versión de la API
    api_url = f"{AZURE_ENDPOINT_EUROPE}/openai/deployments/{AZURE_SPEECH2TXT_MODEL_EUROPE}/audio/transcriptions?api-version={AZURE_API_VERSION_EUROPE}

    # Crear un cliente HTTP asíncrono
    client = httpx.AsyncClient(timeout=500)

    for attempt in range(max_retries + 1):
        try:
            # Realizar la llamada a la API de OpenAI
            response = await client.post(api_url, headers=headers, files=files)

            # Comprobar si la solicitud fue exitosa
            if response.status_code == 200:
                data = response.json()
                print(data)
                return {"transcription": data['text'], "audio_duration_seconds": duracion_en_segundos}

            # Si no fue exitosa y hemos alcanzado el máximo número de intentos, lanzamos una excepción
            elif attempt == max_retries:
                raise HTTPException(status_code=response.status_code, detail=f"OpenAI API error: {response.text}")

            # Si no fue exitosa pero aún podemos volver a intentarlo, esperamos un poco antes de intentarlo de nuevo
            else:
                await asyncio.sleep(1)  # Esperar 1 segundo antes de volver a intentarlo

        except Exception as e:
            if attempt == max_retries:
                raise HTTPException(status_code=500, detail=str(e))
            else:
                await asyncio.sleep(1)

    await client.aclose()  # Cerrar el cliente
