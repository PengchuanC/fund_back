from back_server import db
from sqlalchemy.dialects.mysql import DOUBLE

from .util import ModelToDict


class Indicators(db.Model, ModelToDict):
    """
    CREATE TABLE `indicators` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `windcode` varchar(10) NOT NULL COMMENT '证券代码',
    `indicator` varchar(50) NOT NULL COMMENT '指标',
    `numeric` double DEFAULT NULL COMMENT '数字型指标值',
    `text` text COMMENT '文本型指标值',
    `note` varchar(20) DEFAULT NULL COMMENT '对指标的解释',
    `rpt_date` datetime NOT NULL COMMENT '报告期',
    `update_date` datetime NOT NULL COMMENT '更新日期',
    PRIMARY KEY (`id`),
    UNIQUE KEY `IDX_CODE_IND_NOTE_UPDATE` (`windcode`,`indicator`,`update_date`,`note`)
    ) ENGINE=InnoDB AUTO_INCREMENT=188041 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
    """
    __tablename__ = "indicators"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    windcode = db.Column(db.String(10), nullable=False)
    indicator = db.Column(db.String(50), nullable=False)
    numeric = db.Column(DOUBLE)
    text = db.Column(db.Text)
    note = db.Column(db.String(20))
    rpt_date = db.Column(db.DateTime, nullable=False)
    update_date = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<Indicators {self.windcode}>"
