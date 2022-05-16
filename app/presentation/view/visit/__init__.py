from flask import Blueprint

visit = Blueprint('visit', __name__)

from . import views
