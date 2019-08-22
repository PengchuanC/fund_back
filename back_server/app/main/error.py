from flask import render_template
from . import main


@main.app_errorhandler(404)
def page_not_fund(e):
    return "page not fund"
