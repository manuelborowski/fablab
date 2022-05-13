import sys
from app import log, db
from sqlalchemy import text
from sqlalchemy_serializer import SerializerMixin


class Visit(db.Model, SerializerMixin):
    __tablename__ = 'visits'

    date_format = '%d/%m/%Y'
    datetime_format = '%d/%m/%Y %H:%M'

    id = db.Column(db.Integer, primary_key=True)
    time_in = db.Column(db.DateTime())
    time_out = db.Column(db.DateTime())
    visitor_id = db.Column(db.Integer, db.ForeignKey('visitors.id'),  nullable=False)


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
    visits = db.relationship('Visit', cascade='all, delete-orphan', backref='visitor', lazy=True, order_by=(Visit.time_in))


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


def get_visitors(data={}, special={}, order_by=None, first=False, count=False):
    try:
        q = Visitor.query
        for k, v in data.items():
            if hasattr(Visitor, k):
                q = q.filter(getattr(Visitor, k) == v)
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
    if filter and 'type' in filter[0] and filter[0]['type'] == 'checkbox':
        for cb in filter[0]['value']:
            query = query.filter(text(cb['id']), cb['checked'])
    for f in filter:
        if f['type'] == 'select' and f['value'] != 'none':
            query = query.filter(getattr(Visitor, f['name']) == (f['value'] == 'True'))
    return query


def search_data(search_string):
    search_constraints = []
    search_constraints.append(Visitor.s_first_name.like(search_string))
    search_constraints.append(Visitor.s_last_name.like(search_string))
    return search_constraints

