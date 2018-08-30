import json
import requests as rq
from flask import Blueprint, request, jsonify, abort, render_template

 
bp = Blueprint('client', __name__, template_folder='templates', static_folder='static')

@bp.route('/')
def index():
    return render_template('index.html')