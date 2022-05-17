from flask import request
from . import api
from app.application import  user as muser, visitor as mvisitor
from app import flask_app
import json
from functools import wraps


def key_required(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        if request.values:
            api_key = request.values["api_key"]
        else:
            return json.dumps({"status": False, "data": f'Please provide a key'})
        # Check if API key is correct and valid
        if request.method == "POST" and api_key == flask_app.config['API_KEY']:
            return func(*args, **kwargs)
        else:
            return json.dumps({"status": False, "data": f'Key not valid'})

    return decorator


@api.route('/api/visitor/add', methods=['POST'])
@key_required
def visitor_add():
    data = json.loads(request.data)
    ret = mvisitor.add_visitor(data)
    return(json.dumps(ret))


@api.route('/api/visitor/update', methods=['POST'])
@key_required
def visitor_update():
    data = json.loads(request.data)
    ret = mvisitor.update_visitor(data)
    return(json.dumps(ret))


@api.route('/api/visit/add', methods=['POST'])
@key_required
def visit_add():
    data = json.loads(request.data)
    ret = mvisitor.add_visit(data)
    return(json.dumps(ret))


@api.route('/api/user/add', methods=['POST'])
@key_required
def user_add():
    data = json.loads(request.data)
    ret = muser.add_user(data)
    return(json.dumps(ret))


@api.route('/api/user/update', methods=['POST'])
@key_required
def user_update():
    data = json.loads(request.data)
    ret = muser.update_user(data)
    return(json.dumps(ret))


