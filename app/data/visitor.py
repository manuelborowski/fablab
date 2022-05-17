import sys

import app
from app import log, db
from app.data import utils as mutils
from sqlalchemy import text, desc
from sqlalchemy_serializer import SerializerMixin


class Visit(db.Model, SerializerMixin):
    __tablename__ = 'visits'

    date_format = '%d/%m/%Y'
    datetime_format = '%d/%m/%Y %H:%M'

    id = db.Column(db.Integer, primary_key=True)
    time_in = db.Column(db.DateTime())
    time_out = db.Column(db.DateTime())
    visitor_id = db.Column(db.Integer, db.ForeignKey('visitors.id'),  nullable=False)

    def commit(self):
        db.session.commit()


class Visitor(db.Model, SerializerMixin):
    __tablename__ = 'visitors'

    date_format = '%d/%m/%Y'
    datetime_format = '%d/%m/%Y %H:%M'
    serialize_rules = ('-visits.visitor',)

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(256), default='')
    last_name = db.Column(db.String(256), default='')
    subscription_type = db.Column(db.String(256), default='')
    subscription_from = db.Column(db.Date)
    paygo_max = db.Column(db.Integer)
    paygo_left = db.Column(db.Integer)
    email = db.Column(db.String(256), default='')
    phone = db.Column(db.String(256), default='')
    badge_code = db.Column(db.String(256), default='')
    badge_number = db.Column(db.String(256), default='')
    visits = db.relationship('Visit', cascade='all, delete-orphan', backref='visitor', lazy=True, order_by=(desc(Visit.time_in)))

    def commit(self):
        db.session.commit()

    @property
    def is_subscriber(self):
        return self.subscription_type == "jaarabonnement"

    @property
    def is_active(self):
        return self.subscription_type != 'niet-actief'

    def deactivate(self):
        self.subscription_type = "niet-actief"
        db.session.commit()


def add_visitor(data = {}):
    try:
        visitor = Visitor()
        for k, v in data.items():
            if hasattr(visitor, k):
                if getattr(Visitor, k).expression.type.python_type == type(v):
                    setattr(visitor, k, v.strip() if isinstance(v, str) else v)
        db.session.add(visitor)
        db.session.commit()
        return visitor
    except Exception as e:
        db.session.rollback()
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def update_visitor(visitor, data={}):
    try:
        for k, v in data.items():
            if hasattr(visitor, k):
                if getattr(Visitor, k).expression.type.python_type == type(v):
                    setattr(visitor, k, v.strip() if isinstance(v, str) else v)
        db.session.commit()
        return visitor
    except Exception as e:
        db.session.rollback()
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def delete_visitors(ids=None):
    try:
        for id in ids:
            visitor = get_first_visitor({"id": id})
            db.session.delete(visitor)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


# in data, when a key is prefixed with a '!', then the is not equal-to filter is used
def get_visitors(data={}, order_by=None, first=False, count=False):
    try:
        q = Visitor.query
        for k, v in data.items():
            not_equal = False
            if k[0] == '!':
                not_equal = True
                k = k[1::]
            if hasattr(Visitor, k):
                q = q.filter(getattr(Visitor, k) != v)  if not_equal else q.filter(getattr(Visitor, k) == v)
        if order_by:
            q = q.order_by(getattr(Visitor, order_by))
        if first:
            guest = q.first()
            return guest
        if count:
            return q.count()
        guests = q.all()
        return guests
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def get_first_visitor(data={}):
    try:
        user = get_visitors(data, first=True)
        return user
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


################# visits ####################
def add_visit(data = {}):
    try:
        visit = Visit()
        for k, v in data.items():
            if hasattr(visit, k):
                if getattr(Visit, k).expression.type.python_type == type(v) or isinstance(v, Visitor):
                    setattr(visit, k, v.strip() if isinstance(v, str) else v)
        db.session.add(visit)
        db.session.commit()
        return visit
    except Exception as e:
        db.session.rollback()
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None




def get_visits(data={}, special={}, order_by=None, first=False, count=False):
    try:
        q = Visit.query
        for k, v in data.items():
            if hasattr(Visit, k):
                q = q.filter(getattr(Visit, k) == v)
        if order_by:
            if order_by[0] == "!":
                q = q.order_by(desc(getattr(Visit, order_by[1::])))
            else:
                q = q.order_by(getattr(Visit, order_by))
        if first:
            visit = q.first()
            return visit
        if count:
            return q.count()
        visits = q.all()
        return visits
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def get_first_visit(data={}):
    try:
        visit = get_visits(data, first=True)
        return visit
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def delete_visits(visits=None):
    try:
        if len(visits) > 0 and isinstance(visits[0], Visit):
            for visit in visits:
                db.session.delete(visit)
        else:
            for id in visits:
                visit = get_first_visitor({"id": id})
                db.session.delete(visit)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


############ visitor overview list #########
def pre_filter():
    return db.session.query(Visitor)


def filter_data(query, filter):
    for f in filter:
        if f['name']  == 'filter_badge_code' and f['value'] != '':
            _, is_valid, code = mutils.check_and_process_badge_code(f['value'])
            if is_valid:
                query = query.filter(Visitor.badge_code == code)
    return query


def search_data(search_string):
    search_constraints = []
    search_constraints.append(Visitor.first_name.like(search_string))
    search_constraints.append(Visitor.last_name.like(search_string))
    search_constraints.append(Visitor.subscription_type.like(search_string))
    return search_constraints


############ visits overview list #########
def visit_pre_filter():
    return db.session.query(Visit).join(Visitor)


def visit_filter_data(query, filter):
    if filter and 'name' in filter[0] and filter[0]['name'] == 'filter_date' and filter[0]['value'] != '':
        try:
            start_date = app.datetimestring_to_datetime(f"{filter[0]['value']} 00:00")
            end_date = app.datetimestring_to_datetime(f"{filter[0]['value']} 23:59")
            query = query.filter(Visit.time_in > start_date).filter(Visit.time_in < end_date)
            query = query.filter(Visit.time_out > start_date).filter(Visit.time_out < end_date)
        except:
            pass    #probably wrong format
    return query


def visit_search_data(search_string):
    search_constraints = []
    search_constraints.append(Visitor.first_name.like(search_string))
    search_constraints.append(Visitor.last_name.like(search_string))
    return search_constraints

