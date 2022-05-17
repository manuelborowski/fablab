from . import badge
from app import flask_app
from flask import render_template
from flask_login import login_required, logout_user


@badge.route('/badge/', methods=['POST', 'GET'])
@login_required
def show():
    return render_template('badge/badge.html')

################# a visit ###############
@badge.route('/badge/start', methods=['POST', 'GET'])
def badge_start():
    logout_user()
    return render_template('badge/visit.html', api_key=flask_app.config['API_KEY'])
