import io, logging, requests
from django.http import StreamingHttpResponse
from django.shortcuts import render
from pytube import YouTube, Stream
from pytube.exceptions import PytubeError

def home(request):
    mensaje = ""
    if request.method == 'POST':
        link = request.POST.get('link', '')
        formato = request.POST.get('formato', 'mp4')
        calidad_video = request.POST.get('calidad_video', 'highest')
        calidad_audio = request.POST.get('calidad_audio', 'highest')

        try:
            # Descargar el contenido del video/audio
            archivo, extension = descargar_video_audio(link, formato, calidad_video, calidad_audio)

            # Crear una respuesta HTTP para la descarga
            response = StreamingHttpResponse(archivo, content_type=f"video/{extension}")
            response['Content-Disposition'] = f'attachment; filename="video.{extension}"'
            mensaje = f"Descarga completada!"
            return response
        except PytubeError as e:
            mensaje = f"Error en la descarga: {e}"

    return render(request, 'home.html', {'mensaje': mensaje})

def descargar_video_audio(url, formato='mp4', calidad_video='highest', calidad_audio='highest' ):
    try:
        # Crea una instancia de la clase YouTube
        yt = YouTube(url)

        # Obtiene el flujo de video o audio según el formato seleccionado
        if formato == 'mp4':
            stream = get_best_video_stream(yt.streams, calidad_video)
        elif formato == 'mp3':
            stream = get_best_audio_stream(yt.streams, calidad_audio)
        else:
            raise ValueError("Formato no válido. Debe ser 'mp4' o 'mp3'.")

        if stream:
            response = get_stream_response(stream)
            archivo = response.iter_content(chunk_size=4096)

            return archivo, stream.subtype
        else:
            raise PytubeError("No se encontró la calidad especificada.")
    except Exception as e:
        logging.error(f"Error durante la descarga del video: {e}")
        raise PytubeError(f"Ocurrió un error durante la descarga del video: {e}")

def get_stream_response(stream: Stream):
    # Obtener el contenido del flujo de video o audio
    response = requests.get(stream.url, stream=True)
    return response


def get_best_video_stream(streams: Stream, calidad: str) -> Stream:
    # Filtra los flujos de video disponibles por calidad
    if calidad == 'highest':
        return streams.filter(type='video', progressive=True).first()
    elif calidad == '720p':
        return streams.filter(res='720p', type='video', progressive=True).first()
    elif calidad == '360p':
        return streams.filter(res='360p', type='video', progressive=True).first()
    else:
        raise PytubeError(f"Calidad de video no válida: {calidad}")

def get_best_audio_stream(streams: Stream, calidad: str) -> Stream:
    # Filtra los flujos de audio disponibles por calidad
    if calidad == 'highest':
        return streams.filter(type='audio', progressive=False).first()
    elif calidad == '160kbps':
        return streams.filter(abr='160kbps', type='audio', progressive=False).first()
    elif calidad == '128kbps':
        return streams.filter(abr='128kbps', type='audio', progressive=False).first()
    else:
        raise PytubeError(f"Calidad de audio no válida: {calidad}")