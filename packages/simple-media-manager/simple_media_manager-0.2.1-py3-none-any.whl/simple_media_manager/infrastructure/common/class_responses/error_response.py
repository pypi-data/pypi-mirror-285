from rest_framework import status as rest_http_status
from rest_framework.response import Response

from ..data_responses.data_response import Error, Message


class MessageResponse(Response):
    def __init__(self, message: str, status: rest_http_status = rest_http_status.HTTP_200_OK):
        super(MessageResponse, self).__init__(data=Message(message=message).__dict__,
                                              status=status)


class ErrorResponse(Response):
    def __init__(self, exception: Exception, status_code=rest_http_status.HTTP_400_BAD_REQUEST):
        super(ErrorResponse, self).__init__(data=Error(errors=exception.__str__()).__dict__,
                                            status=status_code)
