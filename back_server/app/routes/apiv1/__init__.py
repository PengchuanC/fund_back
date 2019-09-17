from flask import Blueprint
rest = Blueprint("rest", __name__)

from .views import *
