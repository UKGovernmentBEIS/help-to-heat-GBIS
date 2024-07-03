import logging

logger = logging.getLogger(__name__)

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
