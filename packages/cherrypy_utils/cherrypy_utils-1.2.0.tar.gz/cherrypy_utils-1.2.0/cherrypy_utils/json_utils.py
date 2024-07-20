import datetime
import cherrypy

from typing import Dict
from cherrypy_utils import timestamp_utils


def convert_request_to_entities(converter):
    request_json = get_request_json()
    if isinstance(request_json, dict):
        return [converter(request_json)]
    else:
        entities = []

        for entity in request_json:
            entities.append(converter(entity))

        return entities


def get_request_json() -> Dict:
    if not hasattr(cherrypy.request, "json"):
        raise TypeError("Request data was not JSON format!")
    else:
        return cherrypy.request.json


def get_request_timestamp() -> datetime.datetime:
    request_json = get_request_json()
    return timestamp_utils.parse_timestamp(request_json["timestamp"])
