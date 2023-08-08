from celery import Celery
import requests
from pytube import YouTube
from pytube.exceptions import PytubeError

# Crea una instancia de Celery
app = Celery('tasks', broker='redis://localhost:6379/0')

@app.task
def download_video_audio(url, formato='mp4', calidad_video='highest', calidad_audio='highest'):
    try:
        # Crea una instancia de la clase YouTube
        yt = YouTube(url)

        # Obtiene el flujo de video o audio según el formato seleccionado
        if formato == 'mp4':
            streams = yt.streams.filter(file_extension='mp4')
            stream = streams.filter(res=calidad_video).first()
        elif formato == 'mp3':
            streams = yt.streams.filter(only_audio=True)
            stream = streams.filter(abr=calidad_audio).first()
        else:
            raise ValueError("Formato no válido. Debe ser 'mp4' o 'mp3'.")

        if stream:
            response = requests.get(stream.url)
            archivo = response.content
            extension = formato

            return archivo, extension
        else:
            raise PytubeError("No se encontró la calidad especificada.")
    except Exception as e:
        raise PytubeError(f"Ocurrió un error durante la descarga del video: {e}")