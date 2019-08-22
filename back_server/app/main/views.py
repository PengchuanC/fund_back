from flask import jsonify, make_response
from sqlalchemy import and_

from . import main
from ... import db
from ..models.classify import Classify
from ..models.basic_info import BasicInfo
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


@main.route("/summary/info")
def summary_info():
    ret = db.session.query(
        Classify.classify, Classify.branch, BasicInfo.windcode, BasicInfo.sec_name, BasicInfo.fund_setupdate
    ).join(BasicInfo, and_(Classify.windcode == BasicInfo.windcode, BasicInfo.type == "CSI")).all()
    ret = [{
        "classify": x.classify, "branch": x.branch, "windcode": x.windcode, "sec_name": x.sec_name,
        "setupdate": x.fund_setupdate
    } for x in ret]
    return make_response(jsonify({"data": ret}), 200)


@main.route("/test", methods=["GET", "POST"])
def test():
    c = BasicInfo.query.filter_by(type="CSI").first()
    print(c.__dict__)
    print(c.to_dict())
    return c.windcode
