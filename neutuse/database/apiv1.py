'''
This file exposes RESTful HTTP APIS to interact with service manager and task manager.
'''


from functools import wraps
import json
import threading
import time
from datetime import datetime

from flask import Blueprint, request, jsonify, abort, current_app, g

from .task import Task

from .manager import Manager


bp = Blueprint('tasks', __name__)

    
      
def require_taskman(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        g.man = current_app.config['task_man']
        return func(*args, **kwargs)
    return wrapper
    

def require_logger(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        params = request.args
        info = request.method + ' ' + request.base_url 
        if 'u' in params:
            info += ' user:{}'.format(params['u'])
        if 'app' in params:
            info += ' app:{}'.format(params['app'])
        Manager.get().logger.info(info)
        if request.method == 'POST':
            Manager.get().logger.info('POSTED DATA: {}'.format(request.json))
        return func(*args, **kwargs)
    return wrapper
    

def require_serman(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'service_man' not in current_app.config:
            email = current_app.config.get('email',None)
            slack = current_app.config.get('slack',None)
            current_app.config['service_man'] = Manager(email=email, slack=slack).service
        g.service_man = current_app.config['service_man']
        return func(*args, **kwargs)
    return wrapper
  

def logging_and_check(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            rv = 'FAILED: Request failed because ' + str(e)
            Manager.get().logger.info(rv)
            return rv, 400
    return wrapper

@bp.route('/services/', methods=['GET'])
@bp.route('/services', methods=['GET'])
@require_serman
@require_logger
@logging_and_check
def service_list():
    service_list = g.service_man.all()
    if len(service_list) > 0:
        return jsonify(service_list)
    rv = 'FAILED: No active services found'
    Manager.get().logger.info(rv)
    return rv, 400


@bp.route('/services/', methods=['POST'])
@bp.route('/services', methods=['POST'])
@require_serman
@require_logger
@logging_and_check
def create_service():
    config = request.json
    if 'type' in config and 'name' in config:
        id_ = g.service_man.add({'type':config['type'], 'name':config['name']})
        return jsonify(g.service_man.get(id_))
    rv = 'FAILED: Missing task type or name'
    Manager.get().logger.info(rv)
    return rv, 400
    

@bp.route('/services/<int:id_>/pulse/', methods=['POST'])
@bp.route('/services/<int:id_>/pulse', methods=['POST'])
@require_serman
@require_logger
@logging_and_check
def pulse(id_):
    if g.service_man.update(id_, {'last_active': datetime.now()}):
        return jsonify(g.service_man.get(id_))
    rv = 'FAILED: No services have this id'
    Manager.get().logger.info(rv)
    return rv, 400


#query
@bp.route('/tasks/pagination/<string:order_by>/<int:page_size>/<int:page_index>', methods=['GET'])
@bp.route('/tasks/pagination/<string_order_by>/<int:page_size><int:page_index>', methods=['GET'])
@require_taskman
@require_logger
@logging_and_check
def get_tasks_pagination(order_by, page_size, page_index):
    filters = request.args
    rv = Manager.get().task.pagination(filters, order_by, page_size, page_index, True)
    if len(rv) == 0:
        raise Exception('No tasks meet the conditions')
    return jsonify(rv)
    

#query
@bp.route('/tasks/', methods=['GET'])
@bp.route('/tasks', methods=['GET'])
@require_taskman
@require_logger
@logging_and_check
def get_tasks():
    filters = request.args
    rv = Manager.get().task.query(filters)
    if len(rv) == 0:
        raise Exception('No tasks meet the conditions')
    return jsonify(rv)


@bp.route('/tasks/<int:id_>/', methods=['GET'])
@bp.route('/tasks/<int:id_>', methods=['GET'])
@require_taskman
@require_logger
@logging_and_check
def get_tasks_by_id(id_):
    rv = Manager.get().task.get(id_)
    if not rv:
        raise Exception('No task has this ID')
    return jsonify(rv)


@bp.route('/tasks/<int:id_>/<string:property_>/', methods=['GET'])
@bp.route('/tasks/<int:id_>/<string:property_>', methods=['GET'])
@require_taskman
@require_logger
@logging_and_check
def get_tasks_property_by_id(id_, property_):
    rv = Manager.get().task.get(id_)
    if not rv:
        raise Exception('No task has this ID')
    if property_ not in rv:
        raise Exception('Task object has not ' + property_ + ' property')
    return jsonify(rv[property_])


@bp.route('/tasks/top/<string:type_>/<string:name>/<int:cnt>/', methods=['GET'])
@bp.route('/tasks/top/<string:type_>/<string:name>/<int:cnt>', methods=['GET'])
@require_taskman
@require_logger
@logging_and_check
def top(type_, name, cnt):
    rv = Manager.get().task.top(type_, name, cnt)
    if len(rv) == 0:
        raise Exception('No more tasks')
    return jsonify(rv)


#create
@bp.route('/tasks/', methods=['POST'])
@bp.route('/tasks', methods=['POST'])
@require_taskman
@require_logger
@logging_and_check
def post_tasks():
    config = request.json
    id_ = Manager.get().task.add(config)
    return jsonify(Manager.get().task.get(id_))


#update status :processing ,failed or done
@bp.route('/tasks/<int:id_>/status/<string:status>/', methods=['POST'])
@bp.route('/tasks/<int:id_>/status/<string:status>', methods=['POST'])
@require_taskman
@require_logger
@logging_and_check
def update_status(id_, status):
    if not status in ('processing', 'failed', 'done'):
        raise Exception('Illegal status')
    Manager.get().task.update(id_, {'status':status})
    return jsonify(Manager.get().task.get(id_))
        

#add comment
@bp.route('/tasks/<int:id_>/comments/', methods=['POST'])
@bp.route('/tasks/<int:id_>/comments', methods=['POST'])
@require_taskman
@require_logger
@logging_and_check
def add_comment(id_):
    comment = request.json
    if 0 == Manager.get().task.add_comment(id_, json.dumps(comment)):
        raise Exception('Failed to add comment')
    return jsonify(Manager.get().task.get(id_))

    #return jsonify(Manager.get().task.get(id_))
