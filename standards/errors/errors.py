class BaseException(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status_code'] = self.status_code
        return rv


class BadRequestException(BaseException):

    def __init__(self, message='Nothing matches the given URI', status_code=404):
        super().__init__(message=message, status_code=status_code)


class UnprocessableEntityException(BaseException):
    def __init__(self, message="Information in the request body can't be parsed or understood.", status_code=422):
        super().__init__(message=message, status_code=status_code)


class UnsupportedMediaTypeException(BaseException):
    def __init__(self, message="Entity body in unsupported format.", status_code=415):
        super().__init__(message=message, status_code=status_code)


class BadRequestSyntaxException(BaseException):
    def __init__(self, message="Bad request syntax or unsupported method", status_code=400):
        super().__init__(message=message, status_code=status_code)
