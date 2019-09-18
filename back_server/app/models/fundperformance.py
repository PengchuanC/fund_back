from back_server import db


class FundPerformance(db.Model):
    __tablename__ = 'fs_fund_performance'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    windcode = db.Column(db.String(10), nullable=False, index=True)
    indicator = db.Column(db.String(20), nullable=False)
    numeric = db.Column(db.Float)
    update_date = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<FundPerformance {self.windcode}>"
