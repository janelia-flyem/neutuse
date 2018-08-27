from functools import wraps
import json
from flask import Blueprint, request, jsonify, abort, current_app, g


bp = Blueprint('tasks', __name__)


def require_manager(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        g.man = current_app.config['man']
        return func(*args, **kwargs)
    return wrapper
    

#query
@bp.route('/', methods=['GET'])
@require_manager
def get_tasks():
    filters = request.args
    return jsonify(g.man.query(filters))


@bp.route('/<int:id_>', methods=['GET'])
@require_manager
def get_tasks_id(id_):
    filters = {'id' : id_}
    rv = g.man.query(filters)
    if len(rv) > 0:
        return  jsonify(rv[0])
    else:
        abort(404)


@bp.route('/<int:id_>/<string:property_>', methods=['GET'])
@require_manager
def get_tasks_id_property(id_, property_):
    filters = {'id' : id_}
    rv = g.man.query(filters)
    if len(rv) > 0 and property_ in rv[0]:
        return jsonify(rv[0][property_])
    else:
        abort(404)



@bp.route('/top/<string:type_>/<string:name>/<int:cnt>', methods=['GET'])
@require_manager
def top(type_, name, cnt):
    return jsonify(g.man.top(cnt, type_, name))


#create
@bp.route('/', methods=['POST'])
@require_manager
def post_tasks():
    config = request.json
    if isinstance(config, dict):
        task = Task(**config)
    else:
        abort(415)
    if g.man.insert(task):
        return jsonify(task)
    else:
        abort(406)


#update status :processing ,failed or done
@bp.route('/<int:id_>/status/<string:status>', methods=['POST'])
@require_manager
def update_status(id_, status):
    if not status in ('processing', 'failed', 'done'):
        abort(404)
    if g.man.update(id_, {'status' : status}):
        return jsonify(g.man.query({'id' : id_})[0])
    else:
        abort(406)
        

#add comment
@bp.route('/<int:id_>/comments', methods=['POST'])
@require_manager
def add_comment(id_):
    comment = request.json
    task = g.man.query({'id' : id_})
    if len(task) < 1:
        abort(404)
    task = task[0]
    comments = task.comment
    comments.append(str(comment))
    if g.man.update(id_, {'comment' : json.dumps(comments)}):
        return jsonify(g.man.query({'id' : id_})[0])
    else:
        abort(406)
