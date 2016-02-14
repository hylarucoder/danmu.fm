from datetime import datetime
from sqlalchemy import Table , Column, Integer, String, ForeignKey, TEXT, DATE, Numeric, create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

Base = declarative_base()

class DanmuMsg(object):
    """仅仅用来存储能够获取到(并不是所有)的弹幕消息"""
    __tablename__ = "danmu_msgs"
    msg_type = Column(String(10))
    uid      = Column(String(20))
    level    = Column(String(100))
    content  = Column(Integer())
    rid      = Column(String(20))
    uid      = Column(String(20))
# chatmsg
# type@=chatmsg/rid@=301712/gid@=-9999/uid@=123456/nn@=test/txt@=666/level@=1/

