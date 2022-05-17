from . import badge
from app import log, supervisor_required, flask_app
from flask import redirect, url_for, request, render_template
from flask_login import login_required, current_user
from app.presentation.view import base_multiple_items
from app.presentation.layout.utils import flash_plus
from app.application import socketio as msocketio, settings as msettings
import sys, json
import app.data.visitor
import app.application.visitor


@badge.route('/badge/', methods=['POST', 'GET'])
@login_required
def show():
    return render_template('badge/badge.html')

################# a visit ###############
@badge.route('/badge/start', methods=['POST', 'GET'])
def badge_start():
    return render_template('badge/visit.html', api_key=flask_app.config['API_KEY'])
