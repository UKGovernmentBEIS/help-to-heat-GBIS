import logging

from django.core.handlers.wsgi import WSGIRequest

logger = logging.getLogger(__name__)
requests_logger = logging.getLogger("help_to_heat.requests")


class ExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # pass requests down the stack without edits
        return self.get_response(request)

    def process_exception(self, _request, exception):
        # print out to AWS logs
        logger.exception(exception)
        return None


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: WSGIRequest):
        requests_logger.info(f"{request.method}: {request.path}")
        return self.get_response(request)
