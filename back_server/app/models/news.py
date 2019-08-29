import datetime
from back_server import db


class Toutiao(db.Model):
    __tablename__ = 'finance_news'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False, unique=True, index=True)
    abstract = db.Column(db.TEXT)
    url = db.Column(db.TEXT)
    source = db.Column(db.String(20))
    savedate = db.Column(db.DateTime)

    def __repr__(self):
        return f"<Toutiao {self.title}>"

    def to_dict(self):
        items = self.__dict__
        json = {}
        for k, v in items.items():
            if k != "_sa_instance_state":
                if isinstance(v, datetime.datetime):
                    json[k] = v.strftime("%Y-%m-%d %H:%m")
                else:
                    json[k] = v
        return json
