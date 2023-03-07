from flask import Blueprint, jsonify, request
from todo.models import db
from todo.models.todo import Todo
from flask import Blueprint, jsonify
from datetime import datetime
from datetime import timedelta

# import datetime

api = Blueprint("api", __name__, url_prefix="/api/v1")

TEST_ITEM = {
    "id": 1,
    "title": "Watch CSSE6400 Lecture",
    "description": "Watch the CSSE6400 lecture on ECHO360 for week 1",
    "completed": True,
    "deadline_at": "2023-02-27T00:00:00",
    "created_at": "2023-02-20T00:00:00",
    "updated_at": "2023-02-20T00:00:00",
}


@api.route("/health")
def health():
    """Return a status of 'ok' if the server is running and listening to request"""
    return jsonify({"status": "ok"})


@api.route("/todos", methods=["GET"])
def get_todos():
    completed = request.args.get("completed")
    deadline_days = request.args.get("window")

    todos = []

    if completed is not None:
        completed_val = completed == "true"
        completed_items = Todo.query.filter_by(completed=completed_val).all()
        todos.extend(completed_items)

    elif deadline_days is not None:
        deadline_date = datetime.now() + timedelta(days=int(deadline_days))
        due_items = Todo.query.filter(Todo.deadline_at <= deadline_date).all()
        todos.extend(due_items)
    else:
        todos = Todo.query.all()

    result = []
    for todo in todos:
        result.append(todo.to_dict())
    return jsonify(result)


@api.route("/todos/<int:id>", methods=["GET"])
def get_todo(id):
    todo = Todo.query.get(id)
    if todo is None:
        return jsonify({"error": "Todo not found"}), 404
    return jsonify(todo.to_dict())


@api.route("/todos", methods=["POST"])
def create_todo():
    if not valid_json():
        return jsonify({"error": "Invalid json"}), 400

    todo = Todo(
        title=request.json.get("title"),
        description=request.json.get("description"),
        completed=request.json.get("completed", False),
    )

    if "deadline_at" in request.json:
        todo.deadline_at = datetime.fromisoformat(
            request.json.get("deadline_at"))
    # Adds a new record to the database or will update an existing record
    db.session.add(todo)
    # Commits the changes to the database, this must be called for the changes to be saved
    db.session.commit()
    return jsonify(todo.to_dict()), 201


@api.route("/todos/<int:id>", methods=["PUT"])
def update_todo(id):
    if not valid_json():
        return jsonify({"error": "Invalid json"}), 400

    todo = Todo.query.get(id)

    if todo is None:
        return jsonify({"error": "Todo not found"}), 404
    todo.title = request.json.get("title", todo.title)
    todo.description = request.json.get("description", todo.description)
    todo.completed = request.json.get("completed", todo.completed)
    todo.deadline_at = request.json.get("deadline_at", todo.deadline_at)
    db.session.commit()
    return jsonify(todo.to_dict())


@api.route("/todos/<int:id>", methods=["DELETE"])
def delete_todo(id):
    todo = Todo.query.get(id)
    if todo is None:
        return jsonify({}), 200
    db.session.delete(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 200


def valid_json():
    if request.json.get("title") is None:
        return False
    for field in request.json.keys():
        if not hasattr(Todo, field):
            return False
    return True
