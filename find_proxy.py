#encoding=utf8

from bs4 import BeautifulSoup
import urllib2
import requests
import getwordhot

import httplib
import time
import urllib
import threading

def buildProxyList():
    of = open('proxy.txt' , 'w')

    pages=['nn','nt','wn','wt']

    for page in pages:
        #html_doc = urllib2.urlopen('http://www.xici.net.co/nn/' + str(page) ).read()
        url='http://www.xici.net.co/'+page+'/'
        html_doc = urllib2.urlopen(url).read()

        print 'searching proxy from url: ',url

        soup = BeautifulSoup(html_doc,"html.parser")
        trs = soup.find('table', id='ip_list').find_all('tr')
        for tr in trs[1:]:
            tds = tr.find_all('td')
            ip = tds[2].text.strip()
            port = tds[3].text.strip()
            protocol = tds[6].text.strip()
            if protocol == 'HTTP':                 
                of.write('%s=http://%s:%s\n' % (protocol, ip, port) )
                print '%s=http://%s:%s' % (protocol, ip, port)
            elif protocol == 'HTTPS':
                of.write('%s=https://%s:%s\n' % (protocol, ip, port) )
                print '%s=https://%s:%s' % (protocol, ip, port)
    of.close()

def printMT(msg, lock):
    lock.acquire()
    print msg
    lock.release()

def verifyProxy(inFile,proxyList): #,outFile):

    lock = threading.Lock()    
    while True:
        lock.acquire()
        line = inFile.readline().strip()
        lock.release()
        if len(line) == 0: break
        protocol, proxy = line.split('=')    
    
        try:
            '''
            conn = httplib.HTTPConnection(proxy, timeout=3.0)
            conn.request(method='GET', url='http://www.baidu.com/s?wd=iphone')
            res = conn.getresponse()
            ret_headers = str( res.getheaders() )
            '''
            proxyDic={protocol.lower():proxy}

            print proxyDic
            #print 'trying with proxy=',proxy
            printMT('trying with proxy='+proxy,lock)
            num=getwordhot.getNumOfBaiduSearchResult('iphone',timeout=2,proxy=proxyDic)
            #print 'number is ',num
            #printMT('number is '+str(num),lock) 


            if num>0:
                lock.acquire()                
                print line                
                #outFile = open('good_proxy.txt', 'w+')
                #outFile.write('%s\n',proxy) 
                #outFile.close() 
                #print 'finish write fie'
                proxyList.append(line)
                lock.release()
            #print html_doc.encode('gbk')

        except Exception, e:
            lock.acquire()
            print e
            print 'bad proxy:',proxy
            lock.release()


def verifyProxyWithMT():

    inFile = open('proxy.txt', 'r')
    

    proxyList=[]

    all_thread = []
    for i in range(150):
        t = threading.Thread(target=verifyProxy,args = (inFile,proxyList) )#,outFile) )
        all_thread.append(t)
        t.start()
        
    for t in all_thread:
        t.join()

    inFile.close()
    
    outFile = open('good.txt', 'w')
    #outFile.writelines(proxyList)
    for l in proxyList:
        outFile.write("%s\n" %l)
    outFile.close()


if __name__=='__main__':
    buildProxyList()
    verifyProxyWithMT()

