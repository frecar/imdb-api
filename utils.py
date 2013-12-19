import json
from encoders import SimpleEncoder

from flask import make_response


def json_response(data, status=200):
    response = make_response(json.dumps(data, cls=SimpleEncoder, indent=4), status)
    response.mimetype = 'application/json'
    return response
