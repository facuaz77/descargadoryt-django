from django.shortcuts import render,HttpResponseRedirect
import requests
from pytube import YouTube
from pytube.exceptions import PytubeError


def home(request):
    mensaje = ""
    if request.method == 'POST':
        link = request.POST.get('link', '')
        formato = request.POST.get('formato', 'mp4')
        calidad_video = request.POST.get('calidad_video', 'highest')
        calidad_audio = request.POST.get('calidad_audio', 'highest')

        try:
            # Redirigir al usuario a la URL del archivo descargado
            return descargar_video_audio(request, link, formato, calidad_video, calidad_audio)

        except PytubeError as e:
            mensaje = f"Error en la descarga: {e}"

    return render(request, 'home.html', {'mensaje': mensaje})



def descargar_video_audio(request, url, formato='mp4', calidad_video='highest', calidad_audio='highest'):
    try:
        # Crea una instancia de la clase YouTube
        yt = YouTube(url)

        # Obtiene el flujo de video o audio según el formato seleccionado
        if formato == 'mp4':
            stream = yt.streams.filter(file_extension='mp4', res=calidad_video).first()
        elif formato == 'mp3':
            stream = yt.streams.filter(only_audio=True, abr=calidad_audio).first()
        else:
            raise ValueError("Formato no válido. Debe ser 'mp4' o 'mp3'.")

        if stream:
            response = requests.get(stream.url)
            archivo = response.content
            extension = formato

            # Devuelve una redirección al archivo descargado
            return HttpResponseRedirect(stream.url)

        else:
            raise PytubeError("No se encontró la calidad especificada.")

    except Exception as e:
        raise PytubeError(f"Ocurrió un error: {e}")

