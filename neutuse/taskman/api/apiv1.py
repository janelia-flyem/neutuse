from functools import wraps
import json

from flask import Blueprint, request, jsonify, abort, current_app, g
from ..task import Task

bp = Blueprint('tasks', __name__)


def require_manager(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        g.man = current_app.config['man']
        return func(*args, **kwargs)
    return wrapper
    

#query
@bp.route('/tasks/', methods=['GET'])
@bp.route('/tasks', methods=['GET'])
@require_manager
def get_tasks():
    filters = request.args
    return jsonify(g.man.query(filters))


@bp.route('/tasks/<int:id_>/', methods=['GET'])
@bp.route('/tasks/<int:id_>', methods=['GET'])
@require_manager
def get_tasks_by_id(id_):
    filters = {'id' : id_}
    rv = g.man.query(filters)
    if len(rv) > 0:
        return  jsonify(rv[0])
    else:
        return jsonify(None)


@bp.route('/tasks/<int:id_>/<string:property_>/', methods=['GET'])
@bp.route('/tasks/<int:id_>/<string:property_>', methods=['GET'])
@require_manager
def get_tasks_property_by_id(id_, property_):
    filters = {'id' : id_}
    rv = g.man.query(filters)
    if len(rv) > 0 and property_ in rv[0]:
        return jsonify(rv[0][property_])
    else:
        return jsonify(None)


@bp.route('/tasks/top/<string:type_>/<string:name>/<int:cnt>/', methods=['GET'])
@bp.route('/tasks/top/<string:type_>/<string:name>/<int:cnt>', methods=['GET'])
@require_manager
def top(type_, name, cnt):
    return jsonify(g.man.top(cnt, type_, name))


#create
@bp.route('/tasks/', methods=['POST'])
@bp.route('/tasks', methods=['POST'])
@require_manager
def post_tasks():
    config = request.json
    try:
        task = Task(**config)
    except:
        return jsonify(None)
    if g.man.insert(task):
        return jsonify(task)
    else:
        return jsonify(None)


#update status :processing ,failed or done
@bp.route('/tasks/<int:id_>/status/<string:status>/', methods=['POST'])
@bp.route('/tasks/<int:id_>/status/<string:status>', methods=['POST'])
@require_manager
def update_status(id_, status):
    if not status in ('processing', 'failed', 'done'):
        return jsonify(None)
    if g.man.update(id_, {'status' : status}):
        return jsonify(g.man.query({'id' : id_})[0])
    else:
        return jsonify(None)
        

#add comment
@bp.route('/tasks/<int:id_>/comments/', methods=['POST'])
@bp.route('/tasks/<int:id_>/comments', methods=['POST'])
@require_manager
def add_comment(id_):
    comment = request.json
    task = g.man.query({'id' : id_})
    if len(task) < 1:
        return jsonify(None)
    task = task[0]
    comments = task.comment
    try:
        comments.append(str(comment))
    except:
        return jsonify(None)
    if g.man.update(id_, {'comment' : json.dumps(comments)}):
        return jsonify(g.man.query({'id' : id_})[0])
    else:
        return jsonify(None)
