import requests
from pytube import YouTube
from pytube.exceptions import PytubeError
import logging
from django.shortcuts import render, HttpResponse
from .tasks import download_video_audio
from pytube.exceptions import PytubeError

def home(request):
    mensaje = ""
    if request.method == 'POST':
        link = request.POST.get('link', '')
        formato = request.POST.get('formato', 'mp4')
        calidad_video = request.POST.get('calidad_video', 'highest')
        calidad_audio = request.POST.get('calidad_audio', 'highest')

        try:
            # Llama a la tarea de Celery para la descarga de video/audio de forma asíncrona
            archivo, extension = download_video_audio.delay(link, formato, calidad_video, calidad_audio).get()

            # Crea una respuesta para la descarga
            response = HttpResponse(archivo, content_type=f"video/{extension}")
            response['Content-Disposition'] = f'attachment; filename="video.{extension}"'
            mensaje = f"Descarga completada!"
            return response
        except PytubeError as e:
            mensaje = f"Error en la descarga: {e}"

    return render(request, 'home.html', {'mensaje': mensaje})

def descargar_video_audio(url, formato='mp4', calidad_video='highest', calidad_audio='highest'):
    try:
        # Crea una instancia de la clase YouTube
        yt = YouTube(url)

        # Obtiene el flujo de video o audio según el formato seleccionado
        if formato == 'mp4':
            streams = yt.streams.filter(file_extension='mp4')
            print(streams)  # Print available mp4 streams for debugging
            stream = streams.filter(res=calidad_video).first()
        elif formato == 'mp3':
            streams = yt.streams.filter(only_audio=True)
            print(streams)  # Print available audio streams for debugging
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
        logging.error(f"Error during video download: {e}")
        raise PytubeError(f"Ocurrió un error durante la descarga del video: {e}")