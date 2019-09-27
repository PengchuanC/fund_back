from functools import lru_cache
from collections import OrderedDict

from pandas import cut
from math import ceil

from back_server.app.models.basic_info import BasicInfo as BI
from back_server.app.models.indicators_plot import IndicatorsForPlot, db
from back_server.app.models.classify import Classify


@lru_cache(20)
def latest_update_date():
    ifp = IndicatorsForPlot
    _latest_update_date = db.session.query(db.func.max(ifp.UPDATE_DATE)).one()[0]
    return _latest_update_date


@lru_cache(20)
def query_funds_by_classify(classify):
    ifp = IndicatorsForPlot
    _latest_update_date = latest_update_date()
    funds = db.session.query(Classify.windcode).filter(Classify.classify == classify,
                                                       Classify.update_date == _latest_update_date).all()
    funds = [x[0] for x in funds]
    return funds


def branch_and_classify():
    """获取公募基金分类"""
    _latest_update_date = db.session.query(db.func.max(Classify.update_date)).one()[0]
    classify = Classify.query.with_entities(Classify.branch, Classify.classify).filter_by(
        update_date=_latest_update_date).distinct().all()
    branch = list(set([x[0] for x in classify]))
    bc = {x: [] for x in branch}
    for c in classify:
        bc[c[0]].append(c[1])
    return branch, bc


def plot_exits_years(classify):
    """准备画图数据-基金存续年限分布"""
    ifp = IndicatorsForPlot
    _latest_update_date = latest_update_date()
    funds = query_funds_by_classify(classify)
    data = ifp.query.with_entities(ifp.FUND_SETUPDATE).filter(
        ifp.UPDATE_DATE == _latest_update_date, ifp.WINDCODE.in_(funds)).all()
    data = [x[0] for x in data]
    years = [(_latest_update_date - x).days / 365 for x in data]
    mean = sum(years) / len(years)
    _max = max(years)
    years = cut(years, bins=range(0, ceil(_max)), labels=range(0, ceil(_max) - 1))
    years = (years.value_counts() / len(years)).to_dict()
    years = [{"存续年限": x, "频率分布": y} for x, y in years.items() if y != 0]
    years = sorted(years, key=lambda x: x['存续年限'])
    return years, mean, _latest_update_date.strftime("%Y-%m-%d")


def plot_scale(classify):
    """准备画图数据-基金规模分布"""
    ifp = IndicatorsForPlot
    _latest_update_date = latest_update_date()
    funds = query_funds_by_classify(classify)
    data = ifp.query.with_entities(ifp.PRT_NETASSET).filter(
        ifp.UPDATE_DATE == _latest_update_date, ifp.WINDCODE.in_(funds)).all()
    data = [x[0] / (10 ** 8) for x in data if x[0]]
    _max = max(data)
    count = len(data)
    # 将x轴20等分
    data = cut(data, bins=range(0, ceil(_max / 20) * 20 - ceil(_max / 20), ceil(_max / 20)))
    data = (data.value_counts() / count).to_dict()
    data = [{"规模分布": (int(x.left), int(x.right)), "频率分布": y} for x, y in data.items() if y]
    return data, _latest_update_date.strftime("%Y-%m-%d")


def market_position(classify):
    """基金公司管理规模"""
    ifp = IndicatorsForPlot
    _latest_update_date = latest_update_date()
    funds = query_funds_by_classify(classify)
    data = ifp.query.with_entities(ifp.PRT_NETASSET, ifp.FUND_CORP_FUNDMANAGEMENTCOMPANY).filter(
        ifp.UPDATE_DATE == _latest_update_date, ifp.WINDCODE.in_(funds)).all()
    data = [x for x in data if x[0]]
    company = list(set([x[1] for x in data]))
    company = {x: 0 for x in company}
    for x in data:
        company[x[1]] += x[0] / (10 ** 8)
    company = [{"基金公司": x, "基金资产": y} for x, y in company.items()]
    company = sorted(company, key=lambda x: x['基金资产'], reverse=True)
    cumsum = sum(x['基金资产'] for x in company)
    cum = 0
    for i in range(0, len(company)):
        cum += company[i]['基金资产']
        company[i]['占比'] = cum / cumsum
    return company, _latest_update_date


def scale_and_years(classify):
    """基金存续年限和规模散点图"""
    ifp = IndicatorsForPlot
    _latest_update_date = latest_update_date()
    funds = query_funds_by_classify(classify)
    data = db.session.query(BI.sec_name, ifp.PRT_NETASSET, ifp.FUND_SETUPDATE).join(ifp,
                                                                                    BI.windcode == ifp.WINDCODE).join(
        Classify, BI.windcode == Classify.windcode).filter(ifp.WINDCODE.in_(funds), BI.type == "CSI",
                                                           Classify.classify == classify,
                                                           ifp.UPDATE_DATE == _latest_update_date).all()
    data = [
        {"基金简称": x[0], "基金规模": round(x[1] / (10 ** 8), 2), "存续时间": round((_latest_update_date - x[2]).days / 365, 2)}
        for x in data if
        x[0] if all({x[1], x[2]})]
    data = sorted(data, key=lambda x: x["存续时间"])
    data = [{"基金简称": x["基金简称"], "存续时间": x["存续时间"], "基金规模": x["基金规模"], "近似年限": int(x["存续时间"])} for x in data]
    return data, _latest_update_date
