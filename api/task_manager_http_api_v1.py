from flask import Blueprint,request,jsonify,abort
from model.task_manager import manager
from model.task import Task

bp=Blueprint('tasks',__name__,url_prefix='/api/v1/tasks')

#query
@bp.route('/',methods=['GET'])
def get_tasks():
    filters=request.args
    return jsonify(manager.query(filters))


@bp.route('/<int:id_>',methods=['GET'])
def get_tasks_id(id_):
    filters={'id':id_}
    rv=manager.query(filters)
    if len(rv)>0:
        return  jsonify(rv[0])
    else:
        abort(404)


@bp.route('/<int:id_>/<string:property_>',methods=['GET'])
def get_tasks_id_property(id_,property_):
    filters={'id':id_}
    rv=manager.query(filters)
    if len(rv)>0 and property_ in rv[0]:
        return jsonify(rv[0][property_])
    else:
        abort(404)


@bp.route('/top/<int:cnt>',methods=['GET'])
def top(cnt):
    return jsonify(manager.top(cnt))


#create
@bp.route('/',methods=['POST'])
def post_tasks():
    config=request.json
    if isinstance(config,dict):
        task=Task(**config)
    else:
        abort(415)
    if manager.insert(task):
        return jsonify(task)
    else:
        abort(406)


#update
@bp.route('/<int:id_>',methods=['POST'])
def update_tasks(id_):
    config=request.json
    if manager.update(id_,config):
        return jsonify(manager.query({'id':id_})[0])
    else:
        abort(406)
