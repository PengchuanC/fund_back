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
    branch = Classify.query(Classify.branch).filter(Classify)
