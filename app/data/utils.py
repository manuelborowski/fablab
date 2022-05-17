import datetime

from sqlalchemy import desc

from app import flask_app, log, data, db
from app.data import models as mmodels


def datetime_to_dutch_datetime_string(date, include_seconds=False):
    return mmodels.datetime_to_dutch_datetime_string(date, include_seconds=include_seconds)


def raise_error(message, details=None):
    error = Exception(f'm({message}), d({details}), td({type(details).__name__})')
    raise error


# standardized way to make a key from strings: sort alphabetically and concatenate
def make_key(item_list):
    return make_list(item_list, seperator=',')

def extend_key(item1, item2=None):
    if isinstance(item1, list):
        return ','.join(item1)
    return ','.join([item1, item2])


# standardized way to concatenate strings: sort alphabetically and concatenate; seperated by comma
def make_list(item_list, seperator=', '):
    return seperator.join(sorted(item_list))


def check_and_process_badge_code(code):
    def process_int_code(code):
        if int(code) < 100000:
            # Assumed a student code because it is less then 100.000
            return False, code
        # convert int to hex, add leading 0's (if required) to get 8 characters.
        # revert the order of the 4 tupples (big vs little endian)
        h = '{:0>8}'.format(hex(int(code)).split('x')[-1].upper())
        code = h[6:8] + h[4:6] + h[2:4] + h[0:2]
        return True, code

    def decode_caps_lock(code):
        out = u''
        dd = {u'&': '1', u'É': '2', u'"': '3', u'\'': '4', u'(': '5', u'§': '6', u'È': '7', u'!': '8', u'Ç': '9',
              u'À': '0', u'A': 'A', u'B': 'B', u'C': 'C', u'D': 'D', u'E': 'E', u'F': 'F'}
        for i in code:
            out += dd[i.upper()]
        return out

    is_rfid_code = True
    is_valid_code = True
    code = code.upper()

    if len(code) == 8:
        # Assumed a HEX code of 8 characters
        if 'Q' in code:
            # This is a HEX code, with the Q iso A
            code = code.replace('Q', 'A')
        try:
            # Code is ok
            int(code, 16)
        except:
            try:
                # decode because of strange characters (CAPS LOCK)
                code = decode_caps_lock(code)
                int(code, 16)
            except:
                # It shoulde be a HEX code but it is not valid
                is_valid_code = False
    else:
        # Assumed an INT code
        try:
            # code is ok
            int(code)
            is_rfid_code, code = process_int_code(code)
        except:
            try:
                # decode because of strange characters (CAPS LOCK)
                code = decode_caps_lock(code)
                # code is ok
                int(code)
                is_rfid_code, code = process_int_code(code)
            except:
                # It should be an INT code but it is not valid
                is_valid_code = False

    return is_valid_code, is_rfid_code, code



