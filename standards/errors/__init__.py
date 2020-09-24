from flask import jsonify
from standards import app
from standards.errors.errors import (
    BadRequestException,
    UnprocessableEntityException,
    UnsupportedMediaTypeException,
    BadRequestSyntaxException
)


@app.errorhandler(BadRequestException)
def handle_bad_request_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.errorhandler(UnprocessableEntityException)
def handle_bad_request_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.errorhandler(UnsupportedMediaTypeException)
def handle_bad_request_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.errorhandler(BadRequestSyntaxException)
def handle_bad_request_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

