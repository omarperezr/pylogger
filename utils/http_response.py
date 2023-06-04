from django.http import HttpResponse


def is_success_response(response: HttpResponse) -> bool:
    return 200 <= response.status_code < 300


def is_server_error_response(response: HttpResponse) -> bool:
    return response.status_code == 500
