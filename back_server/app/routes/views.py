import json

from flask import jsonify, make_response, request
from sqlalchemy import and_

from . import main
from ... import db
from ..models.classify import Classify
from ..models.basic_info import BasicInfo
from . import util
from .functions import for_plot, filters, summary as summarize


@main.route('/', methods=['GET', 'POST'])
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
    update_date = db.session.query(db.func.max(Classify.update_date)).one()[0]
    ret = db.session.query(
        Classify.classify, Classify.branch, BasicInfo.windcode, BasicInfo.sec_name, BasicInfo.fund_benchmark,
        BasicInfo.fund_setupdate
    ).join(BasicInfo, and_(Classify.windcode == BasicInfo.windcode, BasicInfo.type == "CSI")).filter(
        Classify.update_date == update_date).paginate(page, 25)
    page, per_page, total, items = util.zip_paginate(ret)
    ret = [{
        "classify": x.classify, "branch": x.branch, "windcode": x.windcode, "sec_name": x.sec_name,
        "benchmark": x.fund_benchmark, "setupdate": x.fund_setupdate.strftime("%Y-%m-%d")
    } for x in items]
    return make_response(jsonify({"data": ret, "page": page, "total": total, "per_page": per_page}), 200)


@main.route("/summary/bc", methods=["GET", "POST"])
def summary_branch_classify():
    bc = summarize.summary()
    return make_response(jsonify({"data": bc}), 200)


@main.route("/branch", methods=["GET", "POST"])
def branch_and_classify():
    branch, bc = for_plot.branch_and_classify()
    return make_response(jsonify({"data": bc, "branch": branch}), 200)


@main.route("/plot/exist", methods=["GET"])
def exists_years():
    classify = request.args.get("classify")
    data, mean, date = for_plot.plot_exits_years(classify)
    return make_response(jsonify({"data": data, "mean": mean, "classify": classify, "date": date}), 200)


@main.route("/plot/scale", methods=["GET"])
def fund_scale():
    classify = request.args.get("classify")
    data, date = for_plot.plot_scale(classify)
    return make_response(jsonify({"data": data, "classify": classify, "date": date}), 200)


@main.route("/plot/comp", methods=["GET"])
def company():
    classify = request.args.get("classify")
    data, date = for_plot.market_position(classify)
    return make_response(jsonify({"data": data, "classify": classify, "date": date}), 200)


@main.route("/plot/scale&year", methods=["GET"])
def scale_and_years():
    classify = request.args.get("classify")
    data, date = for_plot.scale_and_years(classify)
    return make_response(jsonify({"data": data, "classify": classify, "date": date}), 200)


@main.route("/plot", methods=["GET"])
def plot():
    classify = request.args.get("classify")
    exist_data, *_ = for_plot.plot_exits_years(classify)
    scale_data, date = for_plot.plot_scale(classify)
    comp, _ = for_plot.market_position(classify)
    sc_y, _ = for_plot.scale_and_years(classify)
    return make_response(jsonify({"data": {
        "exist": exist_data, "scale": scale_data, 'company': comp, "scale_year": sc_y
    }, "classify": classify, "date": date}), 200)


@main.route("/filter", methods=["POST"])
def funds_filter():
    data = request.get_data()
    data = json.loads(data)
    funds = filters.execute_basic_filter(data)
    if isinstance(funds, int):
        return make_response("invalid request", 400)
    return make_response({"data": list(funds)}, 200)


@main.route("/advance_filter", methods=["POST"])
def funds_advance_filter():
    data = request.get_data()
    data = json.loads(data)
    funds = data['funds']
    f = data["filter"]
    funds = filters.execute_advance_filter(funds, f)
    return make_response({"data": list(funds)}, 200)


@main.route("/filter/info", methods=["GET", "POST"])
def funds_filter_basic_info():
    data = json.loads(request.get_data())
    funds = data["funds"]
    page = data["page"]
    ret = filters.basic_info(funds, page)
    page, per_page, total, items = util.zip_paginate(ret)
    ret = [{
        "classify": x.classify, "branch": x.branch, "windcode": x.windcode, "sec_name": x.sec_name,
        "benchmark": x.fund_benchmark, "setupdate": x.fund_setupdate.strftime("%Y-%m-%d")
    } for x in items]
    return make_response(jsonify({"data": ret, "page": page, "total": total, "per_page": per_page}), 200)
