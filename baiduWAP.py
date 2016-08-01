#!/usr/bin/env python
# coding=utf-8
# code by 92ez.com

from threading import Thread
import requests
import sqlite3
import Queue
import sys
import re

reload(sys)
sys.setdefaultencoding('utf8')

#main function
def bThread(domainList):
    threadl = []
    queue = Queue.Queue()
    for domain in domainList:
        queue.put(domain)
    for x in xrange(0, 50):
        threadl.append(tThread(queue))
    for t in threadl:
        try:
            t.daemon = True
            t.start()
        except:
            pass
    for t in threadl:
        t.join()

#create thread
class tThread(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while not self.queue.empty():
            domain = self.queue.get()
            try:
                getIPbyDomain(domain)
            except Exception,e:
                continue

def getUrls():
	titles = []
	links = []
	try:
		for page in range(0,MAXPAGE):
			thisPageUrl = "https://m.baidu.com/s?word=" + KEYWORDS +'&pn='+str(page*10)
			htmlpage = requests.get(url = thisPageUrl,headers = HEADERS).content
			items = re.findall(r'srcid="www_normal">(.*?)<div class="resitem"',htmlpage)
			for item in items:
				thisTitle = re.findall(r'><div>(.*?)</div>',item)[0].replace('<em>','').replace('</em>','')
				thisUrl = re.findall(r'<span class="site">(.*?)</span>',item)[0]
				titles.append(thisTitle)
				links.append(thisUrl)
				print thisTitle+' -> '+thisUrl
		return titles,links
	except Exception,e:
		print e

def getIPbyDomain(domain):
	try:
		tmpresult = requests.get('http://ip138.com/ips1388.asp?ip='+domain+'&action=2').content
		tempip = re.findall(r'<font color="blue">(.*?)</font>',tmpresult)[0].split('>> ')[1]
		print tempip
		IPS.append(tempip)
	except Exception,e:
		print e

def saveToDB(titleArr,realLinks,ips):
	try:
		cx = sqlite3.connect(sys.path[0]+"/baidu.db")
		cx.text_factory = str
		cu = cx.cursor()
		for item in titleArr:
			thisIndex = titleArr.index(item)
			thisTitle = item
			thisDomain = 'http://'+realLinks[thisIndex]
			thisIP = ips[thisIndex]

			cu.execute("select * from search where domain='%s'" % (thisDomain))
			if not cu.fetchone():
				cu.execute("insert into search (title,domain,ip) values (?,?,?)", (thisTitle,thisDomain,thisIP))
				cx.commit()
				print '[√] Found ' +thisTitle +' => Insert successly!'
			else:
				print '[x] Found ' +thisTitle +' <= Found in database!'
		cu.close()
		cx.close()
	except Exception, e:
		print e

if __name__ == '__main__':

	global KEYWORDS
	global MAXPAGE
	global HEADERS
	global IPS

	KEYWORDS = sys.argv[1];
	MAXPAGE = int(sys.argv[2])
	HEADERS = {"User-Agent":"iphone"}
	IPS = []
	
	print '[*] 当前设置获取前'+ str(MAXPAGE*10) +'个结果'
	print '[*] 提取结果页标题和百度原始链接...'
	titleArr,realLinks = getUrls()
	print '[√] 提取到'+ str(len(titleArr)) +'个标题和原始链接'

	print '[*] 根据域名反查IP...'
	bThread(realLinks)
	saveToDB(titleArr,realLinks,IPS)
