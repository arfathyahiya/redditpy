import requests


class RedditBotException(Exception):
    pass


class WrongCreds(RedditBotException):
    pass


class HTTPException(RedditBotException):
    def __init__(self, response: requests.Response, *, response_json=None):
        self.response = response


class APIException(HTTPException):
    pass


class BadRequest(HTTPException):
    pass


class NotFound(HTTPException):
    pass


class Unauthorized(HTTPException):
    pass


class Forbidden(HTTPException):
    pass


class TooManyRequests(HTTPException):
    pass
