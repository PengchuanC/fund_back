from datetime import timedelta
from functools import lru_cache
from math import floor

from sqlalchemy import and_

from back_server import cache
from ...models.indicators import Indicators, db
from ...models.basic_info import BasicInfo
from ...models.classify import Classify


@lru_cache(20)
def latest_day_in_basic_info():
    latest = db.session.query(db.func.max(BasicInfo.update_date)).first()[0]
    return latest


@lru_cache(20)
def latest_day_in_indicators():
    latest = db.session.query(db.func.max(Indicators.update_date)).first()[0]
    return latest


@lru_cache(20)
def latest_day_in_classify():
    latest = db.session.query(db.func.max(Classify.update_date)).first()[0]
    return latest


@cache.cached()
def funds_by_classify(cls: list):
    """获取特定分类下的全部基金"""
    c = Classify
    latest = latest_day_in_classify()
    funds = db.session.query(c.windcode).filter(c.classify.in_(cls), c.update_date == latest).all()
    funds = {x[0] for x in funds}
    return funds


@cache.cached()
def lever(funds, yes_or_no):
    """是否是杠杆基金"""
    BI = BasicInfo
    funds = db.session.query(BI.windcode, BI.fund_structuredfundornot).filter(BI.windcode.in_(funds)).all()
    funds = {x[0] for x in funds if x[1] == yes_or_no}
    return funds


@cache.cached()
def fund_years(funds, left, right=50):
    """基金存续时间位于[left, right]"""
    c = Classify
    latest = latest_day_in_classify()
    left = latest - timedelta(left*365)
    right = latest - timedelta(right * 365)
    funds = db.session.query(c.windcode).filter(c.fund_setupdate.between(right, left), c.windcode.in_(funds)).all()
    funds = set([x[0] for x in funds])
    return funds


@cache.cached()
def net_asset(funds, recent_asset_level, avg_asset_level):
    """对最新一期季报和年报的基金净值规模作出要求"""
    ins = Indicators
    rpt = db.session.query(db.func.distinct(ins.rpt_date)).order_by(db.desc(ins.rpt_date)).all()
    rpt = [x[0] for x in rpt]
    recent = rpt[0]
    annual = [x for x in rpt if x.month == 12][0]
    funds = db.session.query(ins.windcode).filter(
        ins.windcode.in_(funds), ins.rpt_date == recent, ins.indicator == "NETASSET_TOTAL",
        ins.numeric >= recent_asset_level*1e8
    ).all()
    funds = {x[0] for x in funds}
    funds = db.session.query(ins.windcode).filter(
        ins.windcode.in_(funds), ins.rpt_date == annual, ins.indicator == "PRT_AVGNETASSET",
        ins.numeric >= avg_asset_level*1e8
    ).all()
    funds = {x[0] for x in funds}
    return funds


@cache.cached()
def single_hold_shares(funds, percent: int = 40):
    """单一投资者持仓比例限制，默认低于40%"""
    ins = Indicators
    latest = latest_day_in_indicators()
    funds = db.session.query(ins.windcode, db.func.ifnull(ins.numeric, 0)).filter(
        ins.update_date == latest, ins.indicator == "HOLDER_SINGLE_TOTALHOLDINGPCT", ins.windcode.in_(funds)
    ).all()
    funds = {x[0] for x in funds if x[1] < percent}
    return funds


@cache.cached()
def over_index_return(funds, index_code, year):
    """区间收益超过指定的指数的区间收益"""
    ins = Indicators
    latest = latest_day_in_indicators()
    funds = db.session.query(ins.windcode, db.func.ifnull(ins.numeric, 0)).filter(
        ins.update_date == latest, ins.indicator == "RETURN", ins.windcode.in_(funds)
    ).all()
    index = db.session.query(ins.windcode, db.func.ifnull(ins.numeric, 0)).filter(
        ins.update_date == latest, ins.indicator == "RETURN", ins.windcode == index_code,
        ins.note == str(year)
    ).first()
    funds = {x[0] for x in funds if x[1] > index[1]}
    return funds


@cache.cached()
def over_bench_return(funds, year):
    """区间收益超过基准"""
    ins = Indicators
    latest = latest_day_in_indicators()
    funds = db.session.query(ins.windcode, db.func.ifnull(ins.numeric, 0)).filter(
        ins.update_date == latest, ins.indicator == "NAV_OVER_BENCH_RETURN_PER", ins.note == str(year),
        ins.windcode.in_(funds)
    ).all()
    funds = {x[0] for x in funds if x[1] > 0}
    return funds


