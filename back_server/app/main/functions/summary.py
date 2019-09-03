from functools import lru_cache

from back_server.app.models.basic_info import BasicInfo as BI
from back_server.app.models.indicators_plot import IndicatorsForPlot, db
from back_server.app.models.classify import Classify


@lru_cache(20)
def latest_update_date():
    ifp = IndicatorsForPlot
    _latest_update_date = db.session.query(db.func.max(ifp.UPDATE_DATE)).one()[0]
    return _latest_update_date


def summary():
    """基金分类总结"""
    _latest_update_date = latest_update_date()
    total_count = db.session.query(db.func.count(db.func.distinct(Classify.windcode))).filter(
        Classify.update_date == _latest_update_date).one()
    total_count = total_count[0]
    branch = db.session.query(db.func.distinct(Classify.branch)).filter(
        Classify.update_date == _latest_update_date).all()
    branch = [x[0] for x in branch]

    open_fund = {"name": "公募基金", "value": total_count, "children": []}
    for bran in branch:
        bran_count = db.session.query(db.func.count(Classify.classify)).filter(Classify.branch == bran,
                                                                               Classify.update_date == _latest_update_date).one()
        bran_count = bran_count[0]
        classify = db.session.query(db.func.distinct(Classify.classify)).filter(Classify.branch == bran,
                                                                                Classify.update_date == _latest_update_date).all()
        classify = [x[0] for x in classify]
        branch_classify = {"name": bran, "value": bran_count, "children": []}
        for cla in classify:
            cla_count = db.session.query(db.func.count(Classify.windcode)).filter(
                Classify.branch == bran, Classify.classify == cla, Classify.update_date == _latest_update_date
            ).one()
            cla_count = cla_count[0]
            _classify = {"name": cla, "value": cla_count}
            branch_classify["children"].append(_classify)
        open_fund["children"].append(branch_classify)
    return open_fund
