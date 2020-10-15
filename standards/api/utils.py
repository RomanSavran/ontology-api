import json
import requests

from copy import deepcopy
from jsonschema import Draft7Validator
from requests.exceptions import HTTPError

from standards import app
from standards.api.genson import SchemaBuilder
from standards.api.genson.utils import (
    NestedDict,
    schema_path_id_generator,
    schema_sorted_first_level,
    sorted_nested_dict
)
from standards.errors import UnprocessableEntityException, BadRequestException


def make_request(method: str, url: str, **kwargs) -> requests.Response:
    try:
        response = requests.request(method=method, url=url, **kwargs)
        response.raise_for_status()
    except HTTPError as http_e:
        app.logger.error(http_e)
        raise BadRequestException(f"Nothing matches the given URI: {str(http_e.response.url)}")
    except Exception as e:
        app.logger.error(e)
        raise BadRequestException(f"Nothing matches the given URI: {str(e.response.url)}")
    else:
        return response


def get_context(url: str) -> json:
    try:
        context = make_request('GET', url).json()
    except (ValueError, AttributeError) as e:
        app.logger.exception(
            f'The response body does not contain valid json: {e}')
    else:
        return context


def get_schema(url: str) -> json:
    try:
        schema = make_request('GET', url).json()
    except (ValueError, AttributeError) as e:
        app.logger.exception(
            f'The response body does not contain valid json: {e}')
    else:
        return schema


def get_context_url_from_request_body(data: dict) -> str:
    try:
        context_url = data['@context']
    except (KeyError, TypeError) as e:
        app.logger.exception(e)
        raise UnprocessableEntityException(
            f'The request body must contain valid key \"@context\" with url value.')
    else:
        return str(context_url)


def get_schema_url_from_context(data: dict) -> str:
    try:
        schema_url = data['@context']['@schema']
    except (KeyError, TypeError) as e:
        app.logger.exception(e)
        raise UnprocessableEntityException(
            f'\"@schema\" doesn\'t exist or not found using @context url.')
    else:
        return schema_url


def get_validation_errors(validator: Draft7Validator, data: json) -> dict:
    errors = {}
    for error in sorted(validator.iter_errors(data), key=str):
        key = error.message.split()[0]
        errors.update({key.replace("'", ""): error.message.replace(key, "").strip()})
    return errors


def validate_json(request):
    data = request.get_json()

    # get context
    context_url = get_context_url_from_request_body(data)
    context = get_context(context_url)

    # get schema
    schema_url = get_schema_url_from_context(context)
    schema = get_schema(schema_url)

    v = Draft7Validator(schema)

    errors = get_validation_errors(validator=v, data=data)
    if errors:
        raise UnprocessableEntityException(
            message='One or more fields raised validation errors',
            payload=errors
        )

    return {'isValid': 'True'}


def schema_generator(request):
    data = request.get_json()

    builder = SchemaBuilder('http://json-schema.org/draft-06/schema#')
    builder.add_object(data)

    schema = json.loads(builder.to_json(indent=4))

    context_url = get_context_url_from_request_body(data)

    schema['$id'] = context_url.replace("Context", "Schema")[:-1]
    schema['properties']['@context']['const'] = context_url

    nested_dict = NestedDict(deepcopy(schema))
    schema_path_id_generator(schema, nested_dict)
    nested_dict = schema_sorted_first_level(nested_dict)
    nested_dict = sorted_nested_dict(nested_dict)

    return nested_dict
