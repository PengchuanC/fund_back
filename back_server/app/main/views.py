import json
from flask import jsonify, make_response

from . import main
from ..models.classify import Classify
from . import util


@main.route('/', methods=['GET',  'POST'])
def index():
    return "HOME_PAGE"


@main.route("/summary", methods=["GET"])
def summary():
    """返回基金完整分类"""
    c = Classify.query.filter_by(update_date=util.lastday_of_lastmonth()).all()
    c = [x.to_dict() for x in c]
    date = c[0]['update_date']
    return make_response(jsonify({"date": date, "data": c}), 200)


@main.route("/test", methods=["GET", "POST"])
def test():
    c = Classify.query.filter_by(windcode="000001.OF").all()
    return c[0].classify