@cache.cached()
def month_win_ratio(funds, year, ratio=0.5):
    """月度胜率"""
    ins = Indicators
    latest = latest_day_in_indicators()
    funds = db.session.query(ins.windcode, db.func.ifnull(ins.text, "0/0")).filter(
        ins.update_date == latest, ins.indicator == "ABSOLUTE_UPDOWNMONTHRATIO", ins.note == str(year),
        ins.windcode.in_(funds)
    ).all()
    funds = {x[0] for x in funds if int(x[1].split("/")[0])/int(x[1].split("/")[0]) > ratio}
    return funds


@cache.cached()
def max_downside_over_average(funds, year, ratio=None):
    """最大回撤优于平均"""
    ins = Indicators
    latest = latest_day_in_indicators()
    funds = db.session.query(ins.windcode, db.func.ifnull(ins.numeric, 0)).filter(
        ins.update_date == latest, ins.indicator == "RISK_MAXDOWNSIDE", ins.note == str(year),
        ins.windcode.in_(funds)
    ).all()
    if str(ratio) == "平均":
        mmd = [x[1] for x in funds]
        mean = sum(mmd) / len(mmd)
        funds = {x[0] for x in funds if x[1] > mean}
    else:
        funds = {x[0] for x in funds if x[1] > -ratio}
    return funds


@cache.cached()
def corp_scale_level(funds, level):
    """基金公司规模大于？分位"""
    ins = Indicators
    latest_c = latest_day_in_classify()
    latest_i = latest_day_in_indicators()
    all_funds = db.session.execute(
        f'SELECT a.windcode, a.text, IFNULL(b.numeric, 0) FROM indicators a JOIN indicators b ON a.windcode = b.windcode JOIN fund_classify c ON a.windcode = c.windcode where a.update_date = "{latest_i}" and c.UPDATE_DATE = "{latest_c}" and a.indicator = "FUND_CORP_FUNDMANAGEMENTCOMPANY" AND b.indicator = "FUND_FUNDSCALE"; '
    ).fetchall()
    corps = {x[1] for x in all_funds}
    corps = {x: 0 for x in corps}
    for x in all_funds:
        corps[x[1]] += x[2]
    corps = list(zip(corps.items()))
    corps = [x[0] for x in corps]
    corps = sorted(corps, key=lambda x: x[1], reverse=True)
    corps = corps[: floor(len(corps)*level)]
    corps = {x[0] for x in corps}
    funds = db.session.query(ins.windcode, ins.text).filter(
        ins.indicator == "FUND_CORP_FUNDMANAGEMENTCOMPANY", ins.windcode.in_(funds)
    ).all()
    funds = {x[0] for x in funds if x[1] in corps}
    return funds


@cache.cached()
def manager_working_years(funds, year):
    """基金经历工作年满？年"""
    ins = Indicators
    latest = latest_day_in_indicators()
    funds = db.session.query(ins.windcode, db.func.ifnull(ins.numeric, 0)).filter(
        ins.update_date == latest, ins.indicator == "FUND_MANAGER_MANAGERWORKINGYEARS",
        ins.windcode.in_(funds)
    ).all()
    funds = {x[0] for x in funds if x[1] >= year}
    return funds


@cache.cached()
def manager_working_years_on_this_fund(funds, year):
    """基金经历在本基金任职年限超过？年"""
    ins = Indicators
    latest = latest_day_in_indicators()
    funds = db.session.query(ins.windcode, db.func.ifnull(ins.numeric, 0)/365).filter(
        ins.update_date == latest, ins.indicator == "FUND_MANAGER_ONTHEPOSTDAYS",
        ins.windcode.in_(funds)
    ).all()
    funds = {x[0] for x in funds if x[1] >= year}
    return funds


@cache.cached()
def manager_geometry_return(funds, annual_return):
    """基金经历年化回报"""
    ins = Indicators
    latest = latest_day_in_indicators()
    funds = db.session.query(ins.windcode, db.func.ifnull(ins.numeric, 0)).filter(
        ins.update_date == latest, ins.indicator == "FUND_MANAGER_GEOMETRICANNUALIZEDYIELD",
        ins.windcode.in_(funds)
    ).all()
    funds = {x[0] for x in funds if x[1] >= annual_return}
    return funds


