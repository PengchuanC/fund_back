from flask import jsonify, make_response
from sqlalchemy import and_

from . import main
from ... import db
from ..models.classify import Classify
from ..models.basic_info import BasicInfo
from ..models.news import Toutiao
from . import util


@main.route('/', methods=['GET',  'POST'])
def index():
    return "HOME_PAGE"


@main.route("/summary/<int:page>", methods=["GET"])
def summary(page):
    """返回基金完整分类"""
    c = Classify.query.filter_by(update_date=util.lastday_of_lastmonth()).paginate(page, 25, False)
    db.session.close()
    page, per_page, total, items = util.zip_paginate(c)
    c = [x.to_dict() for x in items]
    date = c[0]['update_date']
    return make_response(jsonify({"date": date, "data": c, 'page': page, "total": total, "per_page": per_page}), 200)


@main.route("/summary/info/<int:page>")
def summary_info(page):
    ret = db.session.query(
        Classify.classify, Classify.branch, BasicInfo.windcode, BasicInfo.sec_name, BasicInfo.fund_benchmark, BasicInfo.fund_setupdate
    ).join(BasicInfo, and_(Classify.windcode == BasicInfo.windcode, BasicInfo.type == "CSI")).paginate(page, 25)
    page, per_page, total, items = util.zip_paginate(ret)
    ret = [{
        "classify": x.classify, "branch": x.branch, "windcode": x.windcode, "sec_name": x.sec_name,
        "benchmark": x.fund_benchmark, "setupdate": x.fund_setupdate.strftime("%Y-%m-%d")
    } for x in items]
    return make_response(jsonify({"data": ret, "page": page, "total": total, "per_page": per_page}), 200)


@main.route("/news/<int:page>", methods=['GET'])
def news(page):
    ret = db.session.query(Toutiao).order_by(db.desc('savedate')).paginate(page, 10)
    page, per_page, total, items = util.zip_paginate(ret)
    ret = [x.to_dict() for x in items]
    return make_response(jsonify({"data": ret, "page": page, "total": total, "per_page": per_page}), 200)


@main.route("/test/<int:pages>", methods=["GET", "POST"])
def test(pages):
    from .functions import toutiao_api
    data = toutiao_api.news_format(pages)
    return make_response(jsonify({"data": data, "pages": pages}), 200)
