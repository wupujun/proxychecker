#coding: utf-8
import sys
import urllib
import requests
import random
import time

import getwordhot

#requests.adapters.DEFAULT_RETRIES = 5


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

def updateHotByID(id,hot):
	filterString=text('id='+str(id))
	recList = session.query(Phrase).filter(filterString)
	recList.update({Phrase.hot: hot}, synchronize_session=False)
	print 'update id=',id,'hot=',hot

def getProxyFromFile(inFIle):
	line = inFile.readline().strip()
	if len(line) == 0: return None

	protocol, proxy = line.split('=')
	proxyDic={'http':proxy}
	return proxyDic

def tryToGetHotWithProxy(rec,proxy):
	hot=0
	try:				
		hot=getwordhot.getNumOfBaiduSearchResult(rec.name,5,proxy)
		if (hot>0) : 
			hasWorkableProxy=True
		else:
			hasWorkableProxy=False

	except Exception, e:
		hasWorkableProxy=False
		print e				
		print 'failed to get result with proxy:',proxy['http']	
	return hot,hasWorkableProxy

if __name__=='__main__':

	#recList=getPhraseByID(1)
	inFile = open('good.txt', 'r')
	recList= getPhraseListWithZeroHot()
	

	i=0
	noWorkableProxy=False
	
	hot=0
	proxy=None
	hasWorkableProxy=False
	hasMoreProxy=True

	for rec in recList :
		# find a available proxy...
		if hasWorkableProxy==False:
			while not hasWorkableProxy and hasMoreProxy :
				proxy=getProxyFromFile(inFile)	
				if proxy == None: 
					print "Can't get a proxy, exit!!!!"
					hasMoreProxy=False
					break
				else:
					print 'change proxy as:',proxy['http']

				hot,hasWorkableProxy=tryToGetHotWithProxy(rec,proxy)
		else:
			hot,hasWorkableProxy=tryToGetHotWithProxy(rec,proxy)

		

		if hasWorkableProxy==False and not hasMoreProxy:
			print 'no more proxy avaible, change as local mode'
			hot=getwordhot.getNumOfBaiduSearchResult(rec.name,2,None)

		if (hot<1):
			print 'all were banned, stop!!!!!'
			break

		i=i+1
		print rec.name.encode('utf8')
		print hot
		updateHotByID(rec.id,hot)

		if (i%10==0):
			print 'i=',i,'make a DB commit'
			session.commit()



	session.commit()		