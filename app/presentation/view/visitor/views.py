from . import visitor
from app import log, supervisor_required, flask_app
from flask import redirect, url_for, request, render_template
from flask_login import login_required, current_user
from app.presentation.view import base_multiple_items
from app.presentation.layout.utils import flash_plus
from app.application import socketio as msocketio, settings as msettings
import sys, json
import app.data.visitor
import app.application.visitor


@visitor.route('/visitor/visitor', methods=['POST', 'GET'])
@login_required
def show():
    # start = datetime.datetime.now()
    base_multiple_items.update(table_configuration)
    ret = base_multiple_items.show(table_configuration)
    # print('visitor.show', datetime.datetime.now() - start)
    return ret


@visitor.route('/visitor/table_ajax', methods=['GET', 'POST'])
@login_required
def table_ajax():
    # start = datetime.datetime.now()
    base_multiple_items.update(table_configuration)
    ret =  base_multiple_items.ajax(table_configuration)
    # print('visitor.table_ajax', datetime.datetime.now() - start)
    return ret


@visitor.route('/visitor/table_action', methods=['GET', 'POST'])
@visitor.route('/visitor/table_action/<string:action>', methods=['GET', 'POST'])
@visitor.route('/visitor/table_action/<string:action>/<string:ids>', methods=['GET', 'POST'])
@login_required
# @supervisor_required
def table_action(action, ids=None):
    if ids:
        ids = json.loads(ids)
    if action == 'edit':
        return item_edit(ids)
    if action == 'add':
        return item_add()
    if action == 'delete':
        return item_delete(ids)
    return redirect(url_for('visitor.show'))


@visitor.route('/visitor/get_form', methods=['POST', 'GET'])
@login_required
def get_form():
    try:
        common = {
            'post_data_endpoint': 'api.visitor_update',
            'submit_endpoint': 'visitor.show',
            'cancel_endpoint': 'visitor.show',
            'api_key': flask_app.config['API_KEY'],
        }
        if request.values['form'] == 'view':
            data = app.application.visitor.prepare_edit_form(request.values['extra'], read_only=True)
            data.update(common)
        elif current_user.is_at_least_supervisor:
            if request.values['form'] == 'edit':
                data = app.application.visitor.prepare_edit_form(request.values['extra'])
                data.update(common)
            elif request.values['form'] == 'add':
                data = app.application.visitor.prepare_add_form()
                data.update(common)
                data['post_data_endpoint'] ='api.visitor_add'
            else:
                return {"status": False, "data": f"get_form: niet gekende form: {request.values['form']}"}
        else:
            return {"status": False, "data": f"U hebt geen toegang tot deze url"}
        return {"status": True, "data": data}
    except Exception as e:
        log.error(f"Error in get_form: {e}")
        return {"status": False, "data": f"get_form: {e}"}


@supervisor_required
def item_delete(ids=None):
    try:
        if ids == None:
            ids = request.form.getlist('chbx')
        app.application.visitor.delete_visitors(ids)
    except Exception as e:
        log.error(f'could not delete visitor {request.args}: {e}')
    return redirect(url_for('visitor.show'))


@supervisor_required
def item_edit(ids=None):
    try:
        if ids == None:
            chbx_id_list = request.form.getlist('chbx')
            if chbx_id_list:
                ids = chbx_id_list[0]  # only the first one can be edited
            if ids == '':
                return redirect(url_for('visitor.show'))
        else:
            id = ids[0]
            data = {"form": "edit",
                "get_form_endpoint": "visitor.get_form",
                "extra": id,
                "buttons": ["save", "cancel"],
                'css': {'width': '50%', 'margin-left': 'auto', 'margin-right': 'auto'},
            }
        return render_template('badge/badge-visitor.html', data=data, visitors=app.application.visitor.get_visitors())
    except Exception as e:
        log.error(f'Could not edit guest {e}')
        flash_plus('Kan gebruiker niet aanpassen', e)
    return redirect(url_for('visitor.show'))


@supervisor_required
def item_add():
    try:
        data = {"form": "add",
                "get_form_endpoint": "visitor.get_form",
                "buttons": ["save", "cancel", "clear"],
                'css': {'width': '50%', 'margin-left': 'auto', 'margin-right': 'auto'},
                'visitors': app.application.visitor.get_visitors()
                }
        return render_template('badge/badge-visitor.html', data=data, visitors=app.application.visitor.get_visitors())
    except Exception as e:
        log.error(f'Could not add visitor {e}')
        flash_plus(f'Kan visitor niet toevoegen: {e}')
    return redirect(url_for('visitor.show'))


def get_filters():
    filters = []
    return filters


def get_show_gauges():
    return ''


def get_pdf_template():
    return msettings.get_pdf_template('visitor-pdf-template')


table_configuration = {
    'view': 'visitor',
    'title': 'Bezoekers',
    'buttons': ['edit', 'add', 'delete'],
    'delete_message': 'Opgelet!!<br>'
                      'Bent u zeker om deze bezoeker(s) te verwijderen?<br>'
                      'Eens verwijderd kunnen ze niet meer worden terug gehaald.<br>',
    'get_filters': get_filters,
    'get_show_info': get_show_gauges,
    'get_pdf_template': get_pdf_template,
    'item': {
        'edit': {'title': 'Wijzig een visitor', 'buttons': ['save', 'cancel']},
        'add': {'title': 'Voeg een visitor toe', 'buttons': ['save', 'cancel']},
    },
    'href': [],
    'pre_filter': app.data.visitor.pre_filter,
    'format_data': app.application.visitor.format_data,
    'filter_data': app.data.visitor.filter_data,
    'search_data': app.data.visitor.search_data,
    'default_order': (1, 'asc'),
    'socketio_endpoint': 'celledit-visitor',
    # 'cell_color': {'supress_cell_content': True, 'color_keys': {'X': 'red', 'O': 'green'}}, #TEST
    # 'suppress_dom': True,
}

