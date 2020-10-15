from flask import request
from werkzeug.exceptions import BadRequest

from standards import app
from standards.api import api_bp
from standards.api.utils import validate_json, schema_generator
from standards.errors import UnsupportedMediaTypeException, UnprocessableEntityException


@api_bp.route('/validate', methods=['POST'])
def validate():
    try:
        request.json
    except BadRequest:
        raise UnprocessableEntityException()
    if not request.json:
        app.logger.error(f'Entity body format {request.data} is not supported')
        raise UnsupportedMediaTypeException()

    response = validate_json(request)
    return response


@api_bp.route('/schema', methods=['POST'])
def build_schema():
    try:
        request.json
    except BadRequest:
        raise UnprocessableEntityException()
    if not request.json:
        app.logger.error(f'Entity body format {request.data} is not supported')
        raise UnsupportedMediaTypeException()

    response = schema_generator(request)
    return response
