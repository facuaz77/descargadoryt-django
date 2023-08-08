from django.shortcuts import render, HttpResponse
import requests
from pytube import YouTube
from pytube.exceptions import PytubeError
import os
import shutil





def home(request):
    mensaje = ""
    if request.method == 'POST':
        link = request.POST.get('link', '')
        formato = request.POST.get('formato', 'mp4')
        calidad_video = request.POST.get('calidad_video', 'highest')
        calidad_audio = request.POST.get('calidad_audio', 'highest')

        try:
            # Descargar el contenido del video/audio
            archivo = descargar_video_audio(link, formato, calidad_video, calidad_audio)

            # Crear una respuesta HTTP para la descarga
            with open(archivo, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/octet-stream')
                response['Content-Disposition'] = f'attachment; filename="{archivo.split("/")[-1]}"'
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
            stream = yt.streams.filter(file_extension='mp4', res=calidad_video).first()
        elif formato == 'mp3':
            stream = yt.streams.filter(only_audio=True, abr=calidad_audio).first()
        else:
            raise ValueError("Formato no válido. Debe ser 'mp4' o 'mp3'.")

        if stream:
            archivo = stream.download()

            # Cambiar la extensión del archivo a .mp3 si es un audio
            if formato == 'mp3':
                nuevo_nombre = os.path.splitext(archivo)[0] + '.mp3'
                shutil.move(archivo, nuevo_nombre)
                archivo = nuevo_nombre

            return archivo
        else:
            raise PytubeError("No se encontró la calidad especificada.")
    except Exception as e:
        raise PytubeError(f"Ocurrió un error: {e}")