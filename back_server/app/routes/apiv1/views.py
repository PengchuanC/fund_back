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
            "savedate": fields.DateTime(dt_format='iso8601'),
            "keyword": fields.String
        })
    ),
    "per_page": fields.Integer,
    "page": fields.Integer,
    "total": fields.Integer
}


@api.resource("/")
class IndexViews(Resource):
    def get(self):
        return {"data": "api version = v1"}


@api.resource("/breaking/<int:page>")
class BreakingViews(Resource):

    @marshal_with(resource_fields)
    def get(self, page):
        """热点新闻"""
        ret = News.query.order_by(db.desc('savedate')).filter(News.keyword.is_(None)).paginate(page, 20)
        page, per_page, total, items = util.zip_paginate(ret)
        resp = {"data": items, "page": page, "per_page": per_page, "total": total}
        return resp


@api.resource("/follow/keywords")
class FollowedKeywordsViews(Resource):

    def get(self):
        """获取关注的全部关键词"""
        ret = db.session.query(db.func.distinct(News.keyword)).all()
        keywords = [x[0] for x in ret if x[0] is not None]
        return {"data": keywords}


@api.resource("/follow")
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
