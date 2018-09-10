'''
This file exposes RESTful HTTP APIS to interact with service manager and task manager.
'''


from functools import wraps
import json
import threading
import time
from datetime import datetime

from flask import Blueprint, request, jsonify, abort


from .manager import Manager


bp = Blueprint('tasks', __name__)


def logging_and_check(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
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
        except Exception as e:
            rv = 'FAILED: Request failed because ' + str(e)
            Manager.get().logger.info(rv)
            return rv, 400
    return wrapper


@bp.route('/services/', methods=['GET'])
@bp.route('/services', methods=['GET'])
@logging_and_check
def service_list():
    service_list = Manager.get().service.online_services()
    if len(service_list) > 0:
        return jsonify(service_list)
    rv = 'FAILED: No active services found'
    Manager.get().logger.info(rv)
    return rv, 400


@bp.route('/services/', methods=['POST'])
@bp.route('/services', methods=['POST'])
@logging_and_check
def create_service():
    config = request.json
    id_ = Manager.get().service.add(config)
    return jsonify(Manager.get().service.get(id_))

    

@bp.route('/services/<int:id_>/', methods=['GET'])
@bp.route('/services/<int:id_>', methods=['GET'])
@logging_and_check
def get_service_by_id(id_):
    rv = Manager.get().service.get(id_)
    return jsonify(rv)
    

@bp.route('/services/<int:id_>/pulse/', methods=['POST'])
@bp.route('/services/<int:id_>/pulse', methods=['POST'])
@logging_and_check
def pulse(id_):
    if Manager.get().service.update(id_, {'last_active': datetime.now(), 'status':'ready'}):
        return jsonify(Manager.get().service.get(id_))
    rv = 'FAILED: No services have this id'
    Manager.get().logger.info(rv)
    return rv, 400


#query
@bp.route('/tasks/pagination/<string:order_by>/<int:page_size>/<int:page_index>', methods=['GET'])
@bp.route('/tasks/pagination/<string_order_by>/<int:page_size><int:page_index>', methods=['GET'])
@logging_and_check
def get_tasks_pagination(order_by, page_size, page_index):
    filters = request.args
    start_index = page_size * page_index
    end_index = page_size * (page_index + 1)
    rv = Manager.get().task.query(filters, order_by, start_index, end_index, True)
    if len(rv) == 0:
        raise Exception('No tasks meet the conditions')
    return jsonify(rv)
    

#query
@bp.route('/tasks/', methods=['GET'])
@bp.route('/tasks', methods=['GET'])
@logging_and_check
def get_tasks():
    filters = request.args
    rv = Manager.get().task.query(filters)
    if len(rv) == 0:
        raise Exception('No tasks meet the conditions')
    return jsonify(rv)


@bp.route('/tasks/<int:id_>/', methods=['GET'])
@bp.route('/tasks/<int:id_>', methods=['GET'])
@logging_and_check
def get_tasks_by_id(id_):
    rv = Manager.get().task.get(id_)
    if not rv:
        raise Exception('No task has this ID')
    return jsonify(rv)


@bp.route('/tasks/<int:id_>/<string:property_>/', methods=['GET'])
@bp.route('/tasks/<int:id_>/<string:property_>', methods=['GET'])
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
@logging_and_check
def top(type_, name, cnt):
    rv = Manager.get().task.top(type_, name, cnt)
    if len(rv) == 0:
        raise Exception('No more tasks')
    return jsonify(rv)


#create
@bp.route('/tasks/', methods=['POST'])
@bp.route('/tasks', methods=['POST'])
@logging_and_check
def post_tasks():
    config = request.json
    id_ = Manager.get().task.add(config)
    return jsonify(Manager.get().task.get(id_))


#update status :processing ,failed or done
@bp.route('/tasks/<int:id_>/status/<string:status>/<int:service_id>', methods=['POST'])
@bp.route('/tasks/<int:id_>/status/<string:status>/<int:service_id>', methods=['POST'])
@logging_and_check
def update_status(id_, status, service_id):
    if not status in ('processing', 'failed', 'done'):
        raise Exception('Illegal status')
    Manager.get().task.update(id_, {'status':status, 'service_id':service_id})
    return jsonify(Manager.get().task.get(id_))
        

#add comment
@bp.route('/tasks/<int:id_>/comments/', methods=['POST'])
@bp.route('/tasks/<int:id_>/comments', methods=['POST'])
@logging_and_check
def add_comment(id_):
    comment = request.json
    if 0 == Manager.get().task.add_comment(id_, json.dumps(comment)):
        raise Exception('Failed to add comment')
    return jsonify(Manager.get().task.get(id_))
