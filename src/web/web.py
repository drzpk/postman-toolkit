from flask import Flask, request, make_response, jsonify

from .facade import WebFacade, FacadeException
from ..core.config import ConfigProperty
from ..core.toolkit import PostmanToolkit


app = Flask("postman-toolkit-web")
with app.app_context():
    toolkit = PostmanToolkit()
    facade = WebFacade(toolkit)


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


@app.teardown_appcontext
def on_destroy(_):
    PostmanToolkit.destroy()


@exception_handler
@app.route("/config/details", methods=["POST"])
def get_config_details():
    property_name = request.json["name"]
    v = facade.get_property_details(property_name)
    if v is not None:
        return jsonify(v)
    else:
        return make_response("", 404)


@exception_handler
@app.route("/config", methods=["GET"])
def list_properties():
    active_only = request.args.get("active_only", None) is not None

    v = facade.list_properties(active_only)
    return make_response(v)


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
@app.route("/profiles/<id>/activate", methods=["POST"])
def activate_profile(id):
    if facade.set_profile_enabled_state(id, True):
        return make_response("", 200)
    return make_response("", 404)


@exception_handler
@app.route("/profiles/<id>/deactivate", methods=["POST"])
def deactivate_profile(id):
    if facade.set_profile_enabled_state(id, False):
        return make_response("", 200)
    return make_response("", 404)


@exception_handler
@app.route("/profiles/<id>/up", methods=["POST"])
def move_profile_up(id):
    facade.change_profile_priority(id, True)
    return make_response("", 200)


@exception_handler
@app.route("/profiles/<id>/down", methods=["POST"])
def move_profile_down(id):
    facade.change_profile_priority(id, False)
    return make_response("", 200)


@exception_handler
@app.route("/profiles/<id>", methods=["DELETE"])
def delete_profile(id):
    if facade.delete_profile(id):
        return make_response("", 204)
    return make_response("", 404)


@exception_handler
@app.route("/profiles/<id>/config", methods=["GET"])
def list_profile_config(id):
    active_only = request.args.get("active_only", None) is not None
    config_list = facade.list_properties(active_only, id)
    if config_list is None:
        return make_response("", 404)
    else:
        return make_response(config_list)


@exception_handler
@app.route("/profiles/<id>/config", methods=["PUT"])
def create_profile_config(id):
    body = request.json
    if body is None or "name" not in body or body["name"] is None:
        return make_response("Name not specified", 422)
    value = ""
    if "value" in body and body["value"] is not None:
        value = body["value"]

    facade.create_property(id, body["name"], value)
    return make_response("", 201)


@exception_handler
@app.route("/profiles/<profile_id>/config/<property_id>", methods=["POST"])
def update_profile_config(profile_id, property_id):
    body = request.json
    if body is None or "value" not in body or body["value"] is None:
        return make_response("New value not specified", 422)

    facade.set_property_value(profile_id, property_id, body["value"])
    return make_response("")


@exception_handler
@app.route("/profiles/<profile_id>/config/<property_id>", methods=["DELETE"])
def delete_profile_config(profile_id, property_id):
    facade.delete_property(profile_id, property_id)


@exception_handler
@app.route("/profiles/<profile_name>/config/<old_name>/rename", methods=["POST"])
def rename_profile_config(profile_name, old_name):
    body = request.json
    if body is None or "new_name" not in body or body["new_name"] is None:
        return make_response("New name not specified", 422)

    if facade.rename_property(profile_name, old_name, body["new_name"]):
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
