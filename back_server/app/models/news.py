
from back_server import db
from .util import ModelToDict


class Toutiao(db.Model, ModelToDict):
    __tablename__ = 'finance_news'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False, unique=True, index=True)
    abstract = db.Column(db.TEXT)
    url = db.Column(db.TEXT)
    source = db.Column(db.String(20))
    savedate = db.Column(db.DateTime)

    def __repr__(self):
        return f"<Toutiao {self.title}>"
