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
from .utils import mail, slack

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
        g.logger = current_app.config['logger']
        params = request.args
        info = request.method + ' ' + request.base_url 
        if 'u' in params:
            info += ' user:{}'.format(params['u'])
        if 'app' in params:
            info += ' app:{}'.format(params['app'])
        g.logger.info(info)
        if request.method == 'POST':
            g.logger.info('POSTED DATA: {}'.format(request.json))
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
    

@bp.route('/services/', methods=['GET'])
@bp.route('/services', methods=['GET'])
@require_serman
@require_logger
def service_list():
    service_list = g.service_man.all()
    if len(service_list) > 0:
        return jsonify(service_list)
    rv = 'FAILED: No active services found'
    g.logger.info(rv)
    return rv, 400


@bp.route('/services/', methods=['POST'])
@bp.route('/services', methods=['POST'])
@require_serman
@require_logger
def create_service():
    config = request.json
    if 'type' in config and 'name' in config:
        id_ = g.service_man.add({'type':config['type'], 'name':config['name']})
        return jsonify(g.service_man.get(id_))
    rv = 'FAILED: Missing task type or name'
    g.logger.info(rv)
    return rv, 400
    

@bp.route('/services/<int:id_>/pulse/', methods=['POST'])
@bp.route('/services/<int:id_>/pulse', methods=['POST'])
@require_serman
@require_logger
def pulse(id_):
    if g.service_man.update(id_, {'last_active': datetime.now()}):
        return jsonify(g.service_man.get(id_))
    rv = 'FAILED: No services have this id'
    g.logger.info(rv)
    return rv, 400


#query
@bp.route('/tasks/pagination/<string:odered_by>/<int:page_size>/<int:page_num>', methods=['GET'])
@bp.route('/tasks/pagination/<string_odered_by>/<int:page_size><int:page_num>', methods=['GET'])
@require_taskman
@require_logger
def get_tasks_pagination(odered_by, page_size, page_num):
    filters = request.args
    if odered_by not in Task.__mapping__.keys():
            rv  = 'FAILED: Invalid odered_by key word'
            g.logger.info(rv)
            return rv, 400 
    for key in filters.keys():
        if key not in Task.__mapping__.keys():
            rv  = 'FAILED: Invalid query filters'
            g.logger.info(rv)
            return rv, 400
    rv = g.man.query(filters,odered_by=odered_by,desc=True)
    start = page_num*page_size
    end = (page_num+1)*page_size
    rv = rv[start:end]
    if len(rv) == 0:
        rv = 'FAILED: No tasks meet the conditions'
        g.logger.info(rv)
        return rv, 400
    return jsonify(rv)
    

#query
@bp.route('/tasks/', methods=['GET'])
@bp.route('/tasks', methods=['GET'])
@require_taskman
@require_logger
def get_tasks():
    filters = request.args
    for key in filters.keys():
        if key not in Task.__mapping__.keys():
            rv  = 'FAILED: Invalid query filters'
            g.logger.info(rv)
            return rv, 400
    rv = g.man.query(filters)
    if len(rv) == 0:
        rv = 'FAILED: No tasks meet the conditions'
        g.logger.info(rv)
        return rv, 400
    return jsonify(rv)


@bp.route('/tasks/<int:id_>/', methods=['GET'])
@bp.route('/tasks/<int:id_>', methods=['GET'])
@require_taskman
@require_logger
def get_tasks_by_id(id_):
    filters = {'id' : id_}
    rv = g.man.query(filters)
    if len(rv) > 0:
        return  jsonify(rv[0])
    else:
        rv  = 'FAILED: No tasks have this id'
        g.logger.info(rv)
        return rv, 400


@bp.route('/tasks/<int:id_>/<string:property_>/', methods=['GET'])
@bp.route('/tasks/<int:id_>/<string:property_>', methods=['GET'])
@require_taskman
@require_logger
def get_tasks_property_by_id(id_, property_):
    filters = {'id' : id_}
    rv = g.man.query(filters)
    if len(rv) > 0:
        if property_ in rv[0]:
            return jsonify(rv[0][property_])
        else:
            rv = 'FAILED: Task found, but it does not contain the specified property'
            g.logger.info(rv)
            return rv, 400
    else:
        rv  = 'FAILED: No tasks have this id'
        g.logger.info(rv)
        return rv, 400


@bp.route('/tasks/top/<string:type_>/<string:name>/<int:cnt>/', methods=['GET'])
@bp.route('/tasks/top/<string:type_>/<string:name>/<int:cnt>', methods=['GET'])
@require_taskman
@require_logger
def top(type_, name, cnt):
    rv = g.man.top(cnt, type_, name)
    if len(rv) > 0:
        return jsonify(rv)
    else:
        rv = 'FAILED: No more tasks'
        g.logger.info(rv)
        return rv, 400


#create
@bp.route('/tasks/', methods=['POST'])
@bp.route('/tasks', methods=['POST'])
@require_taskman
@require_logger
def post_tasks():
    config = request.json
    try:
        task = Task(**config)
    except Exception as e:
        rv = 'FAILED: Failed to create the task because of invalid properties: ' + str(e) 
        g.logger.info(rv)
        return rv, 400
    if g.man.insert(task):
        return jsonify(task)
    else:
        rv = 'FAILED: Task created, but failed to store into the database'
        g.logger.info(rv)
        return rv, 400


#update status :processing ,failed or done
@bp.route('/tasks/<int:id_>/status/<string:status>/', methods=['POST'])
@bp.route('/tasks/<int:id_>/status/<string:status>', methods=['POST'])
@require_taskman
@require_logger
def update_status(id_, status):
    if not status in ('processing', 'failed', 'done'):
        rv = 'FAILED: Illegal status'
        g.logger.info(rv)
        return rv, 400
    if g.man.update(id_, {'status' : status}):
        return jsonify(g.man.query({'id' : id_})[0])
    else:
        rv = 'FAILED: Failed to update the status'
        g.logger.info(rv)
        return rv, 400
        

#add comment
@bp.route('/tasks/<int:id_>/comments/', methods=['POST'])
@bp.route('/tasks/<int:id_>/comments', methods=['POST'])
@require_taskman
@require_logger
def add_comment(id_):
    comment = request.json
    task = g.man.query({'id' : id_})
    if len(task) < 1:
        rv = 'FAILED: No tasks have this id'
        g.logger.info(rv)
        return rv, 400
    task = task[0]
    comments = task.comments
    try:
        comments.append(str(comment))
    except Exception as e:
        rv = 'FAILED: Invalid comments format: ' + str(e) 
        g.logger.info(rv)
        return rv, 400
    if g.man.update(id_, {'comments' : json.dumps(comments)}):
        return jsonify(g.man.query({'id' : id_})[0])
    else:
        rv = 'FAILED: Failed to add the comment'
        g.logger.info(rv)
        return rv, 400
