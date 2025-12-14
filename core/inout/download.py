import io

from django.http import HttpResponse


def excel_response(buffer: io.BytesIO, filename: str) -> HttpResponse:
    content_type = "application/vnd.ms-excel"
    return file_response(buffer=buffer, filename=filename, content_type=content_type)


def file_response(buffer: io.BytesIO, filename: str, content_type: str) -> HttpResponse:
    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type=content_type)
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
