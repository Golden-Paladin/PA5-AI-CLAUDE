from flask import Blueprint, jsonify, request
from services.tasks import get_task, create_task, update_task_priority, list_tasks
from services.users import get_user, list_users, get_notification_pref, update_notification_pref
from utils.errors import AppError

api = Blueprint("api", __name__)

@api.errorhandler(AppError)
def handle_app_error(e):
    return jsonify({"error": e.message}), e.status_code

@api.route("/tasks", methods=["GET"])
def list_tasks_route():
    priority = request.args.get("priority")
    if priority is not None:
        try:
            priority = int(priority)
        except ValueError:
            pass
    return jsonify(list_tasks(priority))

@api.route("/tasks/<int:task_id>", methods=["GET"])
def get_task_route(task_id):
    return jsonify(get_task(task_id))

@api.route("/tasks", methods=["POST"])
def create_task_route():
    data = request.get_json()
    if "priority" in data and data["priority"] is not None:
        return jsonify(create_task(data["title"], data["user_id"], data["priority"])), 201
    return jsonify(create_task(data["title"], data["user_id"])), 201

@api.route("/tasks/<int:task_id>", methods=["PATCH"])
def update_task_route(task_id):
    data = request.get_json()
    return jsonify(update_task_priority(task_id, data.get("priority")))

@api.route("/users/<int:user_id>", methods=["GET"])
def get_user_route(user_id):
    return jsonify(get_user(user_id))

@api.route("/users", methods=["GET"])
def list_users_route():
    return jsonify(list_users())

@api.route("/users/<int:user_id>/notifications", methods=["GET"])
def get_notification_pref_route(user_id):
    return jsonify({"notification_pref": get_notification_pref(user_id)})

@api.route("/users/<int:user_id>/notifications", methods=["PATCH"])
def update_notification_pref_route(user_id):
    data = request.get_json()
    return jsonify(update_notification_pref(user_id, data.get("notification_pref")))
