
from back_server import db
from .util import ModelToDict


class IndicatorsForPlot(db.Model, ModelToDict):
    """
    CREATE TABLE `indicators_for_plot` (
      `ID` int(11) NOT NULL AUTO_INCREMENT,
      `WINDCODE` char(10) NOT NULL,
      `FUND_SETUPDATE` datetime NOT NULL COMMENT '基金成立日期',
      `FUND_MGRCOMP` varchar(100) NOT NULL COMMENT '基金管理人',
      `FUND_CORP_FUNDMANAGEMENTCOMPANY` varchar(25) DEFAULT NULL COMMENT '基金公司简称',
      `FUND_PCHMSTATUS` char(10) DEFAULT NULL COMMENT '基金申购状态',
      `FUND_FUNDSCALE` double DEFAULT NULL COMMENT '基金规模',
      `PRT_NETASSET` double DEFAULT NULL COMMENT '基金净值',
      `FUND_MANAGEMENTFEERATIO` double DEFAULT NULL COMMENT '管理费率%',
      `FUND_PURCHASEFEE` text COMMENT '申购费',
      `FUND_REDEMPTIONFEE` text COMMENT '赎回费',
      `RPT_DATE` datetime NOT NULL COMMENT '报告期',
      `UPDATE_DATE` datetime NOT NULL COMMENT '更新日期',
      PRIMARY KEY (`ID`),
      KEY `idx_code_date` (`WINDCODE`,`UPDATE_DATE`)
    ) ENGINE=InnoDB AUTO_INCREMENT=10339 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
    """
    __tablename__ = 'indicators_for_plot'
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    WINDCODE = db.Column(db.String(10), nullable=False)
    FUND_SETUPDATE = db.Column(db.DateTime, nullable=False)
    FUND_MGRCOMP = db.Column(db.String(100), nullable=False)
    FUND_CORP_FUNDMANAGEMENTCOMPANY = db.Column(db.String(25))
    FUND_PCHMSTATUS = db.Column(db.String(10))
    FUND_FUNDSCALE = db.Column(db.Float)
    PRT_NETASSET = db.Column(db.Float)
    FUND_MANAGEMENTFEERATIO = db.Column(db.Float)
    FUND_PURCHASEFEE = db.Column(db.TEXT)
    FUND_REDEMPTIONFEE = db.Column(db.TEXT)
    RPT_DATE = db.Column(db.DateTime)
    UPDATE_DATE = db.Column(db.DateTime)

    def __repr__(self):
        return f"<IndicatorsForPlot {self.WINDCODE}>"
