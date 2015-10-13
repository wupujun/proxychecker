#coding: utf-8
import sys
import urllib
import requests
from BeautifulSoup import BeautifulSoup
import sys

from requests.adapters import HTTPAdapter
session = requests.Session()
session.mount('http://', HTTPAdapter(max_retries=6))


def getNumOfBaiduSearchResult(keyword,timeout,proxy):
	num=0

	url = "http://www.baidu.com/s?wd=" + urllib.quote(keyword.encode('utf8'))	

	if proxy is not None:		
		response=requests.get(url,timeout=timeout,proxies=proxy)
	#htmlpage = urllib2.urlopen(url).read()
	else:
		print('request without proxy...')
		response=requests.get(url,timeout)

	if response.status_code != 200:
		return -1
	htmlpage=response.text
	soup = BeautifulSoup(htmlpage)
	results= soup.findAll("div", {"class": "nums"})
	
	if len(results)>0:
		result= results[0]
			
		temp=results[0].contents[1]
		#print temp
		
		numStr= temp[11:].replace(',','').replace(u'个','')
		num=int(numStr)
		
	return num

if __name__=='__main__':
	words = [u"春风得意",u"春风化雨",u"春风和气"]

	for word in words:
		no=getNumOfBaiduSearchResult(word,5,None)
		print word.encode('gb18030'),':',no