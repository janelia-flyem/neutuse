import json
import requests as rq
from flask import Blueprint,request,jsonify,abort
from config import SERVER

bp=Blueprint('client',__name__,url_prefix='/')

@bp.route('/')
def index():
    rv='<h1>Welcome to computing service</h1>'
    tasks=rq.get(SERVER+'api/v1/tasks/').json()
    for t in tasks:
        rv+=json.dumps(t)
    return rv
