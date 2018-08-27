import json
import requests as rq
from flask import Blueprint, request, jsonify, abort, render_template

bp = Blueprint('client', __name__, template_folder='templates', static_folder='static')

_server = 'http://127.0.0.1:5000/'

def init(host, port):
    global _server
    _server = 'http://' + str(host) + ':' + str(port) + '/'
    
@bp.route('/')
def index():
    return render_template('index.html', server=_server)
