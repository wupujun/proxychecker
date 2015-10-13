#coding=utf-8
import requests
import BeautifulSoup
import re
import random

def decodeAnyWord(w):
    try:
        w.decode('utf-8')
    except:
        w = w.decode('gb2312')
    else:
        w = w.decode('utf-8')
    return w

def createURL(checkWord):   #create baidu URL with search words
    checkWord = checkWord.strip()
    checkWord = checkWord.replace(' ', '+').replace('\n', '')
    baiduURL = 'http://www.baidu.com/s?wd=%s&rn=100' % checkWord
    return baiduURL

def getContent(baiduURL):   #get the content of the serp
    uaList = ['Mozilla/4.0+(compatible;+MSIE+6.0;+Windows+NT+5.1;+SV1;+.NET+CLR+1.1.4322;+TencentTraveler)',
    'Mozilla/4.0+(compatible;+MSIE+6.0;+Windows+NT+5.1;+SV1;+.NET+CLR+2.0.50727;+.NET+CLR+3.0.4506.2152;+.NET+CLR+3.5.30729)',
    'Mozilla/5.0+(Windows+NT+5.1)+AppleWebKit/537.1+(KHTML,+like+Gecko)+Chrome/21.0.1180.89+Safari/537.1',
    'Mozilla/4.0+(compatible;+MSIE+6.0;+Windows+NT+5.1;+SV1)',
    'Mozilla/5.0+(Windows+NT+6.1;+rv:11.0)+Gecko/20100101+Firefox/11.0',
    'Mozilla/4.0+(compatible;+MSIE+8.0;+Windows+NT+5.1;+Trident/4.0;+SV1)',
    'Mozilla/4.0+(compatible;+MSIE+8.0;+Windows+NT+5.1;+Trident/4.0;+GTB7.1;+.NET+CLR+2.0.50727)',
    'Mozilla/4.0+(compatible;+MSIE+8.0;+Windows+NT+5.1;+Trident/4.0;+KB974489)']
    headers = {'User-Agent': random.choice(uaList)}

    r = requests.get(baiduURL, headers = headers)
    return r.content

def getLastURL(rawurl): #get final URL while there're redirects
    r = requests.get(rawurl)
    return r.url

def getAtext(atext):    #get the text with <a> and </a>
    pat = re.compile(r'<a .*?>(.*?)</a>')
    match = pat.findall(atext.replace('\n', ''))
    pureText = match[0].replace('<em>', '').replace('</em>', '')
    return pureText.replace('\n', '')

def getCacheDate(t):    #get the date of cache
    pat = re.compile(r'<span class="g">.*?(\d{4}-\d{1,2}-\d{1,2}) </span>')
    match = pat.findall(t)
    cacheDate = match[0]
    return cacheDate

def getRank(checkWord, domain): #main line
    checkWord = checkWord.replace('\n', '')
    checkWord = decodeAnyWord(checkWord)
    baiduURL = createURL(checkWord)
    cont = getContent(baiduURL)
    soup = BeautifulSoup.BeautifulSoup(cont)
    results = soup.findAll('table', {'class': 'result'})    #find all results in this page

    for result in results:
        checkData = unicode(result.find('span', {'class': 'g'}))
        if re.compile(r'^[^/]*%s.*?' %domain).match(checkData.replace('<b>', '').replace('</b>', '')): #改正则
            nowRank = result['id']  #get the rank if match the domain info

            resLink = result.find('h3').a
            resURL = resLink['href']
            domainURL = getLastURL(resURL)  #get the target URL
            resTitle = getAtext(unicode(resLink))   #get the title of the target page

            rescache = result.find('span', {'class': 'g'})
            cacheDate = getCacheDate(unicode(rescache)) #get the cache date of the target page

            res = u'%s, 第%s名, %s, %s, %s' % (checkWord, nowRank, resTitle, cacheDate, domainURL)
            return res.encode('gb2312')
            break
    else:
        return '>100'


domain = 'www.baidu.com' #set the domain which you want to search.
print getRank('百度', domain)