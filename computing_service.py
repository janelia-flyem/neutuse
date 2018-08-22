from flask import Flask

from api.task_manager_http_api_v1 import bp

app=Flask(__name__)
app.register_blueprint(bp)

@app.route('/',methods=['GET'])
def index():
    return 'Welcome to computing service'

