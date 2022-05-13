from app import flask_app, login_manager
from app.data.user import load_user as user_load_user


@flask_app.before_first_request
def at_start():
    pass
    # db_subject_topic.add_default_values_if_empty()
    # db_measure_topic.add_default_values_if_empty()

# Set up user_loader
@login_manager.user_loader
def load_user(user_id):
    return user_load_user(user_id)


__all__ = ['models', 'settings', 'user', 'utils', 'warning', 'student_care', 'student_intake', 'visitor']


import app.data.models
import app.data.settings
import app.data.student_care
import app.data.visitor
import app.data.student_intake
import app.data.warning
import app.data.utils
import app.data.user
