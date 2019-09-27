from back_server import db


class FundManager(db.Model):
    __tablename__ = 'fs_fund_manager'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    windcode = db.Column(db.String(10), nullable=False, index=True)
    fund_fundmanager = db.Column(db.String(20), name="fund_fundmanager")
    fund_predfundmanager = db.Column(db.TEXT, name="fund_predfundmanager")
    fund_corp_fundmanagementcompany = db.Column(db.String(20))
    update_date = db.Column(db.DateTime)

    def __repr__(self):
        return f"<FundManager {self.windcode}>"


class FundManagerExtend(db.Model):
    __tablename__ = 'fs_fund_manager_extend'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    windcode = db.Column(db.String(10), db.ForeignKey("fs_fund_manager.windcode"), nullable=False, index=True)
    fund_manager_totalnetasset = db.Column(db.Float)
    fund_manager_resume = db.Column(db.Text)
    fund_manager_gender = db.Column(db.String(2))
    nav_periodicannualizedreturn = db.Column(db.Float)
    rank = db.Column(db.Integer)
    update_date = db.Column(db.DateTime)

    managers = db.relationship('FundManager', backref="manager_info")

    def __repr__(self):
        return f"<FundManagerExtend {self.windcode}>"
