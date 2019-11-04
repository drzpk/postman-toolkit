from flask import Flask, request, make_response, jsonify

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
    active_only = request.args.get("active_only", None) is not None

    v = facade.list_config(active_only)
    return make_response(v)


@app.route("/config/reload", methods=["POST"])
def reload_config():
    facade.reload_config()
    return make_response("", 201)


@app.route("/profiles", methods=["GET"])
def list_profiles():
    active_only = request.args.get("active_only", None) is not None
    return make_response(facade.list_profiles(active_only))


@app.route("/profiles/<name>/config", methods=["GET"])
def list_profile_config(name):
    active_only = request.args.get("active_only", None) is not None
    config_list = facade.list_config(active_only, name)
    if config_list is None:
        return make_response("", 404)
    else:
        return make_response(config_list)


@app.route("/profiles/<profile_name>/config/<name>", methods=["POST"])
def update_profile_config(profile_name, name):
    body = request.json
    if body is None or "value" not in body or body["value"] is None:
        return make_response("New value not specified", 422)

    if not facade.update_config(profile_name, name, body["value"]):
        if "create" in body and body["create"] is True:
            facade.create_config(profile_name, name, body["value"])
            return make_response("", 201)
        else:
            return make_response("", 404)

    return make_response("")


@app.route("/profiles/<profile_name>/config/<name>", methods=["DELETE"])
def delete_profile_config(profile_name, name):
    if facade.delete_config(profile_name, name):
        return make_response("", 204)
    return make_response("", 404)


@app.after_request
def after_request(response):
    if app.debug:
        response.headers["Access-Control-Allow-Origin"] = "*"

    return response


def run_web():
    app.run(
        ConfigProperty.SERVER_HOST.get_value(),
        ConfigProperty.SERVER_PORT.get_value(),
        ConfigProperty.DEBUG.get_value())
