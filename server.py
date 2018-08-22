from flask import Flask

import task_manager_http_api_v1

app=Flask(__name__)
app.register_blueprint(task_manager_http_api_v1.bp)

@app.route('/',methods=['GET'])
def index():
    return 'Welcome to computing service'

