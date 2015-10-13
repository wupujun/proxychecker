#coding: utf-8
import sys
import urllib
import requests

import getwordhot

from sqlalchemy import Column, String, Integer,create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
#import MySQLdb
from sqlalchemy import text

# 创建对象的基类:
Base = declarative_base()

# 定义User对象:
class Phrase(Base):
    # 表的名字:
    __tablename__ = 'main'

    # 表的结构:
    id = Column(Integer, primary_key=True)
    name = Column(String(40))
    hot= Column(Integer)
    prefix=Column(String(64))

# 初始化数据库连接:
engine = create_engine('mysql+mysqldb://root:admin@localhost:3306/phrases?charset=utf8')
# 创建DBSession类型:
# 创建Session:
DBSession =  sessionmaker(bind=engine)
session=DBSession()


def getPhraseListWithZeroHot ():
	# 创建Query查询，filter是where条件，最后调用one()返回唯一行，如果调用all()则返回所有行:
	#filterString=text('hot=0 and id='+str(id))
	filterString=text('hot=0')
	recList = session.query(Phrase).filter(filterString)
	
	return recList

def getPhraseByID (id):
	# 创建Query查询，filter是where条件，最后调用one()返回唯一行，如果调用all()则返回所有行:
	filterString=text('hot=0 and id='+str(id))

	recList = session.query(Phrase).filter(filterString)
	
	return recList


if __name__=='__main__':

	recList=getPhraseByID(1)
	print recList
	for rec in recList :
		print rec.name.encode('utf8')