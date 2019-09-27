from flask import Blueprint
rest = Blueprint("rest", __name__)

from .newsviews import *
from .fundinfoviews import *
from .views import *
from .fundmanagerviews import *