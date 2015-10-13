#coding: utf-8
import sys
import urllib
import requests
import random
import time

import getwordhot
import threading

import time
import Queue

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
	#print 'update id=',id,'hot=',hot

def getProxyFromFile(inFIle):
	line = inFile.readline().strip()
	if len(line) == 0: return None

	protocol, proxy = line.split('=')
	proxyDic={'http':proxy}
	return proxyDic

def tryToGetHotWithProxy(rec,proxy):
	hot=0
	try:				
		hot=getwordhot.getNumOfBaiduSearchResult(rec,5,proxy)
		if (hot>0) : 
			hasWorkableProxy=True
		else:
			hasWorkableProxy=False

	except Exception, e:
		hasWorkableProxy=False
		print e				
		print 'failed to get result with proxy:',proxy['http']	
	return hot,hasWorkableProxy




class Consumer(threading.Thread):  
    def __init__(self, t_name, queue,inFile):  
        threading.Thread.__init__(self, name=t_name)  
        self.queue = queue
        self.proxy=None  
  
    def run(self):
    	lock = threading.Lock()    
    	i=0;
        while True:  
            #从队列中取值  
            try:
            	rec= self.queue.get(block=False)
            	recID=rec[0]
            	keyword=rec[1]

            	bUpdate=False
            	hasMoreProxy=True

            	while not bUpdate and hasMoreProxy:
					if (self.proxy==None):
						lock.acquire()
						line = inFile.readline().strip()
						print 'set proxy as:',line
						lock.release()

						if len(line) == 0: 
							hasMoreProxy=False
							break
						protocol, proxy = line.split('=') 
						proxyDic={protocol.lower():proxy}
						self.proxy=proxyDic

					hot,hasWorkableProxy=tryToGetHotWithProxy(keyword,self.proxy)
					if hot>0 :
						lock.acquire()
						i=i+1
						print 'update DB, id=%d,hot=%d' %(recID,hot)						
						updateHotByID(recID,hot)
						bUpdate=True
						session.commit()
						lock.release()
					else:
						self.proxy=None


            except Exception, e:
            	print e
            	break;
            #if (i%50==0):            	
        	#	session.commit()    		
        session.commit()
        print "%s: %s finished!" % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), self.getName())  
      


if __name__=='__main__':

	queue = Queue.Queue()
	#recList=getPhraseByID(1)
	inFile = open('good.txt', 'r')
	recList= getPhraseListWithZeroHot()

	tList=[]

	for rec in recList :
		queue.put( (rec.id,rec.name) )

	for i in range(1):
		t=Consumer('thread'+str(i),queue,inFile)
		tList.append(t)
		t.start()

	for t in tList:
		t.join()


	session.commit()		
	