import datetime
import calendar


def lastday_of_lastmonth():
    """如果今天是本月最后一天，返回今天，如果今天不是本月最后一天，返回上月最后一天"""
    today = datetime.datetime.today()
    today_day = today.day
    today_month = today.month
    today_year = today.year
    dates = calendar.monthrange(today_year, today_month)
    if today_day == dates[-1]:
        return today
    elif today_day != dates[-1] and today_month != 1:
        dates = calendar.monthrange(today_year, today_month-1)
        return datetime.date(today_year, today_month-1, dates[-1])
    else:
        return datetime.date(today_year-1, 12, 31)


def zip_paginate(p):
    items = p.items
    total = p.total
    page = p.page
    return page, total, items
