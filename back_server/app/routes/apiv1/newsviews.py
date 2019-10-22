import datetime

from flask_restful import Api, Resource, marshal_with, fields, reqparse

from . import rest

from ...models.news import News, db
from .. import util


api = Api(rest)

resource_fields = {
    "data": fields.List(
        fields.Nested({
            "id": fields.Integer,
            "title": fields.String,
            "abstract": fields.String,
            "url": fields.String,
            "source": fields.String,
            "savedate": fields.String,
            "keyword": fields.String
        })
    ),
    "per_page": fields.Integer,
    "page": fields.Integer,
    "total": fields.Integer
}


@api.resource("/news/")
class IndexViews(Resource):
    def get(self):
        return {"data": "api version = v1"}


@api.resource("/news/breaking/<int:page>")
class BreakingViews(Resource):

    @marshal_with(resource_fields)
    def get(self, page):
        """热点新闻"""
        ret = News.query.order_by(db.desc('savedate')).filter(News.keyword.is_(None)).paginate(page, 20)
        page, per_page, total, items = util.zip_paginate(ret)
        resp = {"data": items, "page": page, "per_page": per_page, "total": total}
        return resp


@api.resource("/news/follow/keywords")
class FollowedKeywordsViews(Resource):

    def get(self):
        """获取关注的全部关键词"""
        ret = db.session.query(db.func.distinct(News.keyword)).all()
        keywords = [x[0] for x in ret if x[0] is not None]
        return {"data": keywords}


@api.resource("/news/follow")
class FollowedNewsViews(Resource):

    @marshal_with(resource_fields)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("keyword", type=str)
        parser.add_argument("page", type=int)
        args = parser.parse_args()
        keyword = args["keyword"]
        page = args["page"]
        ret = News.query.order_by(db.desc('savedate')).filter(News.keyword == keyword).paginate(page, 20)
        page, per_page, total, items = util.zip_paginate(ret)
        resp = {"data": items, "page": page, "per_page": per_page, "total": total}
        return resp


@api.resource("/newslist")
class NewsListViews(Resource):

    @marshal_with(resource_fields)
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("page", type=int)
        parser.add_argument("section", type=str)
        parser.add_argument("date", type=str)
        parser.add_argument("search", type=str)
        args = parser.parse_args()
        page = args["page"]
        date = args["date"]
        search = args["search"]
        section = args["section"]

        ret = News.query.order_by(News.savedate.desc(), News.title.desc())
        if date:
            date = datetime.datetime.strptime(date[0: 10], "%Y-%m-%d")
            date_2 = date + datetime.timedelta(days=1)
            ret = ret.filter(News.savedate.between(date, date_2))
        if search:
            ret = ret.filter(db.or_(News.title.like("%"+search+"%")), News.abstract.like("%"+search+"%"))
        if section and section != "whole":
            sections = {"economy": "宏观", "finance": "金融", "company": "商业", "japan": "日本"}
            if section in sections.keys():
                section = sections[section]
            ret = ret.filter(News.keyword == section)
        ret = ret.paginate(page, 25, False)
        _page, per_page, total, items = util.zip_paginate(ret)
        # items = sorted(items, key=lambda x: x.title)
        resp = {"data": items, "page": _page, "per_page": per_page, "total": total}
        return resp
