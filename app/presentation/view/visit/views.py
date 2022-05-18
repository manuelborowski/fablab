from . import visit
from app import flask_app
from flask import redirect, url_for, render_template
from flask_login import login_required
from app.presentation.view import base_multiple_items
from app.application import socketio as msocketio
import app.application.visitor


@visit.route('/visit/visit', methods=['POST', 'GET'])
@login_required
def show():
    # start = datetime.datetime.now()
    base_multiple_items.update(table_configuration)
    ret = base_multiple_items.show(table_configuration)
    # print('visit.show', datetime.datetime.now() - start)
    return ret


@visit.route('/visit/table_ajax', methods=['GET', 'POST'])
@login_required
def table_ajax():
    # start = datetime.datetime.now()
    base_multiple_items.update(table_configuration)
    ret =  base_multiple_items.ajax(table_configuration)
    # print('visit.table_ajax', datetime.datetime.now() - start)
    return ret


@visit.route('/visitor/table_action', methods=['GET', 'POST'])
def table_action():
    return redirect(url_for('visit.show'))



def get_filters():
    filters = [
        {
            'type': 'input',
            'name': 'filter_date',
            'label': 'Datum (dd/mm/jjjj)',
        }
    ]
    return filters


def get_show_gauges():
    return ''


table_configuration = {
    'view': 'visit',
    'title': 'Bezoeken',
    'buttons': [],
    'delete_message': '',
    'get_filters': get_filters,
    'get_show_info': get_show_gauges,
    'item': {},
    'href': [],
    'pre_filter': app.data.visitor.visit_pre_filter,
    'format_data': app.application.visitor.visit_format_data,
    'filter_data': app.data.visitor.visit_filter_data,
    'search_data': app.data.visitor.visit_search_data,
    'default_order': (1, 'asc'),
}


@visit.route('/visit/start', methods=['POST', 'GET'])
def start_fablab():
    return render_template('visit/visit.html', api_key=flask_app.config['API_KEY'])