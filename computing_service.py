from flask import Flask

from api.task_manager_http_api_v1 import bp as api_bp
from webclient.client import bp as client_bp

app=Flask(__name__)
app.register_blueprint(api_bp,url_prefix='/api/v1/tasks')
app.register_blueprint(client_bp,url_prefix='/client')
