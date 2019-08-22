from back_server import db


class Classify(db.Model):
    """
    create table if not exists `fund_classify`(
    `ID` int not null primary key auto_increment,
    `WINDCODE` char(10) not null,
    `FUND_SETUPDATE` datetime comment "报告期" not null,
    `BRANCH` char(10) not null,
    `CLASSIFY` char(20) not null,
    `UPDATE_DATE` datetime not null
    );
    """
    __tablename__ = 'fund_classify'
    id = db.Column(db.Integer, primary_key=True)
    windcode = db.Column(db.String(10))
    fund_setupdate = db.Column(db.DATETIME)
    branch = db.Column(db.String(10))
    classify = db.Column(db.String(20))
    update_date = db.Column(db.DATETIME)

    def __repr__(self):
        return f"<Classify {self.windcode}>"

    def to_dict(self):
        items = self.__dict__
        json = {}
        for k, v in items.items():
            if k != "_sa_instance_state":
                json[k] = v
        return json

