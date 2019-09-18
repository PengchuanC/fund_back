from flask_restful import Api, Resource, marshal_with, fields, reqparse

from . import rest

from ...models.fundperformance import FundPerformance, db
from ...models.basic_info import BasicInfo

fs = Api(rest)

resource_fields = {
    "data": fields.List(fields.Nested({
        "id": fields.Integer,
        "windcode": fields.String,
        "indicator": fields.String,
        "numeric": fields.Float,
        "update_date": fields.String
    })),
    "sec_name": fields.String
}


@fs.resource("/fundinfo/<string:windcode>")
class Performance(Resource):

    def get(self, windcode):
        fp = FundPerformance
        sec_name = BasicInfo.query.with_entities(BasicInfo.sec_name).filter(BasicInfo.windcode == windcode).first()[0]
        max_update_date = db.session.query(db.func.max(fp.update_date)).filter(fp.windcode == windcode).one()[0]
        ret = fp.query.filter(fp.windcode == windcode).filter(fp.update_date == max_update_date).all()
        data = {"update_date": max_update_date.strftime("%Y-%m-%d"), "sec_name": sec_name}
        for r in ret:
            data[r.indicator] = r.numeric
        return data
