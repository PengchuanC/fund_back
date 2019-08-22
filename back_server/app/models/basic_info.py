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
    id = db.Column(db.Integer, primary_key=True)
    windcode = db.Column(db.String(10))
