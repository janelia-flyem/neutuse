from flask import Blueprint,request,jsonify,abort
from model.task_manager import TaskManager
from model.task import Task
from config import db,CHECK_INTERVAL,WATING_TIME,ENABLE_RETRY

bp=Blueprint('tasks',__name__)
manager=TaskManager(db,CHECK_INTERVAL,WATING_TIME,ENABLE_RETRY)

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


@bp.route('/top/<string:type_>/<string:name>/<int:cnt>',methods=['GET'])
def top(type_,name,cnt):
    return jsonify(manager.top(cnt,type_,name))


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


#update status :processing ,failed or done
@bp.route('/<int:id_>/status/<string:status>',methods=['POST'])
def update_status(id_,status):
    if not status in ('processing','failed','done'):
        abort(404)
    if manager.update(id_,{'status':status}):
        return jsonify(manager.query({'id':id_})[0])
    else:
        abort(406)
        
#add comment
@bp.route('/<int:id_>/comment/<string:comment>',methods=['POST'])
def add_comment(id_,status):
    task=manager.query({'id':id_})
    if len(task<1):
        abort(404)
    task=task[0]
    if manager.update(id_,{'comment':task.comment.append(comment)}):
        return jsonify(manager.query({'id':id_})[0])
    else:
        abort(406)
