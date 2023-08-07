import os
from django.http import FileResponse, render, StreamingHttpResponse
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
            # Descargar el video y devolver la respuesta con el archivo descargado
            response = descargar_video(request, link, formato, calidad_video, calidad_audio)
            return response

        except PytubeError as e:
            mensaje = f"Error en la descarga: {e}"

    return render(request, 'home.html', {'mensaje': mensaje})


def video_stream(url, chunk_size=8192):
    yt = YouTube(url)
    stream = yt.streams.filter(progressive=True, file_extension='mp4').first()

    if stream:
        return stream.url
    else:
        raise PytubeError("No se encontró una fuente de video progresiva.")


def descargar_video(request, url, formato='mp4', calidad_video='highest', calidad_audio='highest'):
    try:
        video_url = video_stream(url)
        response = StreamingHttpResponse(video_stream(url), content_type='video/mp4')
        response['Content-Disposition'] = f'attachment; filename="video.mp4"'
        return response

    except PytubeError as e:
        raise PytubeError(f"Error en la descarga: {e}")