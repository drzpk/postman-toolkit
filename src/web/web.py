from flask import Flask, make_response, jsonify

from .facade import WebFacade
from ..core.config import ConfigProperty
from ..core.toolkit import PostmanToolkit


app = Flask("postman-toolkit-web")

toolkit = PostmanToolkit()
facade = WebFacade(toolkit.profiled_configuration)


@app.route("/config/<name>", methods=["GET"])
def get_config(name):
    v = facade.get_config(name)
    if v is not None:
        return jsonify(v)
    else:
        return make_response("", 404)


@app.route("/config", methods=["GET"])
def list_config():
    v = facade.list_config()
    return make_response(v)


@app.route("/config/reload", methods=["POST"])
def reload_config():
    facade.reload_config()
    return make_response("", 201)


def run_web():
    app.run(
        ConfigProperty.SERVER_HOST.get_value(),
        ConfigProperty.SERVER_PORT.get_value(),
        ConfigProperty.DEBUG.get_value())
