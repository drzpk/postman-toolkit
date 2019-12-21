from flask import Flask, request, make_response, jsonify

from .facade import WebFacade, FacadeException
from ..core.config import ConfigProperty
from ..core.toolkit import PostmanToolkit


app = Flask("postman-toolkit-web")

toolkit = PostmanToolkit()
facade = WebFacade(toolkit.profiled_configuration)


def exception_handler(original):
    def _wrapper(*args, **kwargs):
        try:
            original(*args, **kwargs)
        except FacadeException as e:
            error = {
                "message": e.message
            }
            return make_response(error, 400)
    return _wrapper


@exception_handler
@app.route("/config/<name>", methods=["GET"])
def get_config(name):
    v = facade.get_config(name)
    if v is not None:
        return jsonify(v)
    else:
        return make_response("", 404)


@exception_handler
@app.route("/config", methods=["GET"])
def list_config():
    active_only = request.args.get("active_only", None) is not None

    v = facade.list_config(active_only)
    return make_response(v)


@exception_handler
@app.route("/config/reload", methods=["POST"])
def reload_config():
    facade.reload_config()
    return make_response("", 204)


@exception_handler
@app.route("/profiles", methods=["POST"])
def create_profile():
    body = request.json
    facade.create_profile(body["name"], body["active"])
    return make_response("", 201)


@exception_handler
@app.route("/profiles", methods=["GET"])
def list_profiles():
    active_only = request.args.get("active_only", None) is not None
    return make_response(facade.list_profiles(active_only))


@exception_handler
@app.route("/profiles/<name>/activate", methods=["POST"])
def activate_profile(name):
    if facade.set_profile_active_state(name, True):
        return make_response("", 200)
    return make_response("", 404)


@exception_handler
@app.route("/profiles/<name>/deactivate", methods=["POST"])
def deactivate_profile(name):
    if facade.set_profile_active_state(name, False):
        return make_response("", 200)
    return make_response("", 404)


@exception_handler
@app.route("/profiles/<name>/up", methods=["POST"])
def move_profile_up(name):
    if facade.change_profile_importance(name, True):
        return make_response("", 200)
    return make_response("", 404)


@exception_handler
@app.route("/profiles/<name>/down", methods=["POST"])
def move_profile_down(name):
    if facade.change_profile_importance(name, False):
        return make_response("", 200)
    return make_response("", 404)


@exception_handler
@app.route("/profiles/<name>", methods=["DELETE"])
def delete_profile(name):
    if facade.delete_profile(name):
        return make_response("", 204)
    return make_response("", 404)


@exception_handler
@app.route("/profiles/<name>/config", methods=["GET"])
def list_profile_config(name):
    active_only = request.args.get("active_only", None) is not None
    config_list = facade.list_config(active_only, name)
    if config_list is None:
        return make_response("", 404)
    else:
        return make_response(config_list)


@exception_handler
@app.route("/profiles/<profile_name>/config", methods=["PUT"])
def create_profile_config(profile_name):
    body = request.json
    if body is None or "name" not in body or body["name"] is None:
        return make_response("Name not specified", 422)
    value = ""
    if "value" in body and body["value"] is not None:
        value = body["value"]

    if facade.create_config(profile_name, body["name"], value):
        return make_response("", 201)
    else:
        return make_response("", 400)


@exception_handler
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


@exception_handler
@app.route("/profiles/<profile_name>/config/<name>", methods=["DELETE"])
def delete_profile_config(profile_name, name):
    if facade.delete_config(profile_name, name):
        return make_response("", 204)
    return make_response("", 404)


@app.after_request
def after_request(response):
    if app.debug:
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "*"

    return response


def run_web():
    app.run(
        ConfigProperty.SERVER_HOST.get_value(),
        ConfigProperty.SERVER_PORT.get_value(),
        ConfigProperty.DEBUG.get_value())
