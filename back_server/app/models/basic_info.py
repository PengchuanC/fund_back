from back_server import db


class BasicInfo(db.Model):
    """
    create table if not exists `bond_basic_info`(
    `ID` int not null primary key auto_increment,
    `WINDCODE` char(10) not null,
    `SEC_NAME` char(50) not null,
    `FUND_FULLNAME` char(100) not null,
    `FUND_BENCHMARK` text,
    `FUND_INVESTSCOPE` text,
    `FUND_STRUCTUREDFUNDORNOT` char(2),
    `FUND_SETUPDATE` datetime,
    `FUND_FIRSTINVESTTYPE` char(25),
    `FUND_INVESTTYPE` char(25),
    `TYPE` char(5) not null,
    `KIND_I` char(20),
    `KIND_II` char(20)
    );
    """
    __tablename__ = "basic_info"
    id = db.Column(db.Integer, primary_key=True)
    windcode = db.Column(db.String(10))
    sec_name = db.Column(db.String(50))
    fund_fullname = db.Column(db.String(100))
    fund_benchmark = db.Column(db.TEXT)
    fund_investscope = db.Column(db.TEXT)
    fund_structuredfundornot = db.Column(db.String(2))
    fund_setupdate = db.Column(db.DATETIME)
    fund_firstinvesttype = db.Column(db.String(25))
    fund_investtype = db.Column(db.String(25))
    type = db.Column(db.String(5))
    kind_i = db.Column(db.String(20))
    kind_ii = db.Column(db.String(20))

    def __repr__(self):
        return f"<BasicInfo {self.sec_name}>"
