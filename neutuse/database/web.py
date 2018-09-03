import json
import requests as rq
from flask import Blueprint, request, jsonify, abort, render_template

 
bp = Blueprint('web', __name__, template_folder='templates', static_folder='static')

@bp.route('/')
def index():
    return render_template('index.html')
    
@bp.route('/tasks')
def tasks():
    return render_template('tasks.html')
    
@bp.route('/services')
def services():
    return render_template('services.html')
