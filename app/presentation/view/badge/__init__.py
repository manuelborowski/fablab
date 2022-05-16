from flask import Blueprint

badge = Blueprint('badge', __name__)

from . import views
