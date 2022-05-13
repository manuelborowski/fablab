from app import log
from app.data import visitor as mvisitor
import app.data.settings
from app.application import formio as mformio
import sys, datetime

def add_visitor(data):
    try:
        data['subscription_from'] = mformio.datestring_to_date(data['subscription_from'])
        visitor = mvisitor.add_visitor(data)
        log.info(f"Add visitor: {visitor.last_name} {visitor.first_name}, {data}")
        return {"status": True, "data": {'id': visitor.id}}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        log.error(data)
        return {"status": False, "data": f'generic error {e}'}


def update_visitor(data):
    try:
        visitor = mvisitor.get_first_visitor({'id': data['id']})
        if visitor:
            del data['id']
            data['subscription_from'] = mformio.datestring_to_date(data['subscription_from'])
            visitor = mvisitor.update_visitor(visitor, data)
            if visitor:
                add_list, delete_list = update_visits(visitor.visits, data['visits'])
                if delete_list:
                    mvisitor.delete_visits(delete_list)
                for visit in add_list:
                    visit['time_in'] = mformio.datetimestring_to_datetime(visit['time_in'])
                    visit['time_out'] = mformio.datetimestring_to_datetime(visit['time_out'])
                    visit['visitor'] = visitor
                    mvisitor.add_visit(visit)
                log.info(f"Update visitor: {visitor.last_name} {visitor.first_name}, {data}")
                return {"status": True, "data": {'id': visitor.id}}
        return {"status": False, "data": "Er is iets fout gegaan"}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        log.error(data)
        return {"status": False, "data": f'generic error {e}'}


def delete_visitors(ids):
    mvisitor.delete_visitors(ids)


############## formio forms #############
def prepare_add_form():
    try:
        template = app.data.settings.get_json_template('visitor-formio-template')
        now = datetime.datetime.now()
        return {'template': template,
                'defaults': {'subscription_from': mformio.date_to_datestring(now)}}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        raise e


def prepare_edit_form(id):
    try:
        visitor = mvisitor.get_first_visitor({"id": id})
        template = app.data.settings.get_json_template('visitor-formio-template')
        template = mformio.prepare_for_edit(template, visitor.to_dict())
        return {'template': template,
                'defaults': visitor.to_dict()}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        raise e


############ care overview list #########
def format_data(db_list):
    out = []
    for visitor in db_list:
        em = visitor.to_dict()
        em.update({
            'row_action': visitor.id,
            'DT_RowId': visitor.id
        })
        out.append(em)
    return out

############ helpers ###################

# compare the new visits with the current one.  If a new visit is already present in the current ones, ignore it (unchanged)
# if there are unmathed, current visits -> delete them
# if there are unmatched, new visits -> store them
def update_visits(current, new):
    to_add = []
    to_delete = []
    current_cache = [mformio.datetime_to_datetimestring(c.time_in) + mformio.datetime_to_datetimestring(c.time_out) for c in current]
    nbr_current_cache = len(current_cache)
    new_cache = [n['time_in'] + n['time_out'] for n in new]
    nbr_new_cache = len(new_cache)

    if nbr_current_cache > 0:   #check for unchanged values
        for k in new_cache:
            if k in current_cache:
                current_cache[current_cache.index(k)] = -1
                new_cache[new_cache.index(k)] = -1
                nbr_new_cache -= 1
                nbr_current_cache -= 1
    idx_new_cache = idx_current_cache = 0
    while nbr_new_cache > 0:    #new values, add new objects
        if new_cache[idx_new_cache] != -1:
            to_add.append(new[idx_new_cache])
            nbr_new_cache -= 1
        idx_new_cache += 1
    while nbr_current_cache > 0:    #current, obsolete objects, add to delete list
        if current_cache[idx_current_cache] != -1:
            to_delete.append(current[idx_current_cache])
            nbr_current_cache -= 1
        idx_current_cache += 1
    return to_add, to_delete





