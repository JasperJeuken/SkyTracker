"""Error response models"""
from typing import Literal


class Errors:
    """Possible error responses"""

    bad_request: dict = {
        400: {'description': 'Bad request. Server will not process this request due to ' + \
                             'something that is perceived to be a client error.',
              'content': {'application/json': {'example': {'detail': 'information'}}}}
    }
    """dict: bad request (400)"""
    unauthorized: dict = {
        401: {'description': 'Unauthorized. The client has not been authenticated.',
              'content': {'application/json': {'example': {'detail': 'information'}}}}
    }
    """dict: unauthorized (401)"""
    not_found: dict = {
        404: {'description': 'Not found. The requested resource could not be found.',
              'content': {'application/json': {'example': {'detail': 'information'}}}}
    }
    """dict: not found (404)"""
    too_many_requests: dict = {
        429: {'description': 'Too many requests. The user has sent too many requests in a ' + \
                             'short time',
              'content': {'application/json': {'example': {'detail': 'information'}}}}
    }
    """dict: too many requests (429)"""
    internal_server_error: dict = {
        500: {'description': 'Internal server error. Something went wrong while processing ' + \
                             'the request',
              'content': {'application/json': {'example': {'detail': 'information'}}}}
    }
    """dict: internal server error (500)"""

    @classmethod
    def combine(cls, *names: Literal['bad_request', 'unauthorized', 'not_found',
                                     'too_many_requests', 'internal_server_error']) -> dict:
        """Combine multiple errors by name

        Returns:
            dict: combined errors
        """
        combined = {}
        for name in names:
            combined |= getattr(cls, name)
        return combined
