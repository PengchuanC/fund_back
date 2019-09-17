import json

from flask import make_response, jsonify, request

from ..news import news
from ...models.news import News, db
from .. import util


@news.route("/", methods=["GET"])
def index():
    return "news api"


@news.route("/breaking/<int:page>", methods=["GET", "POST"])
def breaking_news(page):
    """热点新闻"""
    ret = db.session.query(News).order_by(db.desc('savedate')).filter(News.keyword.is_(None)).paginate(page, 20)
    page, per_page, total, items = util.zip_paginate(ret)
    ret = [x.to_dict() for x in items]
    return make_response(jsonify({"data": ret, "page": page, "total": total, "per_page": per_page}), 200)


@news.route("/follow/keywords", methods=["GET", "POST"])
def followed_keywords():
    """获取关注的全部关键词"""
    ret = db.session.query(db.func.distinct(News.keyword)).all()
    keywords = [x[0] for x in ret if x[0] is not None]
    return make_response(jsonify({"data": keywords}), 200)


@news.route("/follow", methods=["POST"])
def followed_news():
    """关注的新闻，需要两个关键字获取
    :param page: 页码
    :param keyword: 关注的关键字
    """
    params = request.get_data()
    params = json.loads(params)
    page = params["page"]
    keyword = params["keyword"]
    ret = db.session.query(News).order_by(db.desc('savedate')).filter(News.keyword == keyword).paginate(page, 20)
    page, per_page, total, items = util.zip_paginate(ret)
    ret = [x.to_dict() for x in items]
    return make_response(jsonify({"data": ret, "page": page, "total": total, "per_page": per_page}), 200)
