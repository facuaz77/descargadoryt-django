import boto3
from django.http import FileResponse
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
            # Redirigir al usuario a la URL de descarga
            response = descargar_video_audio(request, link, formato, calidad_video, calidad_audio)
            return response

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
            # Descargar el archivo en un objeto de almacenamiento en la nube (Amazon S3)
            s3_bucket = 'your-s3-bucket-name'
            s3_client = boto3.client('s3')
            file_name = f"{stream.title}.{stream.subtype}"
            s3_key = f"path/in/s3/bucket/{file_name}"
            
            # Descargar el archivo en el objeto de almacenamiento en la nube (Amazon S3)
            stream.download(output_path='/tmp', filename=file_name)
            s3_client.upload_file(f'/tmp/{file_name}', s3_bucket, s3_key)

            # Generar un pre-signed URL para el objeto en el bucket de S3
            s3_url = s3_client.generate_presigned_url('get_object', Params={'Bucket': s3_bucket, 'Key': s3_key}, ExpiresIn=3600)

            # Devolver la respuesta con el enlace al archivo descargado
            response = FileResponse(s3_url)
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response

        else:
            raise PytubeError("No se encontró la calidad especificada.")

    except Exception as e:
        raise PytubeError(f"Ocurrió un error: {e}")