@cache.cached()
def manager_return_on_this_fund(funds, annual_return):
    """任职本基金年化回报"""
    ins = Indicators
    latest = latest_day_in_indicators()
    funds = db.session.query(ins.windcode, db.func.ifnull(ins.numeric, 0)).filter(
        ins.update_date == latest, ins.indicator == "NAV_PERIODICANNUALIZEDRETURN",
        ins.windcode.in_(funds)
    ).all()
    funds = {x[0] for x in funds if x[1] >= annual_return}
    return funds


@cache.cached()
def wind_rating(funds, rating=3):
    """Wind评级超过？星，默认大于等于3星"""
    ins = Indicators
    latest = latest_day_in_indicators()
    funds = db.session.query(ins.windcode, db.func.ifnull(ins.numeric, 0)).filter(
        ins.update_date == latest, ins.indicator == "RATING_WIND3Y",
        ins.windcode.in_(funds)
    ).all()
    funds = {x[0] for x in funds if x[1] >= rating}
    return funds


@cache.cached()
def recent_years_over_others(funds, year, level):
    """最近X年收益均超过？%分位"""
    f = funds
    ins = Indicators
    latest = latest_day_in_indicators()
    funds = db.session.query(ins.windcode, db.func.ifnull(ins.numeric, 0)).filter(
        ins.update_date == latest, ins.indicator == "RETURN", ins.note == str(year)
    ).all()
    funds = [(x[0], x[1]) for x in funds]
    funds = sorted(funds, key=lambda x: x[1], reverse=True)
    funds = funds[: floor(len(funds)*level)]
    funds = {x[0] for x in funds}
    funds = {x for x in f if x in funds}
    return funds


def execute_basic_filter(data):
    """执行简单的筛选规则，传入参数为前端POST请求参数"""
    if data["classify"]:
        funds = funds_by_classify(data['classify'])
    else:
        return -1
    if data["lever"]:
        funds = lever(funds, data["lever"])
    if data["existYear"]:
        funds = fund_years(funds, data["existYear"])
    if data["netValue"]:
        funds = net_asset(funds, data["netValue"], data["netValue"])
    if data["singleHolder"]:
        funds = single_hold_shares(funds, data["singleHolder"])
    if data["overIndex"]:
        funds = over_index_return(funds, data["overIndex"], data["existYear"])
    if data["overBench"] == "是":
        funds = over_bench_return(funds, data["existYear"])
    if data["monthWin"]:
        funds = month_win_ratio(funds, data["existYear"], data["monthWin"])
    if data["maxDownside"]:
        funds = max_downside_over_average(funds, data["existYear"], data["maxDownside"])
    return funds


def execute_advance_filter(funds, f):
    """执行高级筛选功能，需要筛选规则f"""
    if f["overCorps"]:
        funds = corp_scale_level(funds, f["overCorps"])
    if f["workYear"]:
        funds = manager_working_years(funds, f["workYear"])
    if f["workOnThis"]:
        funds = manager_return_on_this_fund(funds, f["workOnThis"])
    if f["geoReturn"]:
        funds = manager_geometry_return(funds, f["geoReturn"]*100)
    if f["thisReturn"]:
        funds = manager_return_on_this_fund(funds, f["thisReturn"]*100)
    if f["windRating"]:
        funds = wind_rating(funds, f["windRating"])
    if f["recentLevel"]:
        levels = f["recentLevel"]
        for level in levels:
            level = level[1: -1]
            year, level = level.split(", ")
            level = level.split("/")
            funds = recent_years_over_others(funds, int(year), float(level[0])/float(level[1]))
    return funds


def basic_info(funds, page):
    """获取基金基础信息"""
    update_date = db.session.query(db.func.max(Classify.update_date)).one()[0]
    ret = db.session.query(
        Classify.classify, Classify.branch, BasicInfo.windcode, BasicInfo.sec_name, BasicInfo.fund_benchmark,
        BasicInfo.fund_setupdate
    ).join(BasicInfo, and_(Classify.windcode == BasicInfo.windcode, BasicInfo.type == "CSI")).filter(
        Classify.update_date == update_date, BasicInfo.windcode.in_(funds)).paginate(page, 25)
    return ret
