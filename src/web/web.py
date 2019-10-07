from flask import Flask, make_response, jsonify

from .facade import WebFacade
from ..core.config import ConfigProperty

app = Flask("postman-toolkit-web")
facade = WebFacade()


@app.route("/config/<name>")
def get_config(name):
    v = facade.get_config(name)
    if v is not None:
        return jsonify(v)
    else:
        return make_response("", 404)


def run_web():
    app.run(
        ConfigProperty.SERVER_HOST.get_value(),
        ConfigProperty.SERVER_PORT.get_value(),
        ConfigProperty.DEBUG.get_value())
