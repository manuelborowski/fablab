import app
from app import log
from app.data import visitor as mvisitor
import app.data.settings
from app.application import formio as mformio
import sys, datetime, json

def add_visitor(data):
    try:
        if 'subscription_from' in data:
            data['subscription_from'] = app.datestring_to_date(data['subscription_from'])
        remove_badge_from_other_visitor(data)
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
            if 'subscription_from' in data:
                data['subscription_from'] = app.datestring_to_date(data['subscription_from'])
            remove_badge_from_other_visitor(data)
            visitor = mvisitor.update_visitor(visitor, data)
            if visitor:
                add_list, delete_list = update_visits(visitor.visits, data['visits'])
                if delete_list:
                    mvisitor.delete_visits(delete_list)
                for visit in add_list:
                    visit['time_in'] = app.datetimestring_to_datetime(visit['time_in'])
                    visit['time_out'] = app.datetimestring_to_datetime(visit['time_out'])
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


def add_visit(data):
    try:
        code = data['code']
        visitor = mvisitor.get_first_visitor({'badge_code': code})
        # visitor = Visitor.find_visitor_from_code(code)
        error_message = None
        ok_message = None
        if visitor:
            if visitor.is_active:
                direction = get_registration_direction(visitor)
                if visitor.is_subscriber:
                    delta = add_years(visitor.subscription_from, 1) - datetime.date.today()
                    if delta.days <= 0:
                        error_message = f'Opgelet {visitor.first_name}, uw abonnement is verlopen.<br>Vraag info aan een medewerker.'
                    else:
                        ok_message = f'<br>{visitor.first_name} uw abonnement is nog {delta.days} dagen geldig.'
                else:
                    if direction == 'in':
                        visitor.paygo_left -= 1
                    if visitor.paygo_left < 0:
                        error_message = f'Opgelet {visitor.first_name} , uw beurtenkaart is verlopen.<br>Vraag info aan een medewerker.'
                    else:
                        ok_message = f'<br>{visitor.first_name}, u heeft nog {visitor.paygo_left} beurten'
                        visitor.commit()

                if not error_message:
                    now = datetime.datetime.now().replace(microsecond=0)
                    if direction == 'in':
                        log.info(f'{code}: registration IN')
                        visit = mvisitor.add_visit({"visitor": visitor, "time_in": now})
                        # registration = Registration(visitor=visitor, time_in=now)
                        # db.session.add(registration)
                    else:
                        log.info(f'{code}: registration OUT')
                        visit = mvisitor.get_visits({"visitor": visitor}, order_by="!time_in", first=True)
                        visit.time_out = now
                        visit.commit()
                        # registration = Registration.find_last_registration_of_visitor(visitor)
                        # registration.time_out = now
                    # db.session.commit()
                    ok_message = f'Hallo {visitor.first_name}, u hebt juist ' \
                                 f'{"IN" if direction == "in" else "UIT"} gebadged om {now.strftime("%H:%M")}.<br>{ok_message}'
            else:
                error_message = f'Bezoeker {visitor.first_name} is niet meer actief'
        else:
            error_message = 'Sorry, dit is geen geldige badgecode'
        if error_message:
            log.info(f"visit: {error_message}")
            return {'status': False, 'data': error_message}
        else:
            log.info(f"visit: {ok_message}")
            return {'status': True, 'data': ok_message}
    except Exception as e:
        log.error(f'badge_entered gave error : {e}')
    return {'status': False, 'data': 'Sorry, er is iets fout gegaan tijdens het badgen'}


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


def get_visitors():
    out = []
    visitors =  mvisitor.get_visitors()
    out = [v.to_dict() for v in visitors]
    return out


############ visitor overview list #########
def format_data(db_list):
    out = []
    for visitor in db_list:
        em = visitor.to_dict()
        em.update({
            'row_action': visitor.id,
            'DT_RowId': visitor.id
        })
        if len(em['visits']) > 0:
            em.update({
                'visit_time_in': em['visits'][0]['time_in'] if em['visits'][0]['time_in'] else '',
                'visit_time_out': em['visits'][0]['time_out'] if em['visits'][0]['time_out'] else '',
            })
        else:
            em.update({
                'visit_time_in': '',
                'visit_time_out': '',
            })
        out.append(em)
    return out


############ visit overview list #########
def visit_format_data(db_list):
    out = []
    for visit in db_list:
        em = visit.to_dict()
        em.update({
            'row_action': visit.id,
            'DT_RowId': visit.id
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


def remove_badge_from_other_visitor(data):
    visitors = mvisitor.get_visitors({'badge_code': data['badge_code']})
    for visitor in visitors:
        visitor.badge_code = ''
        visitor.badge_number = ''
        visitor.deactivate()


def get_registration_direction(visitor):
    now = datetime.datetime.now().replace(microsecond=0)
    last_visit = mvisitor.get_visits({"visitor": visitor}, order_by="!time_in", first=True)
    # registration_last = Registration.find_last_registration_of_visitor(visitor)
    if not last_visit:
        # no registrations yet
        return 'in'
    elif last_visit.time_in.date() == now.date():
        # allready a registration on this day
        return 'out'
    return 'in'


def add_years(d, years):
    try:
        # Return same day as the current year, but 'years' later
        return d.replace(year=d.year + years)
    except ValueError:
        # If not same day, it will return other, i.e.  February 29 to March 1 etc.
        return d + (datetime.date(d.year + years, 1, 1) - datetime.date(d.year, 1, 1))


